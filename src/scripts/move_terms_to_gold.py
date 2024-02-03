import json
import pandas as pd
import requests
from utils import is_word_in_english

# Function to spell-check usin Skrutten Stava API
def swedish_spell_check(word):
    url = 'https://skrutten.csc.kth.se/granskaapi/spell/json/'

    response = requests.get(url + word)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return None

path = "public_data/"
file = "lemma_data_silver.csv"

# Read data
df = pd.read_csv(path+file)[["id", "eng_lemma", "swe_lemma", "status", "pos", "src"]]

swe_terms = df["swe_lemma"].tolist()
eng_terms = df["eng_lemma"].tolist()

correct_spellings = []
incorrect_spellings = []

for eng_term, swe_term in zip(eng_terms, swe_terms):
    # Skip lemmas that consists of two words
    if ' ' in eng_term.strip() or ' ' in swe_term.strip():
        continue

    # Check spelling for Swedish word
    swe_results = swedish_spell_check(swe_term.strip())
    swe_result = swe_results[0]
    swe_correct = swe_result['correct']

    # Check spelling for English word
    eng_correct = is_word_in_english(eng_term)

    # Append rows to their respective lists
    if eng_correct and swe_correct:
        correct_spellings.append(df[(df["eng_lemma"] == eng_term) & (df["swe_lemma"] == swe_term)])
    else:
        incorrect_row = df[(df["eng_lemma"] == eng_term) & (df["swe_lemma"] == swe_term)].copy()
        incorrect_row['incorrect'] = 'both' if not eng_correct and not swe_correct else ('eng' if not eng_correct else 'swe')
        incorrect_spellings.append(incorrect_row)

try:
    df_correct = pd.concat(correct_spellings)
    df_correct['status'] = 'gold'
    df_correct.to_csv(path+"lemma_data_gold.csv", index=False)
except:
    print("No correct terms")

try:
    df_incorrect = pd.concat(incorrect_spellings)
    df_incorrect.to_csv(path+"lemma_data_silver_incorrect_spellings.csv", index=False)
except:
    print("No incorrect terms")