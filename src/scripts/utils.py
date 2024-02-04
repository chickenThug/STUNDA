
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
def is_word_in_english(word):
    return len(wordnet.synsets(word)) > 0

def delete_entry_by_id(id, authorization ,verbose = False):
    url = f"https://ws.spraakbanken.gu.se/ws/karp/v7/entries/stunda/{id}/1.1"
    
    headers = {
    'Authorization': "Bearer " + authorization,
    'Content-Type': 'application/json',
    "entry_id": "01GX3DS1HJBMF7DNCJCQW9E6N3",
    }

    response = requests.delete(url, headers)

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
