import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import requests

nltk.download("wordnet")
nltk.download("brown")
nltk.download("universal_tagset")
nltk.download("averaged_perceptron_tagger")

lemmatizer = WordNetLemmatizer()
wordtags = nltk.ConditionalFreqDist(
    (w.lower(), t) for w, t in nltk.corpus.brown.tagged_words(tagset="universal")
)


# Lemmatizer for english words
def english_lemmatizer(word, pos):
    # Noun: 'n'
    # Verb: 'v'
    # Adjective: 'a'
    # Adverb : 'r'
    return lemmatizer.lemmatize(word, pos)


# Custom lemmatizer for english words
def custom_english_lemmatizer(term, pos):

    # List of instances where we don't lemmatize
    do_nothing = ["NN", "JJ", "NN NN", "JJ NN", "JJ NN NN", "NN NN NN", "VBN NN", "VBG NN", "JJ JJ NN", "NN VBG", "JJ NN NN NN"]

    # List of instances where we lemmatize the last word
    lemmatize_last_word = ["NN NNS", "JJ NNS", "NNS", "JJ NN NNS", "NN NN NNS", "VBN NNS", "VBG NNS"]
    
    if pos in do_nothing:
        return term, "ok"
    elif pos in lemmatize_last_word:
        words = term.split(" ")
        lemmatized_word = lemmatizer.lemmatize(words[-1], "n")
        
        lemmatized_term = " ".join(words[:-1] + [lemmatized_word])

        return lemmatized_term, "ok"
    else:
        return term, "not ok"


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
    url = f"https://ws.spraakbanken.gu.se/ws/karp/v7/query/split/stunda?q="

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


#print(custom_english_lemmatizer("abstract network", "JJ NNS"))

#print(english_lemmatizer("types", "n"))

#print(swedish_pos_tagging("katt"))
print(granska_pos("abstrakta"))