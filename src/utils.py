import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import requests
import pandas as pd
from lemminflect import getAllInflections, getInflection

# nltk.download("wordnet")
# nltk.download("brown")
# nltk.download("universal_tagset")
# nltk.download("averaged_perceptron_tagger")

lemmatizer = WordNetLemmatizer()
wordtags = nltk.ConditionalFreqDist(
    (w.lower(), t) for w, t in nltk.corpus.brown.tagged_words(tagset="universal")
)


def english_lemmatizer(term, pos_tags):
    pos_tags = pos_tags.split(" ")

    # Lemmatize single word
    if len(pos_tags) == 1:
        pos_tag = pos_tags[0]
        if pos_tag in ["NN", "NNS"]:  # Lemmatize noun
            return lemmatizer.lemmatize(term, "n"), "lemmatized"
        elif pos_tag in ["VBZ", "VBP", "VBN", "VBG", "VBD", "VB"]:  # Lemmatize verb
            return lemmatizer.lemmatize(term, "v"), "lemmatized"
        elif pos_tag in ["JJR", "JJS", "JJ"]:
            return lemmatizer.lemmatize(term, "a"), "lemmatized"  # Lemmatize adjective
        elif pos_tag in ["RBS", "RB", "RBR"]:
            return lemmatizer.lemmatize(term, "r"), "lemmatized"  # Lemmatize adverb
        else:
            return term, "unknown english single pos tag"
    else:
        last_tag = pos_tags[-1]
        words = term.split(" ")
        if last_tag == "NNS":
            lemmatized_word = lemmatizer.lemmatize(words[-1], "n")
            words[-1] = lemmatized_word
            return " ".join(words), "lemmatized"
        else:
            return term, "lemmatized"


def english_lemmatizer_v2(term, single_pos, long_pos):
    if len(term.split(" ")) == 1:
        pos = single_pos.lower()
        if pos == "ab":
            pos = "r"
        return lemmatizer.lemmatize(term, pos)
    else:
        last_tag = long_pos.split(" ")[-1]
        words = term.split(" ")
        if last_tag == "NNS":
            lemmatized_word = lemmatizer.lemmatize(words[-1], "n")
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


def delete_entry_by_id(id, authorization, verbose=False):
    url = f"https://ws.spraakbanken.gu.se/ws/karp/v7/entries/stunda/{id}/1"

    headers = {
        "Authorization": "Bearer " + authorization,
        "Content-Type": "application/json",
    }

    response = requests.delete(url=url, headers=headers)

    if verbose:
        if response.status_code == 204:
            print("Succesfully deleted entry with id", id)
        else:
            print("Could not delete entry with id", id)

    return response.status_code == 204


def delete_entries_by_ids(ids, authorization, verbose=False):
    success = []
    for id in ids:
        success.append(delete_entry_by_id(id, authorization, verbose))

    return success


def get_all():
    url = f"https://ws.spraakbanken.gu.se/ws/karp/v7/query/stunda?q="

    params = {"size": 10000}

    # Make the GET request
    response = requests.get(url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Print the response content
        print("succesfull get")
        return response.json()  # Assuming the response is in JSON format
    else:
        print("Error:", response.status_code)
        return {}


def add_entry(authorization, entry, verbose=False):
    url = "https://ws.spraakbanken.gu.se/ws/karp/v7/entries/stunda"

    headers = {
        "Authorization": "Bearer " + authorization,
        "Content-Type": "application/json",
    }

    data = {"entry": entry, "message": ""}

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 201:
        if verbose:
            print("successfull add")
        return response.json()["newID"]
    else:
        if verbose:
            print("unsuccessfull add", response.status_code, response)
        return None


def add_entries(authorization, entries, verbose=False):
    results = []
    for entry in entries:
        results.append(add_entry(authorization, entry, verbose))
    return results


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


# Function to pos-tag using Skrutten Granska API
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
    
def split_swedish_word(term): # Fix for term consisting of multiple words?
    url = "https://skrutten.csc.kth.se/granskaapi/compound/"

    params = {"coding": "json", "words": term}

    response = requests.post(url, data=params)

    if response.status_code == 200:
        result = response.json()
        if result[0]['parts']:
            last_part = result[0]['parts'][0].split("|")[-1]
            beginning_list = result[0]['parts'][0].split("|")[:-1]
            beginning_part = "".join(beginning_list)
            return beginning_part, last_part
        return None, None
    else:
        return None

def get_swe_inflections(swe_lemma, tag = False):
    url = f"https://ws.spraakbanken.gu.se/ws/karp/v4/query?q=extended||and|wf|equals|{swe_lemma}&resource=saldom"

    response = requests.get(url)

    if response.status_code == 200:
        result = response.json()

        if not result['hits']['hits'] and not tag:
            # time to split the word and try with the last past
            first_part, last_part = split_swedish_word(swe_lemma)
            if last_part:
                inflections = get_swe_inflections(last_part, True)
                # here i was thinking i could do some concatenation but i dont know if that will work?? 
                for inflection in inflections:
                    inflection['writtenForm'] = first_part + inflection['writtenForm']
                return inflections
            return f"No inflections for {swe_lemma}"
        elif not result['hits']['hits'] and tag:
            return f"No inflections for {swe_lemma}"
        
        return result['hits']['hits'][0]['_source']['WordForms']
    
    else:
        return None

def get_eng_inflections(eng_lemma, tag):
    # print(getInflection('be', tag='VBD'))
    return getInflection(eng_lemma, tag = tag)

# TODO probably removes
def swedish_lemmatizing(term):
    url = "https://skrutten.csc.kth.se/granskaapi/lemma/"

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


def swedish_lemmatizer_single_term(term):
    url = "https://skrutten.csc.kth.se/granskaapi/lemma/"

    assert len(term.split(" ")) == 1

    response = requests.get(url + "json/" + term)

    if response.status_code == 200:
        result = response.json()
        return result[0]["lemma"]
    else:
        return None


def get_inflections(term, form):
    url = "https://skrutten.csc.kth.se/granskaapi/inflect.php"

    params = {"coding": "json", "word": term, "tag": form}

    response = requests.get(url, params=params)

    # print(response.status_code)

    return response.json()[0]["interpretations"][0]["inflections"]


def lemmatize_adjective(adj, form, genus):

    target_tag = f"jj.pos.{genus}.sin.ind.nom"
    inflections = get_inflections(adj, form)

    for inflection in inflections:
        if inflection.get("tag", "").strip("* ") == target_tag:
            return inflection["word"]

    # Failed to find desired form of adjective
    return None


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


def pos_agreement(swedish_pos, english_pos):
    if (len(swedish_pos.split(" ")) > 1) or (len(english_pos.split(" ")) > 1):
        return True
    eng_pos_local = "IS THIS A EASTER EGG?"
    if english_pos in ["NN", "NNS"]:
        eng_pos_local = "NN"
    elif english_pos in ["VBZ", "VBP", "VBN", "VBG", "VBD", "VB"]:
        eng_pos_local = "VB"
    elif english_pos in ["JJR", "JJS", "JJ"]:
        eng_pos_local = "JJ"
    elif english_pos in ["RBS", "RB", "RBR"]:
        eng_pos_local = "AB"

    if eng_pos_local == swedish_pos:
        return True
    else:
        return False


def english_pos_single_word(word):
    return list(wordtags[word.lower()].items())


def pos_agreement_term_based(swedish_term, english_term):
    if (len(english_term.split(" ")) > 1) or (len(swedish_term.split(" ")) > 1):
        return "N"
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

    swedish_pos_tags = set(
        [
            swedish_mapping.get(tag.split(".")[0], "?")
            for tag in swedish_pos_tagging(swedish_term)[0]["tags"]
        ]
    )
    english_pos_tags = set(
        [
            english_mapping.get(tag[0], "?")
            for tag in english_pos_single_word(english_term)
        ]
    )

    tag = swedish_pos_tags.intersection(english_pos_tags)

    if len(tag) == 1:
        return tag.pop()
    elif len(tag) == 0:
        return "no pos found"
    else:
        tags_as_string = " ".join(list(tag))
        return f"too many possible pos tags: {tags_as_string}"


def get_karp_terms():
    """
    Retrieve terms from Karp, extracting English lemma, Swedish lemma, and POS.

    Returns:
    - pandas.DataFrame: DataFrame containing English lemma, Swedish lemma, and POS for each term.
    """

    json_data = get_all()

    entries = json_data["hits"]

    terms = []
    for entry in entries:

        english_lemma = entry["entry"]["eng"]["lemma"]

        pos = entry["entry"]["pos"]

        swedish_lemma = entry["entry"]["swe"]["lemma"]

        terms.append(
            {"English lemma": english_lemma, "Swedish lemma": swedish_lemma, "POS": pos}
        )

        synonyms = entry["entry"].get("synonyms", [])

        for synonym in synonyms:
            terms.append(
                {"English lemma": english_lemma, "Swedish lemma": synonym, "POS": pos}
            )

    return pd.DataFrame(terms)
