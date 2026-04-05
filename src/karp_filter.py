#!/usr/bin/env python3
"""
Fetch all records from the KARP/stunda database and output those
matching a condition as JSON (including the entry ID).

For records missing pos, the Swedish and English POS taggers are called
(same method as the processing pipeline). If they agree on a single tag,
the pos is added to the output record.

Options:
  -c   Commit changes: write the agreed pos back to the KARP database.

Edit CONDITION at the bottom of this file to change the filter.
"""

import argparse
import json
import sys
import os
import requests
from dotenv import load_dotenv

# Allow importing utils.py from the same directory
sys.path.insert(0, os.path.dirname(__file__))
from utils import swedish_pos_tagging, english_pos_single_word, update_posts_via_api_key

KARP_URL = "https://spraakbanken4.it.gu.se/karp/v7/query/stunda"
PAGE_SIZE = 500

SWEDISH_MAPPING = {"nn": "N", "vb": "V", "jj": "A", "ab": "Ab", "pc": "P"}
ENGLISH_MAPPING = {"NOUN": "N", "VERB": "V", "ADJ": "A", "ADV": "Ab", "PRT": "P"}


def fetch_all_entries():
    """Fetch every entry from KARP using pagination. Returns list of hits."""
    hits = []
    start = 0

    while True:
        response = requests.get(KARP_URL, params={"size": PAGE_SIZE, "from": start})
        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}", file=sys.stderr)
            sys.exit(1)

        data = response.json()
        hits.extend(data["hits"])
        total = data["total"]

        print(f"Fetched {len(hits)}/{total} entries...", file=sys.stderr, end="\r")

        if len(hits) >= total:
            break
        start += PAGE_SIZE

    print(f"Fetched {len(hits)}/{total} entries.   ", file=sys.stderr)
    return hits


def filter_entries(hits, condition):
    """Return list of {id, version, entry} dicts where condition(entry) is True."""
    results = []
    for hit in hits:
        entry = hit["entry"]
        if condition(entry):
            results.append({"id": hit["id"], "version": hit["version"], "entry": entry})
    return results


def get_pos_result(entry):
    """
    Call the Swedish and English POS taggers (same as the pipeline).

    For multi-word terms both taggers agree on "NP" (noun phrase).

    For single-word terms, returns a tuple (agreed, conflict) where:
      agreed   -- the agreed POS tag (str) if both taggers produce exactly the
                  same single valid tag, otherwise None
      conflict -- "X/Y" string if both taggers each produce exactly one valid
                  tag but they differ, otherwise None
    """
    swe_lemma = entry.get("swe", {}).get("lemma", "")
    eng_lemma = entry.get("eng", {}).get("lemma", "")
    if not swe_lemma or not eng_lemma:
        return None, None

    # Multi-word: pipeline assigns "N", but we use "NP" (noun phrase)
    if len(swe_lemma.split()) > 1 or len(eng_lemma.split()) > 1:
        return "NP", None

    try:
        result = swedish_pos_tagging(swe_lemma)
        if not result:
            return None, None
        swe_tags = {SWEDISH_MAPPING[t.split(".")[0]]
                    for t in result[0]["tags"]
                    if t.split(".")[0] in SWEDISH_MAPPING}

        eng_tags = {ENGLISH_MAPPING[tag]
                    for tag, _ in english_pos_single_word(eng_lemma)
                    if tag in ENGLISH_MAPPING}

        agreed = swe_tags & eng_tags
        if len(agreed) == 1:
            return agreed.pop(), None
        if len(swe_tags) == 1 and len(eng_tags) == 1 and not agreed:
            return None, f"{swe_tags.pop()}/{eng_tags.pop()}"
        return None, None
    except Exception:
        return None, None


def augment_with_pos(results):
    """
    For each result, attempt POS tagging.
    Adds 'pos' when both taggers agree, or 'conflictingpos' (X/Y) when both
    produce exactly one valid tag but they differ.
    Returns (results, agreed_count, conflict_count).
    """
    agreed_count = 0
    conflict_count = 0
    total = len(results)
    for i, record in enumerate(results, 1):
        print(f"Tagging {i}/{total}...", file=sys.stderr, end="\r")
        agreed, conflict = get_pos_result(record["entry"])
        if agreed is not None:
            record["entry"]["pos"] = agreed
            agreed_count += 1
        elif conflict is not None:
            record["entry"]["conflictingpos"] = conflict
            conflict_count += 1
    print(f"Tagging done.          ", file=sys.stderr)
    return results, agreed_count, conflict_count


def commit_to_karp(results, api_key):
    """
    For each result that has a 'pos' field added (i.e. not 'conflictingpos'),
    update the entry in the KARP database.
    Returns (committed_count, failed_count).
    """
    to_commit = [r for r in results if "pos" in r["entry"] and "conflictingpos" not in r["entry"]]
    committed = 0
    failed = 0
    total = len(to_commit)
    for i, record in enumerate(to_commit, 1):
        print(f"Committing {i}/{total}...", file=sys.stderr, end="\r")
        result = update_posts_via_api_key(
            record["id"], record["entry"], record["version"], api_key
        )
        if result is not None:
            committed += 1
        else:
            failed += 1
            print(f"\nFailed to update {record['id']}", file=sys.stderr)
    print(f"Committing done.       ", file=sys.stderr)
    return committed, failed


# ---------------------------------------------------------------------------
# CONDITION: edit this function to change the filter.
# It receives one entry dict and should return True to include the record.
# ---------------------------------------------------------------------------
def condition(entry):
    """Records where pos is missing or empty."""
    return not entry.get("pos")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-c", "--commit", action="store_true",
                        help="Commit agreed pos values back to the KARP database")
    args = parser.parse_args()

    api_key = None
    if args.commit:
        load_dotenv()
        load_dotenv(dotenv_path="/var/lib/stunda/data/.env")
        api_key = os.getenv("KARP_API_KEY")
        if not api_key:
            print("Error: KARP_API_KEY not set in environment or .env file", file=sys.stderr)
            sys.exit(1)

    hits = fetch_all_entries()
    results = filter_entries(hits, condition)
    total_found = len(results)
    print(f"Found {total_found} matching entries. Running POS tagger...", file=sys.stderr)

    results, agreed_count, conflict_count = augment_with_pos(results)

    if args.commit:
        committed, failed = commit_to_karp(results, api_key)

    # Output only id and entry (not the internal version field)
    output = [{"id": r["id"], "entry": r["entry"]} for r in results]
    print(json.dumps(output, ensure_ascii=False, indent=2))

    print(f"Total records matching condition : {total_found}", file=sys.stderr)
    print(f"Records augmented with pos       : {agreed_count}", file=sys.stderr)
    print(f"Records with conflicting pos     : {conflict_count}", file=sys.stderr)
    if args.commit:
        print(f"Records committed to KARP        : {committed}", file=sys.stderr)
        if failed:
            print(f"Records failed to commit         : {failed}", file=sys.stderr)
