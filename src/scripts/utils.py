
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

nltk.download('wordnet')
nltk.download('brown')
nltk.download('universal_tagset')

lemmatizer = WordNetLemmatizer()
wordtags = nltk.ConditionalFreqDist((w.lower(), t) for w, t in nltk.corpus.brown.tagged_words(tagset="universal"))

# Lemmatizer for english words
def english_lemmatizer(term, pos):
    pass

# Tag part of speech 
def english_pos(word):
    return list(wordtags[word.lower()].items())


english_pos("crashy")