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

## Java Servlets
In the folder `/se` the Servlets for the project are located.

### Check Login Servlet
Gets called from `login.js` when a user tries to log in. Takes an entered username and password from the user, and checks similarity of these towards the saved username and password stored on the server. Returns a boolean value isValid depending on if the username and password matches.

### Single Term Upload Servlet

### Term Upload Servlet

### Term Verification Servlet

### Handle Verified Terms Servlet

### Upload Report Servlet
Gets called from `search.js` whenever a user decides to report a term. Takes the swedish lemma, english lemma, the reason for the report (non computing term, wrong translation, inappropriate or other) as well as the timestamp for the report. It then saves this report on the server.

### Log Search Servlet
Gets called from `search.js` when a user makes a search at the search page. Takes the search string, the search hits from the database, if the search was successful, the timestamp for the search and the language the search was made from. It then logs this on the server.

### Log Upload Servlet
Gets called from `upload.js` when a user uploads terms from the upload page. It takes the timestamp for the upload, the type of upload (single term pair or file) and if the upload was successful. It then logs this on the server.