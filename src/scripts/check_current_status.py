import json
import pandas as pd
import os
from collections import defaultdict, Counter

path = "public_data/"
all_data_filename = "lemma_data.csv"

# Read all ids
all_ids = pd.read_csv(path+all_data_filename)[["id", "eng_lemma", "swe_lemma", "status", "pos", "src"]]["id"].to_list()

seen = defaultdict(list)
unseen = 0

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
        print(f"Filename:{filename}\nDuplicate rows:{duplicate_rows}\nDuplicate ids:{duplicated_ids}")
        ids = df["id"].to_list()

        if duplicate_rows > 0:
            df.drop_duplicates().to_csv(file_path, index=False)

        for id in ids:
            seen[id].append(filename)


counts = []

for id in all_ids:
    filenames = seen[id]
    if not filenames:
        unseen += 1
    else:
        if len(filenames) > 1:
            counts.append(len(filenames))
        if len(filenames) > 3:
            # print(filenames)
            pass

print(f"{unseen} lost terms")
print(Counter(counts))


        

