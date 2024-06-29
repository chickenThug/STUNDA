# Automatic term processing flow
This folder contains everything necessary for the automatic processing of terms.

## `utils.py`
Utils contains functions that are used for the term processing in `automatic_flow.py`. Example of these are the spell check and lemmatization of both Swedish and English terms.

## `automatic_flow.py`
The automatic processing of incoming terms stored in `unprocessed.csv` is handled by `automatic_flow.py`.

The processing consists of the following steps:

1. Data cleaning
    1. Excess whitespace is removed and the terms are converted to lowercase
    2. Paranthesis data is removed
    3. An assertion is made that the term pairs can only consist of a set of predefined chars
2. Spell checking
    1. The swedish spell checking consist of dictionary look up against [Skrutten API](https://skrutten.csc.kth.se/granskaapi/spell/)
    2. The english spell checking consist of dictionary look up against the Brown Corpus
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

After processing the term pairs, all pairs containing banned words are stored in the `banned.jsonl` file on the server. For the term pairs which already exist in the KARP database, the source is appended to the entry in KARP. The rest of the term pairs are saved in the `processed.jsonl` file ready for manual verification. 

## Java Servlets
The Servlets for the project are located in the folder `/se`.

### Single Term Upload Servlet
Gets called from `upload.js` when a user tries to upload a single term pair. Takes the entered swedish lemma, english lemma and the source from the user and saves these in the file `unprocessed.csv` on the server.

### Term Upload Servlet
Gets called from `upload.js` when a user tries to upload a file. It takes the csv file and the source from the user and saves these in the file `unprocessed.csv` on the server.

### Upload Report Servlet
Gets called from `search.js` whenever a user decides to report a term. Takes the swedish lemma, english lemma, the reason for the report (non computing term, wrong translation, inappropriate or other) as well as the timestamp for the report. It then saves this report on the server in the file `report_data.txt`.

### Log Search Servlet
Gets called from `search.js` when a user makes a search at the search page. Takes the search string, the search hits from the database, if the search was successful, the timestamp for the search and the language the search was made from. It then logs this in the file `log_search.txt` on the server.

### Log Upload Servlet
Gets called from `upload.js` when a user uploads terms from the upload page. It takes the timestamp for the upload, the type of upload (single term pair or file) and if the upload was successful. It then logs this in the file `log_upload.txt` on the server.

### Check Login Servlet
Gets called from `login.js` when a user tries to log in. Takes an entered username and password from the user, and checks similarity of these towards the saved username and password stored on the server. Returns a boolean value isValid depending on if the username and password matches.

### Term Verification Servlet
Gets called from `verify.js` on page load. It reads from the file `processed.jsonl` containing processed terms on the server and returns these to the client to be displayed to the user.

### Handle Verified Terms Servlet
Gets called from `verify.js` when the user presses the button for approval of terms. The servlets functionality includes handling the approved and not approved terms, ensuring the database is updated correctly and that every term pair is saved at the correct file.

The flow of the Servlet is:
1. Environment Config
- The Servlet loads the KARP API key from the server
2. Reading and Parsing Request
- It reads the incoming JSON data from the request, which contains terms marked as approved and not approved, and sorts these into approvedArray and notApprovedArray
3. Logging 
- Loggs the approval of each term pair to `log_verify.txt` containing information about the username, swedish lemma, english lemma, timestamp and if the term pair was approved or not
4. Updating Processed terms
- Reads the existing processed terms from `processed.jsonl` and retains those not present in the current incoming terms
5. Handling not approved terms
- Writes all of the non-approved terms to `notapproved.jsonl`
6. KARP Database Interaction
- For each approved item: checks its presence in the KARP database using `getItem`
- If the term pair already exists in KARP, update its entry to include the new source
- If the term does not exist, construct a new entry and add it do KARP using `addEntry`
7. Final File Updates
- Write remaining processed terms back to `processed.jsonl`
- Write approved terms to `approved.jsonl`
8. Response
- Responds to the client with a message if the operations were successful or not