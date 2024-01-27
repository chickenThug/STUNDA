import json
import pandas as pd

path = "../data/"
file = "stunda-terms.jsonl"

def read_jsonl_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            # Load each line as a JSON object
            json_object = json.loads(line)
            data.append(json_object)
    return data

data = read_jsonl_file(path + file)

lemman = []
inflections = []

for entry in data:
    status = "bronze"

    if entry["status"] == "1":
        status = "silver"
    lemman.append({"id": entry["src"] + entry["row"], 
                   "eng_lemma": entry["eng"]["lemma"],
                   "swe_lemma": entry["swe"]["lemma"],
                   "status": status,
                   "pos": entry["pos"],
                   "src" : entry["src"]
                   })
    
    for inflection in entry["eng"]["inflection"]:
        inflections.append({
            "lemma_id" : entry["src"] + entry["row"],
            "word": inflection,
            "type" : "unknown",
            "language" : "eng" 
        })
    
    for inflection in entry["swe"]["inflection"]:
        inflections.append({
            "lemma_id" : entry["src"] + entry["row"],
            "word": inflection,
            "type" : "unknown",
            "language" : "swe" 
        })


lemma_df = pd.json_normalize(lemman)
inflection_df = pd.json_normalize(inflections)

lemma_df[lemma_df["status"] == "bronze"].to_csv("../public_data/lemma_data_bronze.csv")
lemma_df[lemma_df["status"] == "silver"].to_csv("../public_data/lemma_data_silver.csv")
inflection_df.to_csv("../public_data/inflection_data.csv")

