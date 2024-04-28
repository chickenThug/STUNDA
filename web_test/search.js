function getTermsFromKarp(field, query_mode, searchString) {
    // Format the search string into the URL
    const apiUrl = `https://spraakbanken4.it.gu.se/karp/v7/query/stunda?q=and(or(${query_mode}|${field}|"${searchString}"))&from=0&size=25`;

    // Make the GET request using fetch()
    return fetch(apiUrl)
      .then(response => {
        // Check if the response is OK (status code 200)
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        // Parse the JSON response
        return response.json();
      })
      .then(data => {
        const dataList = [];
        data.hits.forEach(hit => {

            const new_entry = {
                id: hit.id,
                swedishLemma: hit.entry.swe.lemma,
                englishLemma: hit.entry.eng.lemma,
                source: [hit.entry.src],
                pos: [hit.entry.pos],
                swedishInflections: hit.entry.swe.inflection ?? [],
                englishInflections: hit.entry.eng.inflection ?? [],
                alternativeTranslations: hit.entry.synonyms ?? []
            }

            dataList.push(new_entry);
          });
        return dataList;
      })
      .catch(error => {
        // Handle any errors that occur during the fetch
        console.error('There was a problem with the fetch operation:', error);
        return [];
      });
  }

function getLemmaByLanguageExactMatch(language, searchString) {
  const field = `${language}.lemma`
  return getTermsFromKarp(field, "equals", searchString)
}

function getLemmaByLanguageBeginsWith(language, searchString) {
  const field = `${language}.lemma`
  return getTermsFromKarp(field, "startswith", searchString)
}

function mergeResults(firstResultList, secondResultList) {
  const uniqueResults = new Map();

    // Add each item from the first result list to the Map
    firstResultList.forEach(item => {
        uniqueResults.set(item.id, item);
    });

    // Add each item from the second result list to the Map
    // This will automatically overwrite any duplicate ids from the first list
    secondResultList.forEach(item => {
        uniqueResults.set(item.id, item);
    });

    // Convert the Map values back to an array and return
    return Array.from(uniqueResults.values());
}

async function tryMerge() {
  let language = "swe";
  let searchString = "test";
  let query_mode = "startswith";
  let result1 = null;
  let result2 = null;
  try {
        result1 = await getLemmaByLanguageExactMatch(language, searchString);
        // You can now use 'result' here for further processing or return it
    } catch (error) {
        console.error('Error fetching data:', error);
    }

    try {
      result2 = await getLemmaByLanguageBeginsWith(language, searchString);
      // You can now use 'result' here for further processing or return it
  } catch (error) {
      console.error('Error fetching data:', error);
  }
  console.log(mergeResults(result1, result2));
}

let last_get_request_result = {}

let last_get_similar_words_result = {};

let language = 'swe';

let switched_view = 'no';

let done_search = 'no';

let new_best_result = last_get_request_result;

const getResults = (word) => {
    done_search = 'yes';
    get_best_result(word);
    get_similar_results(word);

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

    console.log("GET BEST RESULT");
    console.log(best_word_result);

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
    best_word_container = document.getElementById("best-search-result");
    // Clear the container so we don't append the same results multiple times
    best_word_container.innerHTML = "";

    console.log("DATA");
    console.log(data);

    // Create divs to contain different sections
    const leftSection = document.createElement("div");
    leftSection.classList.add("left-section");

    const rightSection = document.createElement("div");
    rightSection.classList.add("right-section");

    const bottomSection = document.createElement("div");
    bottomSection.classList.add("bottom-section");
    if (language === 'swe') {
        // Paragraphs for left section
        create_paragraph("Svenskt lemma", data.swedishLemma, leftSection);
        create_paragraph("Svenska böjningar", data.swedishInflections, leftSection);

        // Paragraphs for right section
        create_paragraph("Engelskt lemma", data.englishLemma, rightSection);
        create_paragraph("Engelska böjningar", data.englishInflections, rightSection);

        create_paragraph("Ordklass", data.pos, bottomSection);
        create_paragraph("Alternativa översättningar", data.alternativeTranslations, bottomSection);

        // Paragraphs for bottom section
        // Logic for switching between källor and källa

        console.log("data source");
        console.log(data.source);

        if (data.source.length === 1) {
            create_paragraph("Källa", data.source, bottomSection)
        } else {
            create_paragraph("Källor", data.source, bottomSection)
        }
    } else {
        // Paragraphs for left section
        create_paragraph("Swedish lemma", data.swedishLemma, leftSection);
        create_paragraph("Swedish inflections", data.swedishInflections, leftSection);

        // Paragraphs for right section
        create_paragraph("English lemma", data.englishLemma, rightSection);
        create_paragraph("English inflections", data.englishInflections, rightSection);

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

    console.log("similar words result");
    console.log(similar_words_result);

    display_similar_results();
}

const display_similar_results = () => {
    similar_words_result = last_get_similar_words_result;
    console.log("FEL HÄR??")
    console.log(similar_words_result);
    similar_words_container = document.getElementById("search-results");
    // Clear the container so we don't append the same results multiple times
    similar_words_container.innerHTML = "";

    const header = document.createElement("h2");
    header.innerHTML = language === 'swe' ? "Sökträffar:" : "Search results:";
    similar_words_container.appendChild(header);

    create_button("sv", last_get_request_result, similar_words_container);

    for (word in similar_words_result) {
        console.log("WOOOOOOORD");
        console.log(word);
        create_button("sv", similar_words_result[word], similar_words_container);
    }
}

const create_paragraph = (title, value, container) => {
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
    document.getElementById('search-input').setAttribute('placeholder', 'Swedish or English data term');

    if (done_search === 'yes') {
        // Change header text
        document.querySelector('#search-results h2').textContent = 'Search results:';

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
            if (paragraph.textContent.includes('Svenskt lemma')) {
                paragraph.innerHTML = '<strong>Swedish lemma:</strong> ' + show.swedishLemma;
            } else if (paragraph.textContent.includes('Svenska böjningar')) {
                paragraph.innerHTML = '<strong>Swedish inflections:</strong> ' + show.swedishInflections.join(', ');
            } else if (paragraph.textContent.includes('Engelskt lemma')) {
                paragraph.innerHTML = '<strong>English lemma:</strong> ' + show.englishLemma;
            } else if (paragraph.textContent.includes('Engelska böjningar')) {
                paragraph.innerHTML = '<strong>English inflections:</strong> ' + show.englishInflections.join(', ');
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
    document.getElementById('search-input').setAttribute('placeholder', 'Svensk eller engelsk dataterm');

    if (done_search === 'yes'){
        // Change header text
        document.querySelector('#search-results h2').textContent = 'Sökträffar:';

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
            if (paragraph.textContent.includes('Swedish lemma')) {
                paragraph.innerHTML = '<strong>Svenskt lemma:</strong> ' + show.swedishLemma;
            } else if (paragraph.textContent.includes('Swedish inflections')) {
                paragraph.innerHTML = '<strong>Svenska böjningar:</strong> ' + show.swedishInflections.join(', ');
            } else if (paragraph.textContent.includes('English lemma')) {
                paragraph.innerHTML = '<strong>Engelskt lemma:</strong> ' + show.englishLemma;
            } else if (paragraph.textContent.includes('English inflections')) {
                paragraph.innerHTML = '<strong>Engelska böjningar:</strong> ' + show.englishInflections.join(', ');
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