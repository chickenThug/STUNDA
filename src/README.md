# Automatic term processing flow
This folder contains everything necessary for the automatic processing of terms.

## `utils.py`
Utils är ett pythonscript som innehåller funktioner som används för termprocesseringen i automatic_flow.py. Exempel på dessa är lemmatisering av svenska och engelska ord och bestämning av ordklass.

## `automatic_flow.py`

The automatic processing of incoming terms stored in `unprocessed.csv` is handled by `automatic_flow.py`.

The processing consists of the following steps:

1. Data cleaning
    1. Excess whitespace is removed and the terms are converted to lowercase
    2. Paranthesis data is removed
    3. An assertion is made that the termp pairs can only consist of a set of predefined chars
2. Spell checking
    1. The swedish spell checking consist of dictionary look up against [Skrutten API](https://skrutten.csc.kth.se/granskaapi/spell/)
    2. The english spell checking consist of dictionery look up against the Brown Corpus
3. Part-of-Speech tagging
    1. Find all possible POS tags for the english term using nltk
    2. Find all possible POS tags for the swedish term using [Skrutten API](https://skrutten.csc.kth.se/granskaapi/taggstava/)
    3. Take the intersection of the two sets and assert it should be a single POS tag
4. Lemmatization
    1. Swedish lemmatization is performed using [Skrutten API](https://skrutten.csc.kth.se/granskaapi/lemma/)
    2. English lemmatization is performed using nltk
5. Inflection generation
    1. Swedish inflections are generated using [SALDO](https://spraakbanken.gu.se/karp/?mode=saldom&lexicon=saldom&show=saldom:01HQMY872TVCZGR3YPBQ5Q970T&filter=)
    2. English inflection are generated using the library lemminflect
6. Checking for blacklisted words
7. Checking if the term pair already exist in KARP

After processing the term pairs, term pairs containing banned words are stored in the `banned.jsonl` file on the server. For the term pairs which already exist in the KARP database, the source is appended to the entry in KARP. The rest of the term pairs are saved in `processed.jsonl` file ready for manual verification. 