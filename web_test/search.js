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

async function swedishSearch(searchString) {
  let matches = await getTermsFromKarp("swe.lemma", "startswith", searchString);
  
  const entries = {};

  matches.hits.forEach(hit => {
      const key = hit.entry.swe.lemma + ";" + hit.entry.pos;
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
          entries[key].alternativeTranslations.push(hit.entry.eng.lemma);
      }
    });

    // Convert the object back to an array
    let sortedEntries = Object.values(entries);

    // Sort to prioritize the exact match
    sortedEntries.sort((a, b) => {
        if (a.swedishLemma === searchString && b.swedishLemma !== searchString) {
            return -1;
        } else if (a.swedishLemma !== searchString && b.swedishLemma === searchString) {
            return 1;
        }
        return 0;
    });
    console.log("search matches");
    console.log(sortedEntries);
    return sortedEntries;
}


let last_get_request_result = {}

let last_get_similar_words_result = {};

let language = 'swe';

let switched_view = 'no';

let done_search = 'no';

let new_best_result = last_get_request_result;

const displayNoResultsMessage = () => {
    const searchResultsContainer = document.getElementById("best-search-result");
    // Clear the container
    searchResultsContainer.innerHTML = "";

    // Create a new paragraph element
    const messageParagraph = document.createElement("p");
    messageParagraph.textContent = "We don't have that word, make a new search";

    // Append the message paragraph to the search results container
    searchResultsContainer.appendChild(messageParagraph);
};


const getResults = (word, search_language) => {
    // search_language is either "both", "eng" or "swe"
    done_search = 'yes';

    if (search_language === "swe") {
        let result = swedishSearch(word);
        console.log("results_gotten");
        console.log(result);
        
        let best = result[0];
        result.shift();

        last_get_request_result = best;

        console.log("before_best_result");

        display_best_result(last_get_request_result);

        console.log("displayed_best_result");

        last_get_similar_words_result = result;

        display_similar_results();

        console.log("displayed_similar_result");
    }
    else if (search_language === "eng") {
        let result = swedishSearch(word);
        console.log("results_gotten");
        let best = result[0];
        result.shift();

        last_get_request_result = best;

        console.log("before_best_result");

        display_best_result(last_get_request_result);

        console.log("displayed_best_result");

        last_get_similar_words_result = result;

        display_similar_results();

        console.log("displayed_similar_result");
    }
    else {
        let result = swedishSearch(word);
        console.log("results_gotten");

        let best = result.shift();

        last_get_request_result = best;

        console.log("before_best_result");

        display_best_result(last_get_request_result);

        console.log("displayed_best_result");

        last_get_similar_words_result = result;

        display_similar_results();

        console.log("displayed_similar_result");
    }

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

async function get_best_result (word) {
    // TODO: replace below with get request stuff for best word
    best_word_result = await getLemmaByLanguageExactMatch('swe', word);
    best_word_result = best_word_result[0];

    last_get_request_result = best_word_result; // update global variable for further use

    display_best_result(last_get_request_result);
}

const handle_button_parsing = (string_data) => {
    const data = JSON.parse(string_data);
    new_best_result = data;
    switched_view = 'yes';
    display_best_result(data);
}

const display_best_result = (data) => {
    console.log(data);
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
    if (language === 'swe') {
        // Paragraphs for left section
        create_paragraph("Sve", data.swedishLemma, leftSection, true);
        create_paragraph("Böjningar", data.swedishInflections, leftSection);

        // Paragraphs for right section
        create_paragraph("Eng", data.englishLemma, rightSection, true);
        create_paragraph("Böjningar", data.englishInflections, rightSection);

        create_paragraph("Ordklass", data.pos, bottomSection);
        create_paragraph("Alternativa översättningar", data.alternativeTranslations, bottomSection);

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
        create_paragraph("Inflections", data.swedishInflections, leftSection);

        // Paragraphs for right section
        create_paragraph("Eng", data.englishLemma, rightSection, true);
        create_paragraph("Inflections", data.englishInflections, rightSection);

        create_paragraph("Part-of-speech", data.pos, bottomSection);
        create_paragraph("Alternative translations", data.alternativeTranslations, bottomSection);

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

async function get_similar_results(word) {
    // TODO: replace below with get request stuff for similar words
    similar_words_result = await getLemmaByLanguageBeginsWith('swe', word);
    last_get_similar_words_result = similar_words_result;

    display_similar_results();
}

const display_similar_results = () => {
    similar_words_result = last_get_similar_words_result;
    similar_words_container = document.getElementById("search-results");
    // Clear the container so we don't append the same results multiple times
    similar_words_container.innerHTML = "";

    const header = document.createElement("h2");
    header.innerHTML = language === 'swe' ? "Sökträffar:" : "Search results:";
    similar_words_container.appendChild(header);

    for (word in similar_words_result) {
        create_button("sv", similar_words_result[word], similar_words_container);
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

const create_button = (language, data, container) => {
    const button = document.createElement("button");
    button.innerHTML = `${language}: ${data.swedishLemma} (${data.pos})`;
    button.setAttribute("onclick", `handle_button_parsing('${JSON.stringify(data)}')`);
    container.appendChild(button);
}

// Logic for enter on the keyboard and not just pressing "sök"
document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById("search-input");

    // Add event listener for the "keydown" event on the input field
    searchInput.addEventListener("keydown", function(event) {
        // Check if the pressed key is "Enter" (key code 13)
        if (event.keyCode === 13) {
            // Prevent the default action of the "Enter" key (form submission)
            event.preventDefault();
            // Call the getResults function with the input value
            getResults(searchInput.value);
        }
    });
});

// Function to change text content to English
const switchToEnglish = () => {
    // Change logo text
    document.querySelector('.logo-main').textContent = 'STUNDA - ';
    document.querySelector('.logo-sub').textContent = 'Swedish Technical University Network for Data Terms';
    
    // Change info text
    document.querySelector('.info-text p').textContent = 'Stunda is a network for Sweden\'s technical universities aimed at promoting efficient technical communication in Swedish within higher education, primarily by working with discipline-specific terminology.';
    
    // Change button text
    document.querySelector('.search-button').textContent = 'Search';

    // Change placeholder text
    document.getElementById('search-input').setAttribute('placeholder', 'Data term...');

    // Change dropdown text
    document.querySelector('.both').textContent = 'Both';
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

        if (switched_view === 'yes') {
            show = new_best_result;
        } else {
            show = last_get_request_result;
        }
        paragraphs.forEach(paragraph => {
            // Translate each paragraph content
            if (paragraph.textContent.includes('Sve')) {
                paragraph.innerHTML = '<strong>Swe:</strong> ' + show.swedishLemma;
            } else if (paragraph.textContent.includes('Böjningar')) {
                paragraph.innerHTML = '<strong>Inflections:</strong> ' + show.swedishInflections.join(', ');
            } else if (paragraph.textContent.includes('Eng')) {
                paragraph.innerHTML = '<strong>Eng:</strong> ' + show.englishLemma;
            } else if (paragraph.textContent.includes('Böjningar')) {
                paragraph.innerHTML = '<strong>Inflections:</strong> ' + show.englishInflections.join(', ');
            } else if (paragraph.textContent.includes('Ordklass')) {
                paragraph.innerHTML = '<strong>Part-of-speech:</strong> ' + show.pos;
            } else if (paragraph.textContent.includes('Alternativa översättningar')) {
                paragraph.innerHTML = '<strong>Alternative translations:</strong> ' + show.alternativeTranslations.join(', ');
            } else if (paragraph.textContent.includes('Källor')) {
                paragraph.innerHTML = '<strong>Sources:</strong> ' + show.source.join(', ');
            }else if (paragraph.textContent.includes('Källa')) {
                paragraph.innerHTML = '<strong>Source:</strong> ' + show.source;
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
    document.querySelector('.logo-main').textContent = 'STUNDA - ';
    document.querySelector('.logo-sub').textContent = 'Sveriges Tekniska Universitets Nätverk för Datatermer';

    // Change info text
    document.querySelector('.info-text p').textContent = 'Stunda är ett nätverk för Sveriges tekniska universitet med syfte att verka för effektiv fackspråklig kommunikation på svenska inom högre utbildning, främst genom att arbeta med disciplinspecifik terminologi.';
    
    // Change button text
    document.querySelector('.search-button').textContent = 'Sök';

    // Change placeholder text
    document.getElementById('search-input').setAttribute('placeholder', 'Dataterm...');

    // Change dropdown text
    document.querySelector('.both').textContent = 'Båda';
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
        
        if (switched_view === 'yes') {
            show = new_best_result;
        } else {
            show = last_get_request_result;
        }
        paragraphs.forEach(paragraph => {
            // Translate each paragraph content
            if (paragraph.textContent.includes('Swe')) {
                paragraph.innerHTML = '<strong>Sve:</strong> ' + show.swedishLemma;
            } else if (paragraph.textContent.includes('Inflections')) {
                paragraph.innerHTML = '<strong>Böjningar:</strong> ' + show.swedishInflections.join(', ');
            } else if (paragraph.textContent.includes('Eng')) {
                paragraph.innerHTML = '<strong>Eng:</strong> ' + show.englishLemma;
            } else if (paragraph.textContent.includes('Inflections')) {
                paragraph.innerHTML = '<strong>Böjningar:</strong> ' + show.englishInflections.join(', ');
            } else if (paragraph.textContent.includes('Part-of-speech')) {
                paragraph.innerHTML = '<strong>Ordklass:</strong> ' + show.pos;
            } else if (paragraph.textContent.includes('Alternative translations')) {
                paragraph.innerHTML = '<strong>Alternativa översättningar:</strong> ' + show.alternativeTranslations.join(', ');
            } else if (paragraph.textContent.includes('Sources')) {
                paragraph.innerHTML = '<strong>Källor:</strong> ' + show.source.join(', ');
            }else if (paragraph.textContent.includes('Source')) {
                paragraph.innerHTML = '<strong>Källa:</strong> ' + show.source;
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