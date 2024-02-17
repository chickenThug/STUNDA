import json
import pandas as pd
import os
from collections import defaultdict, Counter
import re

path = "public_data/"
all_data_filename = "lemma_data.csv"

# Read all ids
all_ids = pd.read_csv(path+all_data_filename)[["id", "eng_lemma", "swe_lemma", "status", "pos", "src"]]["id"].to_list()

seen = defaultdict(list)
unseen = 0
terms_info = {"bronze" : {"ACM": 0, "ICT": 0, "GF": 0}, "silver": {"ACM": 0, "ICT": 0, "GF": 0}, "gold": {"ACM": 0, "ICT": 0, "GF": 0}}
 # Iterate over files in the directory
for filename in os.listdir(path[:-1]):
    if filename == all_data_filename:
        continue
    if filename.startswith("lemma") and filename.endswith(".csv"):
        # Read the file into a dataframe
        file_path = os.path.join(path[:-1], filename)

        df = pd.read_csv(file_path)
        duplicate_rows = df.duplicated().sum()
        duplicated_ids = df.duplicated(subset=["id"]).sum()
        acm_terms = df[df.src == "ACM"]
        ict_terms = df[df.src == "ICT"]
        gf_terms = df[df.src == "GF"]
        
        print(f"Filename:{filename}\nDuplicate rows:{duplicate_rows}\nDuplicate ids:{duplicated_ids}\nACM terms:{len(acm_terms)}\nICT terms:{len(ict_terms)}\nGF terms:{len(gf_terms)}\n")
        ids = df["id"].to_list()
        for id in ids:
            seen[id].append(filename)

        tier = re.search(r"bronze|silver|gold", filename).group()
        terms_info[tier]["ACM"] += len(acm_terms)
        terms_info[tier]["ICT"] += len(ict_terms)
        terms_info[tier]["GF"] += len(gf_terms)
        

for stage, source_info in terms_info.items():
    print(stage.upper() + ":")
    for source, count in source_info.items():
        print(f"{count} {source} terms")
    print("\n")

# Keep track of terms that exist in multiple files
counts = []

for id in all_ids:
    filenames = seen[id]
    if not filenames:
        unseen += 1
    else:
        if len(filenames) > 1:
            counts.append(tuple(filenames))


print(f"{unseen} lost terms")
print(Counter(counts))


        

