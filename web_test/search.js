const best_word = {
    swedishLemma: "swedish_word1",
    englishLemma: "english_word1",
    source: ["source1", "source2"],
    pos: ["N"],
    swedishInflections: ["swedish_inflection1", "swedish_inflection2"],
    englishInflections: ["english_inflection1", "english_inflection2"],
    alternativeTranslations: ["hej", "hejsan"]
}

let last_get_request_result = {}

const similar_words = {
    word1: {
        swedishLemma: "swedish_word2",
        englishLemma: "english_word2",
        source: ["source2"],
        pos: ["N"],
        swedishInflections: ["swedish_inflection3", "swedish_inflection4"],
        englishInflections: ["english_inflection3", "english_inflection4"],
        alternativeTranslations: ["hej", "hejsan"]
    },
    word2: {
        swedishLemma: "swedish_word3",
        englishLemma: "english_word3",
        source: ["source4", "source5", "source7"],
        pos: ["V"],
        swedishInflections: ["swedish_inflection5", "swedish_inflection6"],
        englishInflections: ["english_inflection5", "english_inflection6"],
        alternativeTranslations: ["hej2", "hejsan2"]
    },
    word3: {
        swedishLemma: "swedish_word4",
        englishLemma: "english_word4",
        source: ["source7"],
        pos: ["Adj"],
        swedishInflections: ["swedish_inflection7", "swedish_inflection8"],
        englishInflections: ["english_inflection7", "english_inflection8"],
        alternativeTranslations: ["hej3", "hejsan3"]
    },
    word4: {
        swedishLemma: "swedish_word5",
        englishLemma: "english_word5",
        source: ["source8", "source9"],
        pos: ["Adv"],
        swedishInflections: ["swedish_inflection9", "swedish_inflection10"],
        englishInflections: ["english_inflection9", "english_inflection10"],
        alternativeTranslations: ["hej4", "hejsan4"]
    },
};

let last_get_similar_words_result = {};

const getResults = (word) => {
    get_best_result(word);
    get_similar_results(word);

    // Show the search result containers
    document.getElementById("search-results").style.display = "block";
    document.getElementById("best-search-result").style.display = "block";
};

const get_best_result = (word) => {
    // TODO: replace below with get request stuff for best word
    best_word_result = best_word; // make get request for best word
    last_get_request_result = best_word_result; // update global variable for further use

    display_best_result(last_get_request_result);
}

const handle_button_parsing = (string_data) => {
    const data = JSON.parse(string_data);
    display_best_result(data);
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

    // Paragraphs for left section
    create_paragraph("Svenskt lemma", data.swedishLemma, leftSection);
    create_paragraph("Svenska böjningar", data.swedishInflections, leftSection);

    // Paragraphs for right section
    create_paragraph("Engelskt lemma", data.englishLemma, rightSection);
    create_paragraph("Engelska böjningar", data.englishInflections, rightSection);

    // Paragraphs for bottom section
    // Logic for switching between källor and källa
    if (data.source.length === 1) {
        create_paragraph("Källa", data.source, bottomSection)
    } else {
        create_paragraph("Källor", data.source, bottomSection)
    }
    create_paragraph("POS", data.pos, bottomSection);
    create_paragraph("Alternativa översättningar", data.alternativeTranslations, bottomSection);

    // Append sections to container
    best_word_container.appendChild(leftSection);
    best_word_container.appendChild(rightSection);
    best_word_container.appendChild(bottomSection);
}

const get_similar_results = () => {
    // TODO: replace below with get request stuff for similar words
    similar_words_result = similar_words; // make get request for similar words
    last_get_similar_words_result = similar_words_result;

    display_similar_results();
}

const display_similar_results = () => {
    similar_words_result = last_get_similar_words_result;
    similar_words_container = document.getElementById("search-results");
    // Clear the container so we don't append the same results multiple times
    similar_words_container.innerHTML = "";

    const header = document.createElement("h2");
    header.innerHTML = "Sökträffar:"
    similar_words_container.appendChild(header);

    create_button("sv", last_get_request_result, similar_words_container);

    for (word in similar_words_result) {
        create_button("sv", similar_words_result[word], similar_words_container);
    }
}

const create_paragraph = (title, value, container) => {
    const paragraph = document.createElement("p");
    paragraph.innerHTML = `<strong>${title}:</strong> ${value}`; 
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
