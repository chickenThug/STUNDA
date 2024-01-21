import json
import pandas as pd
import re

import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer


path = "../data/"
file = "stunda-terms.jsonl"
working_file = "stunda-terms-processed.jsonl"

nltk.download('wordnet')

def read_jsonl_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            # Load each line as a JSON object
            json_object = json.loads(line)
            data.append(json_object)
    return data


data = read_jsonl_file(path + file)

simple_data = []


for entry in data:
    if entry["status"] == "1":
        simple_data.append(entry)
        continue

    # pattern to match single word
    pattern_single_word = r"^[a-z]+$"

    pattern_multiple_words = r"^[a-z]+ ([a-z]+ )*[a-z]+$"

    pattern_pipe_char = r'\b(\w+)\|(\w+)\b'

    # Define a function to handle the replacement
    def replace(match):
        return f"{match.group(1)} {match.group(1)}{match.group(2)}"

    # Use re.sub with the defined pattern and replacement function
    entry["eng"]["lemma"] = re.sub(pattern_pipe_char, replace, entry["eng"]["lemma"])
    entry["swe"]["lemma"] = re.sub(pattern_pipe_char, replace, entry["swe"]["lemma"])

    if re.match(pattern_single_word, entry["eng"]["lemma"]) and re.match(pattern_single_word, entry["swe"]["lemma"]):
        simple_data.append(entry)

    elif re.match(pattern_multiple_words, entry["eng"]["lemma"]) and re.match(pattern_multiple_words, entry["swe"]["lemma"]):
        english_words = entry["eng"]["lemma"].split(" ")
        swedish_words = entry["swe"]["lemma"].split(" ")

        if len(english_words) == len(swedish_words):
            english_lemma = english_words[0]

            lemmatizer = WordNetLemmatizer()
            
            for pos in ["n", "v", "a"]:
                good = True
                for word in english_words[1:]:
                    lemma = lemmatizer.lemmatize(word, pos) 
                    if english_lemma != lemma:
                        good = False
                
                if good:
                    entry["eng"]["lemma"] = english_lemma
                    entry["swe"]["lemma"] = swedish_words[0]
                    entry["eng"]["inflection"] = english_words[1:]
                    entry["swe"]["inflection"] = swedish_words[1:]
                    
                    entry["pos"] = pos
                    simple_data.append(entry)
                    break
                


print(len(simple_data))
quit()

with open(path + working_file, 'w') as jsonl_file:
    for json_object in simple_data:
        jsonl_file.write(json.dumps(json_object) + '\n')


        



