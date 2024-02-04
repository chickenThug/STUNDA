
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

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