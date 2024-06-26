// Function to get terms from the KARP database
function getTermsFromKarp(field, query_mode, searchString) {
    const apiUrl = `https://spraakbanken4.it.gu.se/karp/v7/query/stunda?q=and(or(${query_mode}|${field}|"${searchString}"))&from=0&size=100`;
    return fetch(apiUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
        return "error";
      });
}

// Function called 
async function search(language, searchString) {
    let languageLemma = "";
    let oppositeLang = "";
    let oppositeLemma = "";
    if (language === "swe") {
        languageLemma = "swedishLemma";
        oppositeLemma = "englishLemma";
        oppositeLang = "eng";
    }
    else if (language === "eng") {
        languageLemma = "englishLemma";
        oppositeLemma = "swedishLemma";
        oppositeLang = "swe";
    }
    else {
        throw new Error(`Unknown language '${language}': can only accept 'swe' or 'eng'.`);
    }

    let matches = await getTermsFromKarp(`${language}.lemma`, "startswith", searchString);

    if (matches === "error") {
        return "error"
    }

    // Dictionary for keeping track of unique entries
    const entries = {};
    // Dictionary for keeping track of seen lemmas
    const seen_lemmas = {};

    matches.hits.forEach(hit => {
        const lemma = hit.entry[language].lemma;
        const pos = hit.entry.pos;
        // Define key for unique entry as the searrch language lemma + part-of-speech
        const key = lemma + ";" + pos;
        if (!entries[key]) { // new lemma
            let display_pos = false; // boolean indicating weather or not to display the part of speech in the response list
            if (seen_lemmas[lemma]) {
                const seen_key = seen_lemmas[lemma];
                entries[seen_key].display_pos = true;
                // append key for the given lemma
                seen_lemmas[lemma] = key;
                display_pos = true;
            }
            else {
                seen_lemmas[lemma] = key;
            }

            entries[key] = {
                id: hit.id,
                swedishLemma: hit.entry.swe.lemma,
                englishLemma: hit.entry.eng.lemma,
                source: hit.entry.src.split(", "),
                pos: [hit.entry.pos],
                display_pos: display_pos,
                swedishInflections: hit.entry.swe.inflection ?? [],
                englishInflections: hit.entry.eng.inflection ?? [],
                alternativeTranslations: hit.entry.synonyms ?? []
            };
        } else {
            let sources_old = entries[key].source;
            let sources_new = hit.entry.src.split(", ");

            if (sources_old.length < sources_new.length) {
                let opposite_lemma = entries[key][oppositeLemma];
                let old_translations = entries[key].alternativeTranslations;
                entries[key] = {
                    id: hit.id,
                    swedishLemma: hit.entry.swe.lemma,
                    englishLemma: hit.entry.eng.lemma,
                    source: hit.entry.src.split(", "),
                    pos: [hit.entry.pos],
                    display_pos: entries[key].display_pos,
                    swedishInflections: hit.entry.swe.inflection ?? [],
                    englishInflections: hit.entry.eng.inflection ?? [],
                    alternativeTranslations: hit.entry.synonyms ?? []
                };
                for (const synonym in old_translations) {
                    entries[key].alternativeTranslations.push(synonym)
                }
                entries[key].alternativeTranslations.push(`${opposite_lemma} (${sources_old})`);
            }
            else {
                entries[key].alternativeTranslations.push(`${hit.entry[oppositeLang].lemma} (${hit.entry.src})`);
            }
        }
      });

      // Convert the object back to an array
      let sortedEntries = Object.values(entries);

      // Sort to prioritize the exact match
      sortedEntries.sort((a, b) => {
          if (a[languageLemma] === searchString && b[languageLemma] !== searchString) {
              return -1;
          } else if (a[languageLemma] !== searchString && b[languageLemma] === searchString) {
              return 1;
          }
          return 0;
      });
      return sortedEntries;
  }


let display_entry = {}

const sourceExplanationEnglish = {
    "PK" :"Keywords scraped from thesis projects",
    "ACM" : "Association for Computing Machinery",
    "ICT" : "Mechanically extracted terms from the KTH course IK2554 lecture notes in June 2014",
    "GF" : "Terms collected by a bachelor project group at Chalmers in 2020"
}

const sourceExplanationSwedish = {
    "PK" :"Nyckelord skrapade från examensarbeten",
    "ACM" : "Association for Computing Machinery",
    "ICT" : "Skrapade termer från KTH-kursens IK2554 föreläsningsanteckningar juni 2014",
    "GF" : "Insamlade termer av en kandidatprojektgrupp vid Chalmers 2020"
}

const posMapEnglish = {
    "N" :"Noun",
    "V" : "Verb",
    "A" : "Adjective",
    "Ab" : "Adverb",
    "NP" : "Noun phrase"
}

const posMapSwedish = {
    "N" :"Substantiv",
    "V" : "Verb",
    "A" : "Adjektiv",
    "Ab" : "Adverb",
    "NP" : "Substantivfras"
}

// Function to create a bilingual map
function createBilingualMap(englishMap, swedishMap) {
    let bilingualMap = {};

    // Populate the bilingual map with entries for both languages
    for (const key in englishMap) {
        if (englishMap.hasOwnProperty(key) && swedishMap.hasOwnProperty(key)) {
            const engExplanation = englishMap[key];
            const sweExplanation = swedishMap[key];
            bilingualMap[engExplanation] = sweExplanation;
            bilingualMap[sweExplanation] = engExplanation;
        }
    }

    return bilingualMap;
}

const bilingualExplanationMap = createBilingualMap(sourceExplanationEnglish, sourceExplanationSwedish);

let last_get_similar_words_result = {};

let language = 'swe'; // Language of the page

let switched_view = 'no'; // If the user has switched the view or not

let done_search = 'no'; // If a search has been done

let new_best_result = display_entry;

// Function called when user makes a search. Calls functions for searching for words and displaying the results
const getResults = async (word, search_language) => {
    done_search = 'yes';

    let result = await search(search_language, word); // Making the search

    // Create a new Date object
    let now = new Date();

    // Get the current date and time as a string
    let dateString = now.toString();

    if (result === "error") {
        const data = { searchString: word, searchHits: 0, successful: false, timestamp: dateString, searchLanguage: search_language }
        log_search(data);
        display_error_result();
        return
    }
    else {
        const data = { searchString: word, searchHits: result.length, successful: true, timestamp: dateString, searchLanguage: search_language }
        log_search(data);

        if (result.length == 0) {
            display_no_result();
            return
        }
    }

    let best = result.shift();

    display_entry = best;

    display_best_result(display_entry);

    last_get_similar_words_result = result;

    display_similar_results(search_language);

    // Show the search result containers
    document.getElementById("search-results").style.display = "block";
    document.getElementById("best-search-result").style.display = "block";
};

const handle_button_parsing = (string_data) => {
    const data = JSON.parse(string_data);
    display_entry = data;
    display_best_result(display_entry);
}

// Function for displaying when there are no hits on KARP
function display_no_result() {
    // Clear results
    document.getElementById("search-results").style.display = "none";

    best_word_container = document.getElementById("best-search-result");
    // Clear the container so we don't append the same results multiple times
    best_word_container.innerHTML = "";

    const rightSection = document.createElement("div");
    rightSection.classList.add("bottom-section");
    const paragraph = document.createElement("p");

     // Create the button element
     var button = document.createElement("button");
     button.className = 'redirect-button';
     button.id = 'redirect_button_id';

     // Add click event listener to the button
     button.addEventListener("click", function() {window.location.href = 'upload.html'; });

    if (language === "swe") {
        paragraph.innerHTML = "<strong>Inga sökresultat!</strong>";
        button.innerHTML = "Vill du ladda upp en term?";
    }
    else {
        paragraph.innerHTML = "<strong>No search results found!</strong>";
        button.innerHTML = "Want to upload a term?";
    }
    paragraph.classList.add("nores");
    best_word_container.appendChild(paragraph);
    best_word_container.appendChild(button);

    document.getElementById("best-search-result").style.display = "block";
}

// Function logging the search
function log_search(data) {
    fetch('/stunda/log-search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(data)
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.error('Error logging search:', error));
}

// Function for logging the report data
function log_report_data(data) {
    fetch('/stunda/log-report-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(data)
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.error('Error logging search:', error));
}

// Function for displaying errors
function display_error_result() {
    // Clear results
    document.getElementById("search-results").style.display = "none";

    best_word_container = document.getElementById("best-search-result");
    // Clear the container so we don't append the same results multiple times
    best_word_container.innerHTML = "";

    const rightSection = document.createElement("div");
    rightSection.classList.add("bottom-section");
    const paragraph = document.createElement("p");

    if (language === "swe") {
        paragraph.innerHTML = "<strong>Kunde inte nå KARP!</strong>";
    }
    else {
        paragraph.innerHTML = "<strong>Could not reach KARP!</strong>";
    }
    paragraph.classList.add("nores");
    best_word_container.appendChild(paragraph);

    document.getElementById("best-search-result").style.display = "block";
}

// Function for displaying the best search result div
const display_best_result = (data) => {
    best_word_container = document.getElementById("best-search-result");
    // Clear the container so we don't append the same results multiple times
    best_word_container.innerHTML = "";

    // Create divs to contain different sections
    const leftSection = document.createElement("div");
    leftSection.classList.add("left-section");

    const rightSection = document.createElement("div");
    rightSection.classList.add("right-section");

    const bottomSection = document.createElement("div");
    bottomSection.classList.add("bottom-section");

    // Report button
    const iconButton = document.createElement("img");
    iconButton.src = "images/interrobang.png";
    iconButton.alt = "Report Icon";
    iconButton.classList.add("icon-button");
    iconButton.onclick = () => {
        showModal();
    };

    // Append the icon button to the best_word_container
    best_word_container.appendChild(iconButton);

    if (language === 'swe') {

        // Paragraphs for left section
        create_paragraph("Svenska", data.swedishLemma, leftSection, true);
        if (data.swedishInflections.length !== 0){
            create_paragraph("Böjningar", data.swedishInflections, leftSection);
        }

        // Paragraphs for right section
        create_paragraph("Engelska", data.englishLemma, rightSection, true);
        if (data.englishInflections.length !== 0){
            create_paragraph("Böjningar", data.englishInflections, rightSection);
        }

        create_paragraph("Ordklass", posMapSwedish[data.pos], bottomSection);
        if (data.alternativeTranslations.length !== 0){
            create_paragraph("Alternativa översättningar", data.alternativeTranslations, bottomSection);
        }

        // Paragraphs for bottom section
        if (data.source.length === 1) {
            create_source_paragraph("Källa", data.source, bottomSection, language)
        } else {
            create_source_paragraph("Källor", data.source, bottomSection, language)
        }
    } else {
        // Paragraphs for left section
        create_paragraph("Swedish", data.swedishLemma, leftSection, true);
        if (data.swedishInflections.length !== 0){
            create_paragraph("Inflections", data.swedishInflections, leftSection);
        }

        // Paragraphs for right section
        create_paragraph("English", data.englishLemma, rightSection, true);
        if (data.englishInflections.length !== 0){
            create_paragraph("Inflections", data.englishInflections, rightSection);
        }

        create_paragraph("Part-of-speech", posMapEnglish[data.pos], bottomSection);
        if (data.alternativeTranslations.length !== 0){
            create_paragraph("Alternative translations", data.alternativeTranslations, bottomSection);
        }

        // Paragraphs for bottom section
        if (data.source.length === 1) {
            create_source_paragraph("Source", data.source, bottomSection, language)
        } else {
            create_source_paragraph("Sources", data.source, bottomSection, language)
        }
    }

    // Append sections to container
    best_word_container.appendChild(leftSection);
    best_word_container.appendChild(rightSection);
    best_word_container.appendChild(bottomSection);
}

// Function for displaying the similar result hits
const display_similar_results = (search_language) => {
    similar_words_result = last_get_similar_words_result;
    similar_words_container = document.getElementById("search-results");
    // Clear the container so we don't append the same results multiple times
    similar_words_container.innerHTML = "";

    const header = document.createElement("h2");
    header.innerHTML = language === 'swe' ? "Sökträffar:" : "Search results:";
    similar_words_container.appendChild(header);

    create_button(display_entry, similar_words_container, search_language);

    for (word in similar_words_result) {
        create_button(similar_words_result[word], similar_words_container, search_language);
    }
}

// Function for creating paragraphs to append to the HTML
const create_paragraph = (title, value, container, bigFont) => {
    const paragraph = document.createElement("p");
    let displayValue = value;

    // logic for displaying multiple vs single values
    if (Array.isArray(value)){
        if (value.length === 1) {
            displayValue = value[0];
        } else {
            displayValue = value.join(", ")
        }
    }
    paragraph.innerHTML = `<strong>${title}:</strong> ${displayValue}`;

    // Add a class for bigger font if specified
    if (bigFont) {
        paragraph.classList.add("bigfont");
    }

    container.appendChild(paragraph);
}

const create_source_paragraph = (title, sources, container, language) => {
    const label = document.createElement('span');
    label.id = 'label-text';
    label.innerHTML = `<strong>${title}: </strong>`;
    container.appendChild(label);
    // Create a span for each source with a tooltip
    sources.forEach(source => {
        const wordSpan = document.createElement('span');
        wordSpan.classList.add('tooltip');
        wordSpan.textContent = source;

        const tooltipSpan = document.createElement('span');
        tooltipSpan.classList.add('info');
        if (language === "swe") {
            tooltipSpan.textContent = sourceExplanationSwedish[source];
        }
        else {
            tooltipSpan.textContent = sourceExplanationEnglish[source];
        }

        wordSpan.appendChild(tooltipSpan);
        container.appendChild(wordSpan);
        container.appendChild(document.createTextNode(', ')); // Add comma
    });

    // Remove the last comma
    if (container.lastChild) {
        container.removeChild(container.lastChild);
    }
}

// Function to create the buttons for the similar result div
const create_button = (data, container, language) => {
    const button = document.createElement("button");
    let lemma = language === "swe" ? data.swedishLemma : data.englishLemma;
    button.innerHTML = data.display_pos ? `${lemma} (${data.pos})` : `${lemma}`;
    button.setAttribute("onclick", `handle_button_parsing('${JSON.stringify(data)}')`);
    container.appendChild(button);
}

// Function to show the report modal
const showModal = () => {
    const modal = document.getElementById("report-modal");
    modal.style.display = "block";
    const reportForm = document.getElementById("report-form");
    if (reportForm) {
        reportForm.addEventListener("submit", handleFormSubmit);
    }
};

// Function to hide the report modal
const hideModal = () => {
    const modal = document.getElementById("report-modal");
    modal.style.display = "none";

    // Reset checkboxes
    const checkboxes = modal.querySelectorAll("input[type='checkbox']");
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });

    // Clear the text input
    const textInput = modal.querySelector("input[type='text']");
    if (textInput) {
        textInput.value = '';
    }

    // Hide the feedback message
    const feedbackMessage = modal.querySelector("#feedback-message");
    feedbackMessage.style.display = 'none';
};

// Function to handle form submission for the report modal
const handleFormSubmit = () => {
    const dataterm_error = document.getElementById("dataterm-checkbox").checked;
    const translation_error = document.getElementById("translation-checkbox").checked;
    const inappropriate_error = document.getElementById("inappropriate-checkbox").checked;
    const own_reason = document.getElementById("own-reason").value;
    let now = new Date();
    let dateString = now.toString();
    const data = { searchString: "user report", searchHits: 0, successful: true, timestamp: dateString, searchLanguage: "none" };
    const report_data = {
        sweLemma: display_entry.swedishLemma,
        engLemma: display_entry.englishLemma,
        nonComputingTerm: dataterm_error,
        wrongTranslation: translation_error,
        inappropiate: inappropriate_error,
        other: own_reason,
        timestamp: dateString
    };
    log_search(data);
    log_report_data(report_data);

    // Show the feedback message
    const feedbackMessage = document.getElementById("feedback-message");
    feedbackMessage.style.display = 'block';

    setTimeout(hideModal, 2000); // Hide modal after 2 seconds
};

// Logic for enter on the keyboard and not just pressing the search button
document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById("search-input");
    const searchLanguage = document.getElementById("search-language")

    // Add event listener for the "keydown" event on the input field
    searchInput.addEventListener("keydown", function(event) {
        // Check if the pressed key is "Enter" (key code 13)
        if (event.keyCode === 13) {
            // Prevent the default action of the "Enter" key (form submission)
            event.preventDefault();
            // Call the getResults function with the input value
            getResults(searchInput.value, searchLanguage.value);
        }
    });
});

// Function to change text content to English
const switchToEnglish = () => {
    document.documentElement.lang = 'en';
    // Change logo text
    document.querySelector('.logo-main').textContent = 'STUNDA';
    document.querySelector('.logo-sub').textContent = 'Swedish Technical University Network for Computing Terms';

    // Change info text
    document.querySelector('.info-text p').innerHTML = 'Stunda is a network for Sweden\'s technical universities aimed at promoting efficient technical communication in Swedish within higher education, primarily by working with discipline-specific terminology. Read more <a href="https://writing.chalmers.se/stunda/" target="blank">here</a>. For advanced search, see <a href="https://spraakbanken.gu.se/karp/tng/?mode=stunda&lexicon=stunda&show=stunda:01GX3DS1AKX7YZVYR6F5V8VZS6">KARP</a>.';

    // Change button text
    document.querySelector('.search-button').textContent = 'Search';

    // Change placeholder text
    document.getElementById('search-input').setAttribute('placeholder', 'Data term...');

    // Change dropdown label text
    document.querySelector('.search-options label').textContent = "Search language:";

    // Change dropdown text
    document.querySelector('.swe').textContent = 'Swedish';
    document.querySelector('.eng').textContent = 'English';

    // Change report modal text
    document.querySelector('#report-modal-content p').textContent = 'You are now choosing to report this term. Please check one of the options or provide your own reason for the report:';
    document.querySelector('label[for="dataterm-checkbox"]').textContent = 'Not a data term';
    document.querySelector('label[for="translation-checkbox"]').textContent = 'Incorrect translation';
    document.querySelector('label[for="inappropriate-checkbox"]').textContent = 'Inappropriate term';
    document.querySelector('label[for="own-reason"]').textContent = 'Other reason:';
    document.querySelector('#send-button').textContent = 'Send';
    document.querySelector('#feedback-message').textContent = 'The report has been sent!';

    if (done_search === 'yes') {
        // Change header text
        const searchResultsHeader = document.querySelector('#search-results h2');
        if (searchResultsHeader) {
            searchResultsHeader.textContent = 'Search results:';
        }

        // Translate content within best-search-result
        const bestSearchResult = document.getElementById('best-search-result');
        const paragraphs = bestSearchResult.querySelectorAll('p');

        //Translate upload term button
        const redirect_button = document.getElementById('redirect_button_id');
        if (!(redirect_button == null)) {
            redirect_button.textContent = "Want to upload a term?";
        }

        // Translate sources and tooltip TODO: add null check for label-text
        const tooltips = bestSearchResult.getElementsByClassName('info');
        const source_label = document.getElementById('label-text');

        if (!(source_label == null)){
            if (source_label.innerHTML.includes("Källor")){
                source_label.innerHTML = `<strong>Sources: </strong>`;
            }
            else if (source_label.innerHTML.includes("Källa")) {
                source_label.innerHTML = `<strong>Source: </strong>`;
            }
        }

        for (let tooltip of tooltips) {
            const swedish_text = tooltip.textContent;
            tooltip.textContent = bilingualExplanationMap[swedish_text];
        }

        paragraphs.forEach(paragraph => {
            // Translate each paragraph content
            if (paragraph.textContent.includes('Svenska')) {
                paragraph.innerHTML = '<strong>Swedish:</strong> ' + display_entry.swedishLemma;
            } else if (paragraph.textContent.includes('Böjningar')) {
                paragraph.innerHTML = '<strong>Inflections:</strong> ' + display_entry.swedishInflections.join(', ');
            } else if (paragraph.textContent.includes('Engelska')) {
                paragraph.innerHTML = '<strong>English:</strong> ' + display_entry.englishLemma;
            } else if (paragraph.textContent.includes('Böjningar')) {
                paragraph.innerHTML = '<strong>Inflections:</strong> ' + display_entry.englishInflections.join(', ');
            } else if (paragraph.textContent.includes('Ordklass')) {
                paragraph.innerHTML = '<strong>Part-of-speech:</strong> ' + posMapEnglish[display_entry.pos];
            } else if (paragraph.textContent.includes('Alternativa översättningar')) {
                paragraph.innerHTML = '<strong>Alternative translations:</strong> ' + display_entry.alternativeTranslations.join(', ');
            }else if (paragraph.textContent.includes('Inga sökresultat!')) {
                paragraph.innerHTML = '<strong>No search results found!</strong>';
            }else if (paragraph.textContent.includes('Kunde inte nå KARP!')) {
                paragraph.innerHTML = '<strong>Could not reach KARP!</strong>';
            }
        });
        const similarSearchHeader = document.getElementById('search-results');
        const header = similarSearchHeader.querySelectorAll('h2');
        header.innerHTML = 'Search results:';
    }
};

// Function to change text content to Swedish
const switchToSwedish = () => {
    document.documentElement.lang = 'sv';
    // Change logo text
    document.querySelector('.logo-main').textContent = 'STUNDA';
    document.querySelector('.logo-sub').textContent = 'Sveriges Tekniska Universitets Nätverk för Datatermer';

    // Change info text
    document.querySelector('.info-text p').innerHTML = 'Stunda är ett nätverk för sveriges tekniska universitet med syfte att verka för effektiv fackspråklig kommunikation på svenska inom högre utbildning, främst genom att arbeta med disciplinspecifik terminologi. Läs mer <a href="https://writing.chalmers.se/stunda/" target="blank">här</a>. För avancerad sökning, se <a href="https://spraakbanken.gu.se/karp/tng/?mode=stunda&lexicon=stunda&show=stunda:01GX3DS1AKX7YZVYR6F5V8VZS6">KARP</a>.';

    // Change button text
    document.querySelector('.search-button').textContent = 'Sök';

    // Change placeholder text
    document.getElementById('search-input').setAttribute('placeholder', 'Dataterm...');

    // Change dropdown label text
    document.querySelector('.search-options label').textContent = "Sökspråk:";

    // Change dropdown text
    document.querySelector('.swe').textContent = 'Svenska';
    document.querySelector('.eng').textContent = 'Engelska';

    // Change report modal text
    document.querySelector('#report-modal-content p').textContent = 'Du väljer nu att rapportera denna term. Vänligen tryck i ett av alternativen eller ange egen anledning till rapporteringen:';
    document.querySelector('label[for="dataterm-checkbox"]').textContent = 'Ingen dataterm';
    document.querySelector('label[for="translation-checkbox"]').textContent = 'Felaktig översättning';
    document.querySelector('label[for="inappropriate-checkbox"]').textContent = 'Olämplig term';
    document.querySelector('label[for="own-reason"]').textContent = 'Annan anledning:';
    document.querySelector('#send-button').textContent = 'Skicka';
    document.querySelector('#feedback-message').textContent = 'Rapporten har skickats!';

    if (done_search === 'yes'){
        // Change header text
        const searchResultsHeader = document.querySelector('#search-results h2');
        if (searchResultsHeader) {
            searchResultsHeader.textContent = 'Sökträffar:';
        }

        // Translate content within best-search-result
        const bestSearchResult = document.getElementById('best-search-result');
        const paragraphs = bestSearchResult.querySelectorAll('p');

        // Translate sources tooltips
        const tooltips = bestSearchResult.getElementsByClassName('info');
        const source_label = document.getElementById('label-text');

        //Translate upload term button
        const redirect_button = document.getElementById('redirect_button_id');
        if (!(redirect_button == null)) {
            redirect_button.textContent = "Vill du ladda upp en term?";
        }

        if (!(source_label == null)){
            if (source_label.innerHTML.includes("Sources")) {
                source_label.innerHTML = `<strong>Källor: </strong>`;
            }
            else if (source_label.innerHTML.includes("Source")) {
                source_label.innerHTML = `<strong>Källa: </strong>`;
            }
        }

        for (let tooltip of tooltips) {
            const english_text = tooltip.textContent;
            tooltip.textContent = bilingualExplanationMap[english_text];
        }

        paragraphs.forEach(paragraph => {
            // Translate each paragraph content
            if (paragraph.textContent.includes('Swedish')) {
                paragraph.innerHTML = '<strong>Svenska:</strong> ' + display_entry.swedishLemma;
            } else if (paragraph.textContent.includes('Inflections')) {
                paragraph.innerHTML = '<strong>Böjningar:</strong> ' + display_entry.swedishInflections.join(', ');
            } else if (paragraph.textContent.includes('English')) {
                paragraph.innerHTML = '<strong>Engelska:</strong> ' + display_entry.englishLemma;
            } else if (paragraph.textContent.includes('Inflections')) {
                paragraph.innerHTML = '<strong>Böjningar:</strong> ' + display_entry.englishInflections.join(', ');
            } else if (paragraph.textContent.includes('Part-of-speech')) {
                paragraph.innerHTML = '<strong>Ordklass:</strong> ' + posMapSwedish[display_entry.pos];
            } else if (paragraph.textContent.includes('Alternative translations')) {
                paragraph.innerHTML = '<strong>Alternativa översättningar:</strong> ' + display_entry.alternativeTranslations.join(', ');
            }else if (paragraph.textContent.includes('No search results found!')) {
                paragraph.innerHTML = '<strong>Inga sökresultat!</strong>';
            }else if (paragraph.textContent.includes('Could not reach KARP!')) {
                paragraph.innerHTML = '<strong>Kunde inte nå KARP!</strong>';
            }
        });
        const similarSearchHeader = document.getElementById('search-results');
        const header = similarSearchHeader.querySelectorAll('h2');
        header.innerHTML = 'Sökträffar:';
    }
};

// Function for switching language, called when user presses the language toggle icon
const language_toggle = () => {
    const languageToggle = document.getElementById('language-toggle');
    if (languageToggle.alt === 'swe') {
        switchToSwedish();
        language = 'swe';
        languageToggle.alt = 'eng';
    } else {
        switchToEnglish();
        language = 'eng';
        languageToggle.alt = 'swe';
    }
}