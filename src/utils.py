# Third-part libraries
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import requests
from lemminflect import getAllInflections

# path to save nltk-data
nltk.data.path.append("./nltk_data")
nltk.download("wordnet", download_dir="./nltk_data")
nltk.download("brown", download_dir="./nltk_data")
nltk.download("universal_tagset", download_dir="./nltk_data")
nltk.download("averaged_perceptron_tagger", download_dir="./nltk_data")
nltk.download("omw-1.4", download_dir="./nltk_data")
nltk.download("punkt", download_dir="./nltk_data")

lemmatizer = WordNetLemmatizer()
wordtags = nltk.ConditionalFreqDist(
    (w.lower(), t) for w, t in nltk.corpus.brown.tagged_words(tagset="universal")
)


# Function for lemmatizing english terms based on the term and Part-of-Speech using the WordNetLemmatizer
def english_lemmatizer(term, single_pos, long_pos):
    # Check for single or multiple terms
    if len(term.split(" ")) == 1:
        pos = single_pos.lower()
        # convert pos to expected convention
        if pos == "ab":
            pos = "r"
        return lemmatizer.lemmatize(term, pos)
    else:
        # Extract the POS of the last word
        last_tag = long_pos.split(" ")[-1]
        words = term.split(" ")
        # If the last word is a plural noun
        if last_tag == "NNS":
            # Lemmatize the last word
            lemmatized_word = lemmatizer.lemmatize(words[-1], "n")
            # use the lemmatized last word
            words[-1] = lemmatized_word
            return " ".join(words)
        else:
            return term


# English part-of-speech tagger
def english_pos(term):
    tokenized_words = word_tokenize(term)
    pos_tags = nltk.pos_tag(tokenized_words)
    pos_tags = " ".join([pos_tag[1] for pos_tag in pos_tags])
    return pos_tags


# Function to check if every word in the term exists in the brown corpus
def is_word_in_english(term):
    # Split the term into words
    words = term.split(" ")

    # Iterate over the words checking if exists
    for word in words:
        # Check for existense
        if len(wordnet.synsets(word)) == 0:
            # If hyphenated word check the subwords separately
            if "-" in word:
                subwords = word.split("-")
                if (
                    len(wordnet.synsets(subwords[0])) == 0
                    or len(wordnet.synsets(subwords[1])) == 0
                ):
                    return False
            else:
                return False
    # all words exist
    return True


def convert_to_simple_pos(terms):
    terms = terms.split(" ")
    terms = [term.split(".")[0].upper() for term in terms]
    return " ".join(terms)


# Function for getting all terms from KARP
def get_all():
    return get_all_help(0, 5000)

def get_all_help(start, size):
    url = f"https://spraakbanken4.it.gu.se/karp/v7/query/stunda?q="

    params = {"size": size, "from": start}

    # Make the GET request
    response = requests.get(url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Print the response content
        response = response.json()

        if response["total"] > (start+size):
            return response["hits"] + get_all_help(start+size, size)
        else:
            return response["hits"]
    else:
        print("Error:", response.status_code)
        return []
    pass

# Function for adding an entry to KARP by means of an API-key
def add_entry_via_api_key(api_key, entry, verbose=False):
    url = "https://spraakbanken4.it.gu.se/karp/v7/entries/stunda"

    headers = {
        "Content-Type": "application/json",
    }

    data = {"entry": entry, "message": ""}

    params = {"api_key": api_key}

    response = requests.put(url, headers=headers, json=data, params=params)

    if response.status_code == 201:
        if verbose:
            print("successfull add")
        return response.json()["newID"]
    else:
        if verbose:
            print("unsuccessfull add", response.status_code, response)
        return None


# Function for updating an entry to KARP by means of an API-key
def update_posts_via_api_key(id, entry, version, api_key, verbose=False):
    url = f"https://spraakbanken4.it.gu.se/karp/v7/entries/stunda/{id}"

    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }

    data = {"entry": entry, "message": "", "version": version}

    params = {"api_key": api_key}

    response = requests.post(url, headers=headers, json=data, params=params)

    if response.status_code == 200:
        if verbose:
            print("successfull update")
        return response.json()
    else:
        if verbose:
            print("unsuccessfull update", response.status_code, response)
        return None


# Function to spell-check using Skrutten Stava API
def swedish_spell_check(term):
    url = "https://skrutten.csc.kth.se/granskaapi/spell/"

    words = term.split(" ")

    if len(words) == 1:
        response = requests.get(url + "json/" + term)
    else:
        params = {"coding": "json", "words": term}

        response = requests.post(url, data=params)

    if response.status_code == 200:
        result = response.json()
        correct = True

        for i in result:
            if not i["correct"]:
                correct = False

        if len(result) == 0:
            return False
        return correct
    else:
        return None


# Function to POS tag using Skrutten API
def granska_pos(term):
    url = "https://skrutten.csc.kth.se/granskaapi/pos.php"

    params = {"coding": "json", "text": term}

    response = requests.post(url, data=params)

    if response.status_code == 200:
        result = response.json()
        pos_tags = " ".join([pos_tag["POS"] for pos_tag in result])

        return pos_tags
    else:
        return None


# Function for breaking down compound words using the Skrutten API
def split_swedish_word(term):
    url = "https://skrutten.csc.kth.se/granskaapi/compound/"

    params = {"coding": "json", "words": term}

    response = requests.post(url, data=params)

    if response.status_code == 200:
        result = response.json()
        if result[0]["parts"]:
            last_part = result[0]["parts"][0].split("|")[-1]
            beginning_list = result[0]["parts"][0].split("|")[:-1]
            beginning_part = "".join(beginning_list)
            return beginning_part, last_part
        return None, None
    else:
        return None, None


# Function for generating swedish inflections using SALDO
def get_swe_inflections(swe_lemma, second_try=False):
    url = f"https://ws.spraakbanken.gu.se/ws/karp/v4/query?q=extended||and|wf|equals|{swe_lemma}&resource=saldom"

    response = requests.get(url)

    if response.status_code == 200:
        result = response.json()

        if not result["hits"]["hits"] and not second_try:
            # time to split the word and try with the last past
            first_part, last_part = split_swedish_word(swe_lemma)
            if last_part:
                inflections = get_swe_inflections(last_part, True)
                if not type(inflections) == list:
                    return f"No inflections for {swe_lemma}"
                for inflection in inflections:
                    inflection["writtenForm"] = first_part + inflection["writtenForm"]
                return inflections
            return f"No inflections for {swe_lemma}"

        elif not result["hits"]["hits"] and second_try:
            return f"No inflections for {swe_lemma}"

        return result["hits"]["hits"][0]["_source"]["WordForms"]

    else:
        return None


# Function for getting swedish inflections for a lemma and pos
def swe_inflections(swe_lemma, pos):
    # List consisting of the verified infletctions
    verified_inflections = []
    inflections = get_swe_inflections(swe_lemma)
    # Unable to generate inflections
    if not type(inflections) == list:
        return []
    # Noun
    if pos == "N":
        for inflection in inflections:
            # Extract the plural indefinitve nomanative form
            if inflection.get("msd", "") == "pl indef nom":
                verified_inflections.append(inflection.get("writtenForm", ""))
    # Verb
    elif pos == "V":
        for inflection in inflections:
            if inflection.get("msd", "") in [
                "pres ind aktiv",
                "pret ind aktiv",
                "sup aktiv",
            ]:
                verified_inflections.append(inflection.get("writtenForm", ""))
    # Adverb and Adjective
    elif pos in ["A", "Ab"]:
        for inflection in inflections:
            if inflection.get("msd", "") in [
                "pos indef sg u nom",
                "pos indef sg n nom",
                "pos indef pl nom",
            ]:
                verified_inflections.append(inflection.get("writtenForm", ""))

    # Remove hyphen and content before (yes this is weird but SALDO sometimes generates a hyphen and prefix for words when generating inflections)
    for inflection in verified_inflections:
        if "-" in inflection and not "-" in swe_lemma:
            inflection = inflection.split("-")[1]

    verified_inflections = [
        (
            inflection.split("-")[1]
            if ("-" in inflection and not "-" in swe_lemma)
            else inflection
        )
        for inflection in verified_inflections
    ]
    return verified_inflections


# Function for getting english inflections for a lemma and pos
def eng_inflections(eng_lemma, pos):
    verified_inflections = []
    # Noun
    if pos == "N":
        inflections = get_eng_inflections(eng_lemma, "NOUN")
        if "NNS" in inflections:
            verified_inflections.append(inflections.get("NNS", "")[0])
    # Verb
    elif pos == "V":
        inflections = get_eng_inflections(eng_lemma, "VERB")
        if "VBG" in inflections:
            verified_inflections.append(inflections.get("VBG", "")[0])
        if "VBN" in inflections:
            verified_inflections.append(inflections.get("VBN", "")[0])
        if "VBD" in inflections:
            verified_inflections.append(inflections.get("VBD", "")[0])
    return verified_inflections


# Function for lemmatizing a single swedish term
def swedish_lemmatizer_single_term(term):
    url = "https://skrutten.csc.kth.se/granskaapi/lemma/"

    assert len(term.split(" ")) == 1

    response = requests.get(url + "json/" + term)

    if response.status_code == 200:
        result = response.json()
        return result[0]["lemma"]
    else:
        return None


# Function for getting inflections from skrutten API
def get_inflections(term, form):
    url = "https://skrutten.csc.kth.se/granskaapi/inflect.php"

    params = {"coding": "json", "word": term, "tag": form}

    response = requests.get(url, params=params)

    return response.json()[0]["interpretations"][0]["inflections"]


# Function for lemmatizing adjective
def lemmatize_adjective(adj, form, genus):

    target_tag = f"jj.pos.{genus}.sin.ind.nom"
    inflections = get_inflections(adj, form)

    for inflection in inflections:
        if inflection.get("tag", "").strip("* ") == target_tag:
            return inflection["word"]

    # Failed to find desired form of adjective
    return None


# Function that can lemmatize swedish terms consisting of a single term or adjective followed by a noun
def advanced_swedish_lemmatizer(term, simple_pos, swedish_pos):
    if not " " in term.strip(" "):
        return swedish_lemmatizer_single_term(term), "ok"
    elif simple_pos == "JJ NN":
        noun = term.split(" ")[1]
        lemmatized_noun = swedish_lemmatizer_single_term(noun)
        genus = swedish_pos.split(" ")[1].split(".")[1]
        adj = lemmatize_adjective(term.split(" ")[0], swedish_pos.split(" ")[0], genus)

        if adj:
            return adj + " " + lemmatized_noun, "ok"
        else:
            return term, "could not lemmatize swedish adjective"
    else:
        return term, "no processing rule for swedish POS sequence"


# Function for getting possible Part-of-Speech tags for a single english term
def english_pos_single_word(word):
    return list(wordtags[word.lower()].items())


# Function for getting possible Part-of-Speech tags for a single swedish term
def swedish_pos_tagging(term):
    url = "https://skrutten.csc.kth.se/granskaapi/taggstava/"

    words = term.split(" ")

    if len(words) == 1:
        response = requests.get(url + "json/" + term)
    else:
        params = {"coding": "json", "words": term}

        response = requests.post(url, data=params)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return None


# Function for finding if there is exist an intersection between the possible swedish POS tags and english POS tags consisting of a single POS tag
def pos_agreement_term_based(swedish_term, english_term):
    # If multiple terms return Noun
    if (len(english_term.split(" ")) > 1) or (len(swedish_term.split(" ")) > 1):
        return "N"

    # Map to a unified convention
    swedish_mapping = {"nn": "N", "vb": "V", "jj": "A", "ab": "Ab", "pc": "P"}

    english_mapping = {
        "NOUN": "N",
        "VERB": "V",
        "ADJ": "A",
        "X": "X",
        "ADV": "Ab",
        "PRT": "P",
        "NUM": "NUM",
    }

    # Create a set of swedish tags
    swedish_pos_tags = set(
        [
            swedish_mapping.get(tag.split(".")[0], "?")
            for tag in swedish_pos_tagging(swedish_term)[0]["tags"]
        ]
    )

    # Create a set of english tags
    english_pos_tags = set(
        [
            english_mapping.get(tag[0], "?")
            for tag in english_pos_single_word(english_term)
        ]
    )

    # Take the intersection
    tag = swedish_pos_tags.intersection(english_pos_tags)

    # Single POS - success
    if len(tag) == 1:
        return tag.pop()
    # No POS
    elif len(tag) == 0:
        return "no pos found"
    # More than one POS
    else:
        tags_as_string = " ".join(list(tag))
        return f"too many possible pos tags: {tags_as_string}"


# Function for getting english inflections using Lemminflect
def get_eng_inflections(eng_lemma, tag):
    # print(getInflection("be", tag="VBD"))
    # Nouns: NNS
    # Verbs: VBG, VBN, VBD
    # Adjective:
    return getAllInflections(eng_lemma, upos=tag)
