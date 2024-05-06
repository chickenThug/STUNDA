function getTermsFromKarp(field, query_mode, searchString) {
    // Format the search string into the URL
    const apiUrl = `https://spraakbanken4.it.gu.se/karp/v7/query/stunda?q=and(or(${query_mode}|${field}|"${searchString}"))&from=0&size=100`;
    // Make the GET request using fetch()
    return fetch(apiUrl)
      .then(response => {
        // Check if the response is OK (status code 200)
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .catch(error => {
        // Handle any errors that occur during the fetch
        console.error('There was a problem with the fetch operation:', error);
        return [];
      });
}

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

    const entries = {};
    console.log("before");
    matches.hits.forEach(hit => {
        const key = hit.entry[language].lemma + ";" + hit.entry.pos;
        if (!entries[key]) {
            // If the lemma doesn't exist in entries, create a new entry
            entries[key] = {
                id: hit.id,
                swedishLemma: hit.entry.swe.lemma,
                englishLemma: hit.entry.eng.lemma,
                source: hit.entry.src.split(", "),
                pos: [hit.entry.pos],
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
      console.log(sortedEntries);
      return sortedEntries;
  }


let display_entry = {}

let last_get_similar_words_result = {};

let language = 'swe';

let switched_view = 'no';

let done_search = 'no';

let new_best_result = display_entry;

const getResults = async (word, search_language) => {
    done_search = 'yes';

    let result = await search(search_language, word);

    if (result.length == 0) {
        display_no_result();
        return
    }

    let best = result.shift();

    display_entry = best;

    display_best_result(display_entry);

    last_get_similar_words_result = result;

    display_similar_results(search_language);

    // Show the search result containers
    document.getElementById("search-results").style.display = "block";
    document.getElementById("best-search-result").style.display = "block";

    // Update display language if the toggle button has been clicked
    if (language === 'eng') {
        switchToEnglish();
    } else {
        switchToSwedish();
    }
};

const handle_button_parsing = (string_data) => {
    const data = JSON.parse(string_data);
    display_entry = data;
    display_best_result(display_entry);
}

function display_no_result() {
    // Clear results
    document.getElementById("search-results").style.display = "none";

    best_word_container = document.getElementById("best-search-result");
    // Clear the container so we don't append the same results multiple times
    best_word_container.innerHTML = "";

    const rightSection = document.createElement("div");
    rightSection.classList.add("bottom-section");
    const paragraph = document.createElement("p");

    if (language === "swe") {
        paragraph.innerHTML = "<strong>Inga sökresultat!</strong>";
    }
    else {
        paragraph.innerHTML = "<strong>No search results found!</strong>";
    }
    paragraph.classList.add("nores");
    best_word_container.appendChild(paragraph);

    document.getElementById("best-search-result").style.display = "block";
}

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

    console.log("data");
    console.log(data);
    if (language === 'swe') {
        
        // Paragraphs for left section
        create_paragraph("Sve", data.swedishLemma, leftSection, true);
        if (data.swedishInflections.length !== 0){
            create_paragraph("Böjningar", data.swedishInflections, leftSection);
        }

        // Paragraphs for right section
        create_paragraph("Eng", data.englishLemma, rightSection, true);
        if (data.englishInflections.length !== 0){
            create_paragraph("Böjningar", data.englishInflections, rightSection);
        }

        create_paragraph("Ordklass", data.pos, bottomSection);
        if (data.alternativeTranslations.length !== 0){
            create_paragraph("Alternativa översättningar", data.alternativeTranslations, bottomSection);
        }

        // Paragraphs for bottom section
        // Logic for switching between källor and källa

        if (data.source.length === 1) {
            create_paragraph("Källa", data.source, bottomSection)
        } else {
            create_paragraph("Källor", data.source, bottomSection)
        }
    } else {
        // Paragraphs for left section
        create_paragraph("Swe", data.swedishLemma, leftSection, true);
        if (data.swedishInflections.length !== 0){
            create_paragraph("Inflections", data.swedishInflections, leftSection);
        }

        // Paragraphs for right section
        create_paragraph("Eng", data.englishLemma, rightSection, true);
        if (data.englishInflections.length !== 0){
            create_paragraph("Inflections", data.englishInflections, rightSection);
        }

        create_paragraph("Part-of-speech", data.pos, bottomSection);
        if (data.alternativeTranslations.length !== 0){
            create_paragraph("Alternative translations", data.alternativeTranslations, bottomSection);
        }

        // Paragraphs for bottom section
        // Logic for switching between källor and källa
        if (data.source.length === 1) {
            create_paragraph("Source", data.source, bottomSection)
        } else {
            create_paragraph("Sources", data.source, bottomSection)
        }
    }

    // Append sections to container
    best_word_container.appendChild(leftSection);
    best_word_container.appendChild(rightSection);
    best_word_container.appendChild(bottomSection);
}

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

const create_button = (data, container, language) => {
    const button = document.createElement("button");
    if (language === "swe"){
        button.innerHTML = `${data.swedishLemma} (${data.pos})`;
    } else {
        button.innerHTML = `${data.englishLemma} (${data.pos})`;
    }
    button.setAttribute("onclick", `handle_button_parsing('${JSON.stringify(data)}')`);
    container.appendChild(button);
}

// Logic for enter on the keyboard and not just pressing "sök"
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
    // Change logo text
    document.querySelector('.logo-main').textContent = 'STUNDA';
    document.querySelector('.logo-sub').textContent = 'Swedish Technical University Network for Data Terms';
    
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

    if (done_search === 'yes') {
        // Change header text
        const searchResultsHeader = document.querySelector('#search-results h2');
        if (searchResultsHeader) {
            searchResultsHeader.textContent = 'Search results:';
        }

        // Translate content within best-search-result
        const bestSearchResult = document.getElementById('best-search-result');
        const paragraphs = bestSearchResult.querySelectorAll('p');

        paragraphs.forEach(paragraph => {
            // Translate each paragraph content
            if (paragraph.textContent.includes('Sve')) {
                paragraph.innerHTML = '<strong>Swe:</strong> ' + display_entry.swedishLemma;
            } else if (paragraph.textContent.includes('Böjningar')) {
                paragraph.innerHTML = '<strong>Inflections:</strong> ' + display_entry.swedishInflections.join(', ');
            } else if (paragraph.textContent.includes('Eng')) {
                paragraph.innerHTML = '<strong>Eng:</strong> ' + display_entry.englishLemma;
            } else if (paragraph.textContent.includes('Böjningar')) {
                paragraph.innerHTML = '<strong>Inflections:</strong> ' + display_entry.englishInflections.join(', ');
            } else if (paragraph.textContent.includes('Ordklass')) {
                paragraph.innerHTML = '<strong>Part-of-speech:</strong> ' + display_entry.pos;
            } else if (paragraph.textContent.includes('Alternativa översättningar')) {
                paragraph.innerHTML = '<strong>Alternative translations:</strong> ' + display_entry.alternativeTranslations.join(', ');
            } else if (paragraph.textContent.includes('Källor')) {
                paragraph.innerHTML = '<strong>Sources:</strong> ' + display_entry.source.join(', ');
            }else if (paragraph.textContent.includes('Källa')) {
                paragraph.innerHTML = '<strong>Source:</strong> ' + display_entry.source;
            }
            else if (paragraph.textContent.includes('Inga sökresultat!')) {
                paragraph.innerHTML = '<strong>No search results found!</strong>';
            }
        });
        const similarSearchHeader = document.getElementById('search-results');
        const header = similarSearchHeader.querySelectorAll('h2');
        header.innerHTML = 'Search results:';
    }
};

// Function to change text content to Swedish
const switchToSwedish = () => {
    // Change logo text
    document.querySelector('.logo-main').textContent = 'STUNDA';
    document.querySelector('.logo-sub').textContent = 'Sveriges Tekniska Universitets Nätverk för Datatermer';

    // Change info text
    document.querySelector('.info-text p').innerHTML = 'Stunda är ett nätverk för Sveriges tekniska universitet med syfte att verka för effektiv fackspråklig kommunikation på svenska inom högre utbildning, främst genom att arbeta med disciplinspecifik terminologi. Läs mer <a href="https://writing.chalmers.se/stunda/" target="blank">här</a>. För avancerad sökning, se <a href="https://spraakbanken.gu.se/karp/tng/?mode=stunda&lexicon=stunda&show=stunda:01GX3DS1AKX7YZVYR6F5V8VZS6">KARP</a>.';
    
    // Change button text
    document.querySelector('.search-button').textContent = 'Sök';

    // Change placeholder text
    document.getElementById('search-input').setAttribute('placeholder', 'Dataterm...');

    // Change dropdown label text
    document.querySelector('.search-options label').textContent = "Sökspråk:";

    // Change dropdown text
    document.querySelector('.swe').textContent = 'Svenska';
    document.querySelector('.eng').textContent = 'Engelska';

    if (done_search === 'yes'){
        // Change header text
        const searchResultsHeader = document.querySelector('#search-results h2');
        if (searchResultsHeader) {
            searchResultsHeader.textContent = 'Sökträffar:';
        }

        // Translate content within best-search-result
        const bestSearchResult = document.getElementById('best-search-result');
        const paragraphs = bestSearchResult.querySelectorAll('p');
        
        paragraphs.forEach(paragraph => {
            // Translate each paragraph content
            if (paragraph.textContent.includes('Swe')) {
                paragraph.innerHTML = '<strong>Sve:</strong> ' + display_entry.swedishLemma;
            } else if (paragraph.textContent.includes('Inflections')) {
                paragraph.innerHTML = '<strong>Böjningar:</strong> ' + display_entry.swedishInflections.join(', ');
            } else if (paragraph.textContent.includes('Eng')) {
                paragraph.innerHTML = '<strong>Eng:</strong> ' + display_entry.englishLemma;
            } else if (paragraph.textContent.includes('Inflections')) {
                paragraph.innerHTML = '<strong>Böjningar:</strong> ' + display_entry.englishInflections.join(', ');
            } else if (paragraph.textContent.includes('Part-of-speech')) {
                paragraph.innerHTML = '<strong>Ordklass:</strong> ' + display_entry.pos;
            } else if (paragraph.textContent.includes('Alternative translations')) {
                paragraph.innerHTML = '<strong>Alternativa översättningar:</strong> ' + display_entry.alternativeTranslations.join(', ');
            } else if (paragraph.textContent.includes('Sources')) {
                paragraph.innerHTML = '<strong>Källor:</strong> ' + display_entry.source.join(', ');
            }else if (paragraph.textContent.includes('Source')) {
                paragraph.innerHTML = '<strong>Källa:</strong> ' + display_entry.source;
            }else if (paragraph.textContent.includes('No search results found!')) {
                paragraph.innerHTML = '<strong>Inga sökresultat!</strong>';
            }
        });
        const similarSearchHeader = document.getElementById('search-results');
        const header = similarSearchHeader.querySelectorAll('h2');
        header.innerHTML = 'Sökträffar:';
    }
};

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