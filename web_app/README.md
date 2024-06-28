# Web application
This folder contains everything necessary for the web deployment of the project.

## Directories
- `files` contains the outline.csv available to the user on the upload page.

- `images` contains all of the images and icons used on the web page

- `WEB_INF` contains the xml file, the java classes and the jar files needed for the java servlets

## Pages and files
All of the pages gathered CSS is contained in the `style.css` file.
### Search page
The search page consists of `index.html` and `search.js`.

The functionality and purpose of the page is for the user to be able to search for data terms in either Swedish or English.

The user selects a language for the page as well as a language to search from and then enters a term and searches. That makes an API call to KARP to get the terms that matches the search in the database. The best and most similar term pair to the search is then shown to the user, while the other hits are shown in a field to the side.

For the best search hit the swedish lemma, english lemma, inflections, alternative translations and soures are displayed to the user.

If there are no terms on KARP that matches the users search, the user is suggested to visit the upload page to upload the term.

#### Report functionality
The user has the ability to report a term by clicking on the interrobang symbol that is displayed for each term. By conducting a report, the user can specify what they want to report with the term (for example if they believe that it is a bad translation, not a valid data term etc). The report is then saved in is full format on the server, and a log that a report has been made is also saved on the server.

#### Servlet calls
The searchpage makes fetches to the following servlets:
- POST to `log-search`for logging the searches. 
- POST to `log-report-data` for logging the report data.

### Upload page
The upload page consists of `upload.js` and `upload.html`.

The functionality and purpose of this page is to allow the user to upload term pairs that will then be processed by the automatic flow and manually verified to either be added to the database or rejected.

The user is shown a instruction for the upload, and also has the option to download an outline csv file where they can add their terms.

The user can either:
1. upload a single term pair
2. upload a csv file containing multiple term pairs at once

A part from these input fields, there is also fields for source and contact information. There is also a checkbox that ensures that the user gives the rights for the terms to be publically uploaded in STUNDA.

Source and rights for upload are mandatory fields for the user to be able to upload the terms. It is not valid with a ","-symbol in the source.

The terms that are uploaded by the user is saved in the file unprocessed.csv on the format "eng_lemma,swe_lemma,src" on the server.

#### Servlet calls
The searchpage makes fetches to the following servlets:
- POST to `single-term-upload` for adding a single term pair to the unprocessed.csv file on the server
- POST to `term-upload` for adding a csv of terms to the unprocessed.csv file on the server

### Verification page
The verification page is a page that is only available for members of the STUNDA-project. It it protected by a login-page consisting of `login.html` and `login.js`. `login.js`makes a POST call to the check-login servlet to check wether the credentials are correct, and uses session storage to store the authentication of a user. 

If the user has the right login-credentials, they are connected to the verification page consisting of the `verify.js`and `verify.html`page.

The purpose of the verification page is to have a web interface to manually verify all of the uploaded and processed terms, and having the opportunity to upload them to KARP.

The verification page reads the terms from the processed.jsonl file (which contains terms that have been processed by the automatic flow). It displays the terms in a table manner, where the user can check a checkbox to confirm upload of the term to the database, or uncheck the checkbox to deny the upload.

The verification page displays 25 term pairs from unprocessed.jsonl file at a time, and the user has to go through these and press the submit button in order to be prompted with 25 new terms (if there exists 25 more).

#### Servlet calls
- POST to `handle-verify` to 