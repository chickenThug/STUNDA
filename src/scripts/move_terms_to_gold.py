import json
import pandas as pd
import requests
from utils import is_word_in_english, english_pos

# mapping for pos-tags swe --> correct tag
pos_mapping = {
    'nn': 'N',
    'jj': 'A',
    'vb': 'V'
}

# Function to spell-check using Skrutten Stava API
def swedish_spell_check(word):
    url = 'https://skrutten.csc.kth.se/granskaapi/spell/json/'

    response = requests.get(url + word)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return None

# Function to pos-tag using Skrutten Taggstava API
def swedish_pos_tagging(word):
    url = 'https://skrutten.csc.kth.se/granskaapi/taggstava/json/'

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
        df_correct_spellings = pd.concat(correct_spellings)
        # df_correct_spellings['status'] = 'gold' # not finished for gold here, unless GF
        # df_correct_spellings.to_csv(path+"test_ok.csv", index=False) # Keep handling data
    except:
        print("No correct terms")

    try:
        df_incorrect_spellings = pd.concat(incorrect_spellings)
        df_incorrect_spellings.to_csv(path+"lemma_data_silver_stage3_incorrect_spellings.csv", index=False)
    except:
        print("No incorrect terms")
    
    return df_correct_spellings

def pos_tag_terms(df):
    swe_terms = df["swe_lemma"].tolist()
    eng_terms = df["eng_lemma"].tolist()

    correct_pos_tags = []

    for eng_term, swe_term in zip(eng_terms, swe_terms):
        swe_results = swedish_pos_tagging(swe_term.strip())
        swe_result = swe_results[0]
        swe_tags = swe_result['tags']
        swe_pos = []

        # retrieve the pos from the output of skrutten api (contains more info originally)
        for tag in swe_tags:
            pos = tag.split('.')[0]
            if pos in swe_pos:
                continue
            swe_pos.append(pos)

        #eng_pos = english_pos(eng_term.strip())

        # if only one pos tag for swedish, add to correct list with that tag
        if len(swe_pos) == 1:
            try:
                pos_tag = pos_mapping[swe_pos[0]]
                correct_pos_tags.append(df[(df["eng_lemma"] == eng_term) & (df["swe_lemma"] == swe_term)].assign(pos=pos_tag))
            except:
                continue # tag that can't be handled. what is "ab"?
    
    try:
        df_correct_pos = pd.concat(correct_pos_tags)
        df_correct_pos.to_csv(path+"lemma_data_silver_stage3.csv", index=False) # Keep handling data
    except:
        print("No correct terms")

path = "public_data/"
file = "lemma_data_silver_stage2.csv"

df = pd.read_csv(path+file)[["id", "eng_lemma", "swe_lemma", "status", "pos", "src"]]

df_correct_spellings = spell_check_terms(df) # send this to pos_tagging later

pos_tag_terms(df)