# Standard library imports
import os
import sys
import argparse
import json
import re
import time
from collections import defaultdict
from datetime import datetime

# Define path to third-party libraries

# Third-party imports
import pandas as pd
from dotenv import load_dotenv

# Local application imports
from utils import *

# Dictionary containing banned words for content filtering
banned_words = {
    # English banned words
    "en": [
        "abortion",
        "anal",
        "anus",
        "arse",
        "ass",
        "ass-fucker",
        "asses",
        "asshole",
        "assholes",
        "ballbag",
        "balls",
        "bastard",
        "bellend",
        "bestial",
        "bestiality",
        "bitch",
        "bitches",
        "bitching",
        "bloody",
        "blowjob",
        "bollok",
        "boob",
        "boobs",
        "breasts",
        "buceta",
        "bum",
        "butt",
        "carpet muncher",
        "chink",
        "cipa",
        "clitoris",
        "cock",
        "cock-sucker",
        "cocks",
        "coon",
        "crap",
        "cum",
        "cumshot",
        "cunillingus",
        "cunt",
        "damn",
        "dick",
        "dildo",
        "dildos",
        "dink",
        "dog-fucker",
        "duche",
        "dyke",
        "ejaculate",
        "ejaculated",
        "ejaculates",
        "ejaculating",
        "ejaculation",
        "fag",
        "fagging",
        "faggot",
        "fagot",
        "fagots",
        "fanny",
        "felching",
        "fellatio",
        "flange",
        "fuck",
        "fucked",
        "fucker",
        "fuckers",
        "fucking",
        "fuckings",
        "fucks",
        "fudge packer",
        "god-damned",
        "goddamn",
        "hell",
        "hore",
        "horny",
        "jerk-off",
        "kock",
        "labia",
        "lust",
        "lusting",
        "masochist",
        "masturbate",
        "mother fucker",
        "nazi",
        "nigger",
        "niggers",
        "orgasim",
        "orgasm",
        "orgasms",
        "pecker",
        "penis",
        "piss",
        "pissed",
        "pisser",
        "pisses",
        "pissing",
        "pissoff",
        "poop",
        "porn",
        "porno",
        "pornography",
        "prick",
        "pricks",
        "pube",
        "pussies",
        "pussy",
        "rape",
        "rapist",
        "rectum",
        "retard",
        "rimming",
        "sadist",
        "screwing",
        "scrotum",
        "semen",
        "sex",
        "shag",
        "shagging",
        "shemale",
        "shit",
        "shite",
        "shits",
        "shitted",
        "shitting",
        "shitty",
        "skank",
        "slut",
        "sluts",
        "smegma",
        "smut",
        "snatch",
        "son-of-a-bitch",
        "spac",
        "spunk",
        "testicle",
        "tit",
        "tits",
        "titt",
        "turd",
        "vagina",
        "viagra",
        "vulva",
        "wang",
        "wank",
        "whore",
        "x rated",
        "xxx",
    ],
    # Swedish banned words
    "sv": [
        "abort",
        "anal",
        "anus",
        "röv",
        "ass-fucker",
        "åsnor",
        "idiot",
        "arslen",
        "bollväska",
        "bollar",
        "bastard",
        "bellend",
        "bestialisk",
        "tidelag",
        "tik",
        "tikar",
        "bitching",
        "blodig",
        "avsugning",
        "bollok",
        "boob",
        "tuttar",
        "bröst",
        "buceta",
        "luffare",
        "stånga",
        "mattan mattan",
        "spricka",
        "cipa",
        "klitoris",
        "kuk",
        "cock-suga",
        "tuppar",
        "coon",
        "skit",
        "sperma",
        "cumshot",
        "cunillingus",
        "fitta",
        "attans",
        "dildo",
        "dildos",
        "dink",
        "hund-fucker",
        "duche",
        "fördämning",
        "ejakulat",
        "ejakulerade",
        "utlösning",
        "ejakulation",
        "bög",
        "fagging",
        "faggots",
        "rumpa",
        "felching",
        "fellatio",
        "fläns",
        "knulla",
        "körd",
        "fucker",
        "fuckers",
        "jävla",
        "fuckings",
        "fucks",
        "fudge packer",
        "god-damned",
        "helvete",
        "hore",
        "kåt",
        "jerk-off",
        "kock",
        "blygdläppar",
        "lusta",
        "lusting",
        "masochist",
        "onanera",
        "mamma fucker",
        "nazist",
        "nigger",
        "niggers",
        "orgasim",
        "orgasm",
        "orgasmer",
        "pecker",
        "penis",
        "piss",
        "förbannad",
        "pisser",
        "pisses",
        "pissing",
        "dra åt helvete",
        "bajs",
        "porr",
        "pornografi",
        "pube",
        "mesar",
        "våldta",
        "våldtäktsman",
        "ändtarm",
        "hämma",
        "rimming",
        "sadist",
        "skruvning",
        "scrotum",
        "sädesvätska",
        "sex",
        "shag",
        "shagging",
        "shemale",
        "shite",
        "shits",
        "shitted",
        "shitting",
        "shitty",
        "skank",
        "slampa",
        "sluts",
        "smegma",
        "smut",
        "ryck",
        "son-of-a-tik",
        "spac",
        "testikel",
        "mes",
        "titt",
        "vagina",
        "viagra",
        "vulva",
        "wang",
        "wank",
        "hora",
        "x betygsatt",
        "xxx",
    ],
}


def clean_and_simple_checks(df, keepcase=False):
    """
    Clean and perform simple checks on the DataFrame lemma data to ensure data quality.

    Args:
    - df (DataFrame): DataFrame containing lemma data with columns 'eng_lemma' and 'swe_lemma'.

    Returns:
    - DataFrame: Filtered DataFrame containing entries ready for the next processing step.

    """

    # Remove excess whitespace and (unless keepcase) convert to lower case (preserve all-caps lemmas)
    df["eng_lemma"] = df["eng_lemma"].str.replace(r"\s+", " ", regex=True)
    if not keepcase:
        df["eng_lemma"] = df["eng_lemma"].apply(lambda x: x if x.upper() == x else x.lower())
    df["swe_lemma"] = df["swe_lemma"].str.replace(r"\s+", " ", regex=True)
    if not keepcase:
        df["swe_lemma"] = df["swe_lemma"].apply(lambda x: x if x.upper() == x else x.lower())

    # remove [*] and [**] from entries
    df["eng_lemma"] = (
        df["eng_lemma"].str.replace(r"\[\*\*?\]", "", regex=True).str.strip()
    )
    df["swe_lemma"] = (
        df["swe_lemma"].str.replace(r"\[\*\*?\]", "", regex=True).str.strip()
    )

    # copy paranthesis from entry
    df["eng_paranthesis"] = df["eng_lemma"].str.extract(r"(\([^\(]+\))")
    df["swe_paranthesis"] = df["swe_lemma"].str.extract(r"(\([^\(]+\))")

    # remove paranthesis from entry
    df["eng_lemma"] = (
        df["eng_lemma"].str.replace(r"\([^\(]+\)", "", regex=True).str.strip()
    )
    df["swe_lemma"] = (
        df["swe_lemma"].str.replace(r"\([^\(]+\)", "", regex=True).str.strip()
    )

    # define condition for checking if a swedish and english lemma exist
    lemma_exist_cond = (df["eng_lemma"] == "") | (df["swe_lemma"] == "")

    # condition to ensure only accpeted characters are present in the lemma
    character_condition = (df["eng_lemma"].str.match(r"^[a-zA-Z\-\d ]+$")) & (
        df["swe_lemma"].str.match(r"^[a-zA-ZåäöÅÄÖ\- \d]+$")
    )

    # mark the entries ready for the next stage
    df.loc[character_condition & ~lemma_exist_cond, "status"] = "shallow processed"

    # mark entries with data quality issues
    df.loc[~character_condition & ~lemma_exist_cond, "status"] = (
        "invalid characters in lemma"
    )

    # Mark entries with no english or swedish lemma as lacking translation
    df.loc[lemma_exist_cond, "status"] = "no translation"

    return df


def spell_check(df):
    """
    Perform spell check on English and Swedish lemmas using dictionary lookups.

    Args:
    - df (DataFrame): DataFrame containing lemma data with columns 'eng_lemma' and 'swe_lemma'.

    Returns:
    - DataFrame: Filtered DataFrame containing entries with correct spelling.

    """
    if len(df) == 0:
        return df

    # Perform english spell check
    english_spell_condition = df["eng_lemma"].apply(is_word_in_english)

    # Perform swedish spell check
    swedish_spell_condition = df["swe_lemma"].apply(swedish_spell_check)

    # mark entries
    df.loc[english_spell_condition & swedish_spell_condition, "status"] = "spelling ok"

    df.loc[english_spell_condition & ~swedish_spell_condition, "status"] = (
        "swedish misspelt"
    )

    df.loc[~english_spell_condition & swedish_spell_condition, "status"] = (
        "english misspelt"
    )

    df.loc[~english_spell_condition & ~swedish_spell_condition, "status"] = (
        "both misspelt"
    )

    # Preserve the spell check outcome in its own column so it survives
    # later pipeline steps even when they are not used to stop the row.
    df["spell_status"] = df["status"]

    return df


def pos(df):
    """
    Part-of-speech tagging for entries in the DataFrame.

    Args:
        df (DataFrame): DataFrame containing lemma data.

    Returns:
        DataFrame: DataFrame after POS tagging.
    """

    if len(df) == 0:
        return df

    # Find agreed pos
    df["agreed_pos"] = df.apply(
        lambda x: pos_agreement_term_based(x["swe_lemma"], x["eng_lemma"]), axis=1
    )

    # Upgrade "N" to "NP" (noun phrase) when either lemma contains a space
    multi_word = df["swe_lemma"].str.contains(" ") | df["eng_lemma"].str.contains(" ")
    df.loc[(df["agreed_pos"] == "N") & multi_word, "agreed_pos"] = "NP"

    # If no pos is found set status accordingly
    df.loc[~df["agreed_pos"].isin(["N", "NP", "V", "A", "Ab", "P"]), "status"] = df.loc[
        ~df["agreed_pos"].isin(["N", "NP", "V", "A", "Ab", "P"]), "agreed_pos"
    ]

    # If pos found set status accordingly
    df.loc[df["agreed_pos"].isin(["N", "NP", "V", "A", "Ab", "P"]), "status"] = "found pos"

    # Preserve the POS outcome in its own column so it survives later
    # pipeline steps even when they are not used to stop the row.
    df["pos_status"] = df["status"]

    return df


def lemmatize(df, keepcase=False):
    """
    Perform Swedish POS tagging and lemmatization on a DataFrame.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing columns "swe_lemma" and "simple_swedish_pos".
    - keepcase (bool): if True, don't lemmatize lemmas that contain any
      uppercase character. The Skrutten/WordNet lemmatizer APIs normalize
      their output to lowercase regardless of input casing, so a mixed-case
      term such as "LSTM-modell" would otherwise come back as "lstm-modell"
      even though the caller asked to preserve the original case.

    Returns:
    - pandas.DataFrame: Filtered DataFrame with successfully lemmatized entries.
    """

    if len(df) == 0:
        return df

    # get pos of english lemmas
    df["english_pos"] = df["eng_lemma"].apply(english_pos)

    # get pos of swedish lemmas
    df["swedish_pos"] = df["swe_lemma"].apply(granska_pos)

    # reduce information for easier checks
    df["simple_swedish_pos"] = df["swedish_pos"].apply(convert_to_simple_pos)

    # condition to check for suspected sarskrivning
    sarskrivning_condition = df["simple_swedish_pos"].str.contains(
        r"NNS? NNS?", regex=True
    )

    df.loc[sarskrivning_condition, "status"] = "suspected särskriving"

    # agreed_pos is only a real POS tag when pos() found a single agreed tag;
    # on disagreement it instead holds an error string (e.g. "no pos found").
    # Lemmatizers and inflection generators key off this value, so an invalid
    # tag here must skip lemmatization for that row rather than being passed
    # through (english_lemmatizer would otherwise raise a KeyError).
    valid_pos = {"N", "NP", "V", "A", "Ab", "P"}

    # lemmatize swedish lemma (preserve all-caps lemmas, and any casing at
    # all when keepcase is set, since the lemmatizer APIs always return
    # lowercase output)
    df["swe_lemma"], df["swe_lemmatizer_status"] = zip(
        *df.apply(
            lambda x: (x["swe_lemma"], "ok")
            if x["swe_lemma"].upper() == x["swe_lemma"]
            or x["agreed_pos"] not in valid_pos
            or (keepcase and x["swe_lemma"] != x["swe_lemma"].lower())
            else advanced_swedish_lemmatizer(
                x["swe_lemma"], x["simple_swedish_pos"], x["swedish_pos"]
            ),
            axis=1,
        )
    )

    df["eng_lemma"] = df.apply(
        lambda x: x["eng_lemma"]
        if x["eng_lemma"].upper() == x["eng_lemma"]
        or x["agreed_pos"] not in valid_pos
        or (keepcase and x["eng_lemma"] != x["eng_lemma"].lower())
        else english_lemmatizer(x["eng_lemma"], "N" if x["agreed_pos"] == "NP" else x["agreed_pos"], x["english_pos"]),
        axis=1,
    )

    df.loc[
        ~sarskrivning_condition & (df["swe_lemmatizer_status"] == "ok"), "status"
    ] = "automatically verified"
    df.loc[
        ~sarskrivning_condition & (df["swe_lemmatizer_status"] != "ok"), "status"
    ] = df.loc[
        ~sarskrivning_condition & (df["swe_lemmatizer_status"] != "ok"),
        "swe_lemmatizer_status",
    ]

    return df


def generate_inflections(df):
    """
    Generates inflections for Swedish and English lemmas in the DataFrame.

    This function applies Swedish and English inflection rules to each lemma
    based on its part of speech (POS). The function expects the DataFrame to
    have 'swe_lemma', 'eng_lemma', and 'agreed_pos' columns.

    Args:
        df (DataFrame): The DataFrame containing lemma and POS data.

    Returns:
        DataFrame: The DataFrame with added columns for Swedish and English
                   inflections.
    """
    # Return the DataFrame immediately if it is empty
    if len(df) == 0:
        return df

    # Apply Swedish inflection rules across the DataFrame
    df["swedish_inflections"] = df.apply(
        lambda x: swe_inflections(x.swe_lemma, x.agreed_pos), axis=1
    )

    # Apply English inflection rules across the DataFrame
    df["english_inflections"] = df.apply(
        lambda x: eng_inflections(x.eng_lemma, x.agreed_pos), axis=1
    )

    return df


def check_for_banned_words(df):
    """
    Checks if the entries in the DataFrame contain banned words in English or Swedish lemmas.

    This function applies a check across multiple columns ('eng_lemma', 'swe_lemma', and 'src')
    to determine if any entries contain words that are on a predefined list of banned words.
    The function updates the 'contains_banned' column in the DataFrame to reflect whether any
    banned words are present.

    Args:
        df (DataFrame): The DataFrame containing the data to check against banned words lists.

    Returns:
        DataFrame: The DataFrame with the 'contains_banned' column updated.
    """

    def contains_banned_word(text, banned_words):
        """
        Determines if any word in a given text is a banned word.

        Args:
            text (str): The text to be checked.
            banned_words (list): List of words that are considered banned.

        Returns:
            bool: True if any word in the text is banned, otherwise False.
        """
        words = text.split()
        for word in words:
            if word in banned_words:
                return True
        return False

    # Check for banned English words in 'eng_lemma' column
    df["contains_banned"] = df["eng_lemma"].apply(
        lambda x: contains_banned_word(x, banned_words["en"])
    )

    # Check for banned Swedish words in 'swe_lemma' column if not already banned
    df.loc[~df["contains_banned"], "contains_banned"] = df["swe_lemma"].apply(
        lambda x: contains_banned_word(x, banned_words["sv"])
    )

    # Check for banned words in 'src' column if not already banned, combining both languages
    df.loc[~df["contains_banned"], "contains_banned"] = df["src"].apply(
        lambda x: contains_banned_word(x, banned_words["en"] + banned_words["sv"])
    )

    return df


def term_already_exists(existing_terms, new_term):
    """
    Checks if a term already exists in the provided list of existing terms and updates the source if necessary.

    The function constructs a tuple from the new term's English and Swedish lemmas and its source.
    It then checks this tuple against existing terms. If the term exists and the source is not already listed,
    it updates the source. This function also interacts with the KARP API to update the terms in the KARP database.

    Args:
        existing_terms (list of dicts): A list of dictionaries, each representing a term with its details.
        new_term (dict): A dictionary representing the new term to be checked.

    Returns:
        bool: True if the term already exists, False otherwise.
    """

    # Construct a tuple from the new term's relevant details
    term = (new_term["eng_lemma"], new_term["swe_lemma"], new_term["src"])

    # Iterate through existing terms to see if there's a match
    for existing_term in existing_terms:
        compare_term = (
            existing_term["entry"]["eng"]["lemma"],
            existing_term["entry"]["swe"]["lemma"],
        )

        # Check if the English and Swedish lemmas match
        if term[:2] == compare_term:
            entry = existing_term["entry"]
            needs_update = False

            # Update the source if it's not already listed
            sources = entry["src"].split(", ")
            if term[2] not in sources:
                entry["src"] += ", " + new_term["src"]
                needs_update = True

            # Merge in any Swedish synonyms from this row that aren't
            # already on the KARP entry, instead of silently dropping them
            # just because the primary eng/swe lemma pair already exists.
            existing_synonyms = entry.get("synonyms") or []
            new_synonyms = new_term.get("synonyms")
            if not isinstance(new_synonyms, list):
                new_synonyms = []
            merged_synonyms = existing_synonyms + [
                s for s in new_synonyms if s not in existing_synonyms
            ]
            if merged_synonyms != existing_synonyms:
                entry["synonyms"] = merged_synonyms
                needs_update = True

            if needs_update:
                # Retrieve API key from environment and update the entry via API
                key = os.getenv("KARP_API_KEY")
                update_posts_via_api_key(
                    existing_term["id"],
                    entry,
                    existing_term["version"],
                    key,
                    verbose=True,
                )
            return True

    return False


def process_synonyms(synonyms, continue_on_issues=False):
    """
    Clean and lemmatize each synonym. Drops synonyms that fail the
    character check. Synonyms that fail the Swedish spell check are
    dropped by default, same as before; when continue_on_issues is set
    they're kept in cleaned form but not lemmatized instead, since
    Skrutten's dictionary doesn't cover all valid domain terminology
    (e.g. "ambiguitet") and silently dropping such synonyms loses real
    data. Only opt-in via continue_on_issues since it can also let a
    genuine misspelling through uncorrected.
    POS is derived independently per synonym; lemmatization failure falls back to the cleaned word.
    Returns list of processed synonym strings.
    """
    processed = []
    for syn in synonyms:
        syn = re.sub(r'\s+', ' ', syn).lower().strip()
        # Strip bracketed annotations such as [även]
        syn = re.sub(r'\[[^\]]*\]\s*', '', syn).strip()
        if not re.match(r'^[a-zA-ZåäöÅÄÖ\- \d]+$', syn):
            continue
        if not swedish_spell_check(syn):
            if continue_on_issues:
                processed.append(syn)
            continue
        swe_pos = granska_pos(syn)
        simple_pos = convert_to_simple_pos(swe_pos)
        lemmatized, status = advanced_swedish_lemmatizer(syn, simple_pos, swe_pos)
        processed.append(lemmatized if status == 'ok' else syn)
    return processed


def process_eng_synonyms(synonyms, keepcase=False, continue_on_issues=False):
    """
    Clean, spell-check, and lemmatize each English alternative translation.
    Drops entries that fail the character check. Entries that fail the
    English spell check are dropped by default; when continue_on_issues
    is set they're kept in cleaned form instead, for the same reason as
    in process_synonyms - only opt-in since it can also let a genuine
    misspelling through uncorrected.
    All-caps single words are treated as acronyms and bypass spell-checking.
    POS is derived independently per synonym.
    Returns list of processed strings.
    """
    # english_lemmatizer's single-word branch expects a WordNet-style tag
    # (N/V/A/Ab, matching the "ab" -> "r" special case it already handles),
    # but english_pos() returns raw Penn Treebank tags (NN, VB, JJ, RB, ...).
    # Map between the two so single-word synonyms don't hit an unmapped tag.
    def to_single_word_pos(penn_tag):
        first_tag = penn_tag.split(" ")[0]
        if first_tag.startswith("VB"):
            return "V"
        if first_tag.startswith("JJ"):
            return "A"
        if first_tag.startswith("RB"):
            return "Ab"
        return "N"

    processed = []
    for syn in synonyms:
        syn = re.sub(r'\s+', ' ', syn).strip()
        is_acronym = syn.isupper() and ' ' not in syn
        if not keepcase:
            syn = syn.lower()
        if not re.match(r'^[a-zA-Z\- \d]+$', syn):
            continue
        if is_acronym:
            processed.append(syn)
            continue
        if not is_word_in_english(syn):
            if continue_on_issues:
                processed.append(syn)
            continue
        eng_pos_tag = english_pos(syn)
        lemmatized = english_lemmatizer(syn, to_single_word_pos(eng_pos_tag), eng_pos_tag)
        processed.append(lemmatized)
    return processed


def main():
    """
    Main function to orchestrate the processing of English-Swedish computer science term pairs.

    Parses command-line arguments to handle single input pairs or batch processing on a server.
    Performs a series of processing steps including data cleaning, spell checking, POS tagging,
    and lemmatization. Outputs results, handles file logging, and data exporting based on the environment.
    """

    # Setup command-line arguments for processing term pairs
    parser = argparse.ArgumentParser(
        description="Automatically process english-swedish computer science term pairs"
    )
    parser.add_argument("-s", "--strings", nargs=3, help="Two term pairs")
    parser.add_argument(
        "-srv",
        "--server",
        action="store_true",
        help="flag for indicating the file is being run on the server",
    )
    parser.add_argument(
        "-test",
        "--test",
        action="store_true",
        help="flag for running against the teststunda instance",
    )
    parser.add_argument(
        "-keepcase",
        "--keepcase",
        action="store_true",
        help="keep the original case of lemmas from unprocessed.csv (do not lowercase)",
    )
    parser.add_argument(
        "-coi",
        "--continue-on-issues",
        action="store_true",
        help="run spell check, POS tagging, lemmatization and inflection generation "
        "for every entry, even those with misspellings or POS disagreement, "
        "instead of stopping early. Entries are still sent to manual review "
        "with every detected issue listed instead of being auto-approved.",
    )

    args = parser.parse_args()

    data_dir = "/var/lib/teststunda" if args.test else "/var/lib/stunda"
    print(f"Using data directory: {data_dir}")

    # Initialize flags and data structures for processing
    term_pairs = []
    df = None
    og_df = None

    # Handle command-line inputs and setup DataFrame accordingly
    if args.strings:
        load_dotenv()
        term_pairs.append(
            {
                "eng_lemma": args.strings[0],
                "swe_lemma": args.strings[1],
                "src": args.strings[2],
            }
        )
        df = pd.DataFrame(term_pairs)
    elif args.server or args.test:
        load_dotenv(dotenv_path=f"{data_dir}/data/.env")
        df = pd.read_csv(f"{data_dir}/terms/unprocessed.csv", encoding="utf-8", index_col=False)
        if 'comment' not in df.columns:
            df['comment'] = ''
        df = df.astype(str)
        df['comment'] = df['comment'].replace('nan', '')
        df = df[df['eng_lemma'] != 'eng_lemma']
        og_df = df.copy()

        now = datetime.now()
        datetime_string = now.strftime("%Y-%m-%d %H:%M:%S")

        # Save original input
        df.to_csv(
            f"{data_dir}/historical_processed/unprocessed_{datetime_string}.csv",
            index=False,
            encoding="utf-8",
        )

        if len(df) == 0:
            return
    else:
        print("Missing or incorrect arguments")
        exit(1)

    # Split swe_lemma on comma; first part is lemma, rest are synonyms
    df['swe_synonyms'] = df['swe_lemma'].apply(
        lambda x: [s.strip() for s in str(x).split(',')[1:]]
    )
    df['swe_lemma'] = df['swe_lemma'].apply(
        lambda x: str(x).split(',')[0].strip()
    )
    # Default synonyms to raw list; overwritten with processed synonyms after lemmatization
    df['synonyms'] = df['swe_synonyms']

    # Split eng_lemma on comma; first part is lemma, rest are alternative translations
    df['eng_alt_raw'] = df['eng_lemma'].apply(
        lambda x: [s.strip() for s in str(x).split(',')[1:]]
    )
    df['eng_lemma'] = df['eng_lemma'].apply(
        lambda x: str(x).split(',')[0].strip()
    )
    # Default alternative_translations to raw list; overwritten after lemmatization
    df['alternative_translations'] = df['eng_alt_raw']

    # Initialize DataFrame column for agreed POS
    df["agreed_pos"] = ""

    t0 = time.time()

    # Time the cleaning and simple checks
    start_time = time.time()
    df = clean_and_simple_checks(df, keepcase=args.keepcase)
    print("finished simple checks in {:.2f} seconds".format(time.time() - start_time))

    df_stop1 = df[df["status"] != "shallow processed"]
    df_cont = df[df["status"] == "shallow processed"]

    # Time the spell check
    start_time = time.time()
    df = spell_check(df_cont.copy())
    print(
        "finished spell check in {:.2f} minutes".format((time.time() - start_time) / 60)
    )

    if args.continue_on_issues:
        # Keep every entry moving through the rest of the pipeline; the
        # misspelling reason is preserved in "spell_status" and folded
        # back into the final status/reason further down.
        df_stop2 = df.iloc[0:0]
        df_cont = df
    else:
        df_stop2 = df[df["status"] != "spelling ok"]
        df_cont = df[df["status"] == "spelling ok"]

    # Time the part-of-speech tagging
    start_time = time.time()
    df = pos(df_cont.copy())
    print(
        "finished part-of-speech tagging in {:.2f} minutes".format(
            (time.time() - start_time) / 60
        )
    )

    if args.continue_on_issues:
        # Same as above: keep going, "pos_status" remembers the disagreement.
        df_stop3 = df.iloc[0:0]
        df_cont = df
    else:
        df_stop3 = df[df["status"] != "found pos"]
        df_cont = df[df["status"] == "found pos"]

    # Time the lemmatization
    start_time = time.time()
    df = lemmatize(df_cont.copy(), keepcase=args.keepcase)
    print(
        "finished lemmatization in {:.2f} minutes".format(
            (time.time() - start_time) / 60
        )
    )

    # Process synonyms for rows that completed lemmatization
    df['synonyms'] = [process_synonyms(s, continue_on_issues=args.continue_on_issues) for s in df['swe_synonyms']]
    df['alternative_translations'] = [process_eng_synonyms(s, keepcase=args.keepcase, continue_on_issues=args.continue_on_issues) for s in df['eng_alt_raw']]

    # Drop duplicate entries over swedish lemma, engish lemma, pos and source
    df = df.drop_duplicates(subset=["eng_lemma", "swe_lemma", "agreed_pos", "src"])

    # Aggregate the sources
    aggregated_sources_df = (
        df.groupby(["swe_lemma", "eng_lemma", "agreed_pos"])["src"]
        .apply(lambda x: ", ".join(x))
        .reset_index()
    )
    df = df.drop(columns="src").drop_duplicates(subset=["eng_lemma", "swe_lemma", "agreed_pos"])
    df = df.merge(aggregated_sources_df, on=["swe_lemma", "eng_lemma", "agreed_pos"])

    # Generate inflections for the processed terms
    df = generate_inflections(df)

    print(
        "finished generating inflections in {:.2f} minutes".format(
            (time.time() - start_time) / 60
        )
    )

    # Concatenate all parts
    output_df = pd.concat([df_stop1, df_stop2, df_stop3, df]).reset_index(drop=True)

    if 'comment' not in output_df.columns:
        output_df['comment'] = ''
    else:
        output_df['comment'] = output_df['comment'].fillna('').replace('nan', '')

    if "swedish_inflections" not in output_df.columns:
        output_df["swedish_inflections"] = None
        output_df["english_inflections"] = None

    # Check for and mark any entries with banned words
    output_df = check_for_banned_words(output_df)

    # Check if terms already exist in the KARP database
    existing_terms = get_all()
    output_df["already_exist"] = False
    output_df.loc[~output_df.contains_banned, "already_exist"] = output_df.loc[
        ~output_df.contains_banned
    ].apply(lambda x: term_already_exists(existing_terms, x), axis=1)

    # calculate total processing time
    total_time = time.time() - t0
    print("Total processing time: {:.2f} minutes".format(total_time / 60))

    # Handle output based on the environment (server or local)
    if args.server or args.test:

        if args.continue_on_issues:
            # "status" currently only reflects the outcome of the last step
            # that touched the row (lemmatization), since spell_check() and
            # pos() no longer stop rows with issues before overwriting it.
            # Fold the earlier spell/POS outcomes back in so no issue is
            # silently dropped from what the manual reviewer sees.
            def combine_status(row):
                spell_status = row.get("spell_status")
                pos_status = row.get("pos_status")

                # Rows that never reached spell_check() (format check
                # failures) don't have these columns populated - status
                # already holds the right reason for them.
                if pd.isna(spell_status) and pd.isna(pos_status):
                    return row["status"]

                issues = []
                if pd.notna(spell_status) and spell_status != "spelling ok":
                    issues.append(spell_status)
                if pd.notna(pos_status) and pos_status != "found pos":
                    issues.append(pos_status)
                if row["status"] != "automatically verified":
                    issues.append(row["status"])

                return "; ".join(issues) if issues else "automatically verified"

            output_df["status"] = output_df.apply(combine_status, axis=1)

        def set_reason(status):
            if status == "automatically verified":
                return ""
            else:
                return status

        output_df["reason"] = output_df["status"].apply(set_reason)

        output_df.loc[~(output_df.status == "automatically verified"), "status"] = (
            "not automatically verified"
        )
        # Extract entries with banned words
        df_banned = output_df.loc[output_df.contains_banned]

        # Extract terms that already exist in KARP
        df_exist_already = output_df.loc[output_df.already_exist]

        # Extract the rest as new terms
        df_new_terms = output_df.loc[
            (~output_df.contains_banned) & (~output_df.already_exist)
        ]

        # Column values to save for data storage
        columns_to_save = [
            "eng_lemma",
            "swe_lemma",
            "src",
            "status",
            "agreed_pos",
            "swedish_inflections",
            "english_inflections",
            "reason",
            "synonyms",
            "alternative_translations",
            "comment",
        ]

        # Converting the selected DataFrame to a list of JSON objects
        jsonl_banned = json.loads(
            df_banned[columns_to_save].to_json(orient="records", force_ascii=False)
        )

        # Saved banned entries
        with open(f"{data_dir}/terms/banned.jsonl", "a", encoding="utf-8") as file:
            for item in jsonl_banned:
                json_line = json.dumps(item, ensure_ascii=False) + "\n"
                file.write(json_line)

        # Converting the selected DataFrame to a list of JSON objects
        jsonl_new_terms = json.loads(
            df_new_terms[columns_to_save].to_json(orient="records", force_ascii=False)
        )

        # Save new entries
        with open(f"{data_dir}/terms/processed.jsonl", "a", encoding="utf-8") as file:
            for item in jsonl_new_terms:
                file.write(json.dumps(item, ensure_ascii=False) + "\n")

        # Converting the selected DataFrame to a list of JSON objects
        jsonl_existing_terms = json.loads(
            df_exist_already[columns_to_save].to_json(
                orient="records", force_ascii=False
            )
        )

        # Save already existing entries
        with open(f"{data_dir}/terms/approved.jsonl", "a", encoding="utf-8") as file:
            for item in jsonl_existing_terms:
                file.write(json.dumps(item, ensure_ascii=False) + "\n")

        # Remove all processed entries from unprocessed
        og_df.head(0).to_csv(
            f"{data_dir}/terms/unprocessed.csv", index=False, encoding="utf-8"
        )
    else:

        print("English lemma:", output_df.at[0, "eng_lemma"])
        print("Swedish lemma:", output_df.at[0, "swe_lemma"])
        print("Status       :", output_df.at[0, "status"])
        if (
            "agreed_pos" in output_df.columns
            and len(output_df.at[0, "eng_lemma"].split(" ")) == 1
            and len(output_df.at[0, "swe_lemma"].split(" ")) == 1
        ):
            print("POS          :", output_df.at[0, "agreed_pos"])


main()
