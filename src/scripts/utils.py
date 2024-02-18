
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
import requests

nltk.download('wordnet')
nltk.download('brown')
nltk.download('universal_tagset')

lemmatizer = WordNetLemmatizer()
wordtags = nltk.ConditionalFreqDist((w.lower(), t) for w, t in nltk.corpus.brown.tagged_words(tagset="universal"))

# Lemmatizer for english words
def english_lemmatizer(word, pos):
    # Noun: 'n'
    # Verb: 'v'
    # Adjective: 'a'
    # Adverb : 'r'
    return lemmatizer.lemmatize(word, pos)

# Tag part of speech 
def english_pos(word):
    return list(wordtags[word.lower()].items())

# Function to check if a string is a word in WordNet
def is_word_in_english(term):
    words = term.split(" ")
    correct = True

    for word in words:
        if len(wordnet.synsets(word)) == 0:
            correct = False

    return correct

def delete_entry_by_id(id, authorization ,verbose = False):
    url = f"https://ws.spraakbanken.gu.se/ws/karp/v7/entries/stunda/{id}/1"
    
    headers = {
    'Authorization': "Bearer " + authorization,
    'Content-Type': 'application/json',
    }

    response = requests.delete(url = url, headers = headers)

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
    url =  f"https://ws.spraakbanken.gu.se/ws/karp/v7/query/split/stunda?q="

    params = {
        "size" : 10000
    }

    # Make the GET request
    response = requests.get(url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Print the response content
        print("succesfull get")
        return response.json()  # Assuming the response is in JSON format
    else:
        print('Error:', response.status_code)
        return {}
    
def add_entry(authorization, entry, verbose=False):
    url = "https://ws.spraakbanken.gu.se/ws/karp/v7/entries/stunda"

    headers = {
    'Authorization': "Bearer " + authorization,
    'Content-Type': 'application/json',
    }

    data = {
        "entry" : entry,
        "message": ""
    }

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
    url = 'https://skrutten.csc.kth.se/granskaapi/spell/'

    words = term.split(" ")

    if len(words) == 1:
        response = requests.get(url + 'json/' + term)
    else:
        params = {'coding': 'json', 'words': term}

        response = requests.post(url, data=params)

    if response.status_code == 200:
        result = response.json()
        correct = True

        for i in result:
            if not i['correct']:
                correct = False
        
        if len(result) == 0:
            return False
        return correct
    else:
        return None
    
# Function to pos-tag using Skrutten Taggstava API
def swedish_pos_tagging(term):
    url = 'https://skrutten.csc.kth.se/granskaapi/taggstava/'

    words = term.split(" ")

    if len(words) == 1:
        response = requests.get(url + 'json/' + term)
    else:
        params = {'coding': 'json', 'words': term}

        response = requests.post(url, data=params)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return None

