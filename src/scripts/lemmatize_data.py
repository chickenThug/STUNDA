import pandas as pd
import requests
from utils import english_lemmatizer

# pos-tags swe --> correct tag for csv
pos_mapping = {
    'nn': 'N',
    'jj': 'A',
    'vb': 'V'
}

# Function to pos-tag using Skrutten Taggstava API
def swedish_pos_tagging(word):
    url = 'https://skrutten.csc.kth.se/granskaapi/taggstava/json/'

    response = requests.get(url + word)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return None

def swedish_lemmatizing(word):
    url = 'https://skrutten.csc.kth.se/granskaapi/lemma/json/'

    response = requests.get(url + word)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return None

def lemmatize_df(df):
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

        # if only one pos tag for swedish, add to correct list with that tag
        if len(swe_pos) == 1:
            # lemmatize swedish word
            swe_lemmatized = swedish_lemmatizing(swe_term)
            swe_lemma = swe_lemmatized[0]['lemma']

            try:
                # lemmatize english word
                eng_pos_tag = pos_mapping[swe_pos[0]].lower()
                eng_lemma = english_lemmatizer(eng_term, eng_pos_tag)

                # get correct pos tag for csv
                pos_tag = pos_mapping[swe_pos[0]]

                values_to_assign = {
                    "eng_lemma": eng_lemma,
                    "swe_lemma": swe_lemma,
                    "pos": pos_tag
                }

                correct_pos_tags.append(df[(df["eng_lemma"] == eng_term) & (df["swe_lemma"] == swe_term)].assign(**values_to_assign))
            except:
                print("We are in except ): " + swe_term)
                continue # tag that can't be handled
    
    try:
        df_correct_pos = pd.concat(correct_pos_tags)
        df_correct_pos['status'] = 'gold'
        df_correct_pos.to_csv(path+"lemma_data_gold.csv", mode='a', header=False, index=False) # NAME
    except:
        print("No correct terms")

path = "public_data/"
file = "lemma_data_silver_stage3.csv"

df = pd.read_csv(path+file)[["id", "eng_lemma", "swe_lemma", "status", "pos", "src"]]

lemmatize_df(df)