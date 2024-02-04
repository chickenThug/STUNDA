import json
import pandas as pd
import requests
from utils import is_word_in_english

# Function to spell-check using Skrutten Stava API
def swedish_spell_check(word):
    url = 'https://skrutten.csc.kth.se/granskaapi/spell/json/'

    response = requests.get(url + word)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return None

def spell_check_terms(df):
    swe_terms = df["swe_lemma"].tolist()
    eng_terms = df["eng_lemma"].tolist()

    correct_spellings = []
    incorrect_spellings = []

    for eng_term, swe_term in zip(eng_terms, swe_terms):
        # Skip lemmas that does not consist of two words
        if ' ' not in eng_term.strip() and ' ' not in swe_term.strip():
            continue

        swe_words = swe_term.strip().split()
        eng_words = eng_term.strip().split()
        swe_check = True
        eng_check = True

        # spell check swe
        for word in swe_words:
            swe_results = swedish_spell_check(word)
            swe_result = swe_results[0]
            swe_correct = swe_result['correct']
            if swe_correct == False:
                swe_check = False

        for word in eng_words:
            eng_correct = is_word_in_english(word)
            if eng_correct == False:
                eng_check = False

        # Append rows to their respective lists
        if eng_check and swe_check:
            correct_spellings.append(df[(df["eng_lemma"] == eng_term) & (df["swe_lemma"] == swe_term)])
        else:
            incorrect_row = df[(df["eng_lemma"] == eng_term) & (df["swe_lemma"] == swe_term)].copy()
            incorrect_row['incorrect'] = 'both' if not eng_check and not swe_check else ('eng' if not eng_check else 'swe')
            incorrect_spellings.append(incorrect_row)

    try:
        df_correct_spellings = pd.concat(correct_spellings)
        df_correct_spellings['status'] = 'gold' # not finished for gold here, unless GF
        df_correct_spellings.to_csv(path+"lemma_data_gold.csv", mode='a', header=False, index=False) # Keep handling data
    except:
        print("No correct terms")

    try:
        df_incorrect_spellings = pd.concat(incorrect_spellings)
        df_incorrect_spellings.to_csv(path+"lemma_data_silver_incorrect_spellings.csv", mode='a', header=False, index=False) # keep writing to incorrect spelling csv
    except:
        print("No incorrect terms")
    
    return df_correct_spellings

path = "public_data/"
file = "lemma_data_silver.csv"

df = pd.read_csv(path+file)[["id", "eng_lemma", "swe_lemma", "status", "pos", "src"]]

spell_check_terms(df)