import json
import pandas as pd

path = "public_data/"
file = "lemma_data_bronze.csv"

# Read data
df = pd.read_csv(path+file)[["id", "eng_lemma", "swe_lemma", "status", "pos", "src"]]

print(len(df))


# Select only those rows which consist of alphabet chars

ready_for_silver = df[(df["eng_lemma"].str.match(r"^[a-zA-Z]+$")) & (df["swe_lemma"].str.match(r"^[a-zA-ZåäöÅÄÖ]+$"))]

still_bronze = df[~((df["eng_lemma"].str.match(r"^[a-zA-Z]+$")) & (df["swe_lemma"].str.match(r"^[a-zA-ZåäöÅÄÖ]+$")))]

still_bronze.to_csv(path+file, index=False)

if len(ready_for_silver) > 0:
    ready_for_silver.to_csv(path + "lemma_data_silver_batch2.csv", index=False)

