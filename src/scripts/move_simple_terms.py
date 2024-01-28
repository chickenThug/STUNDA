import json
import pandas as pd

path = "public_data/"
file = "lemma_data_bronze.csv"

# Read data
df = pd.read_csv(path+file)[["id", "eng_lemma", "swe_lemma", "status", "pos", "src"]]

# Select only those rows which consist of alphabet chars
# ready_for_silver = df[(df["eng_lemma"].str.match(r"^[a-zA-Z]+$")) & (df["swe_lemma"].str.match(r"^[a-zA-ZåäöÅÄÖ]+$"))]

still_bronze = df[~((df["eng_lemma"].str.match(r"^[a-zA-Z]+$")) & (df["swe_lemma"].str.match(r"^[a-zA-ZåäöÅÄÖ]+$")))]


# select words on the form "word-secondWord" in english 
cond1 = ((df["eng_lemma"].str.match(r"^[a-zA-Z]+-[a-zA-Z]+$")) & (df["swe_lemma"].str.match(r"^[a-zA-ZåäöÅÄÖ]+$")))

# select and clean words with pipe char in lemma
cond2 = ((df["eng_lemma"].str.match(r"^[a-zA-Z\|]+$")) & (df["swe_lemma"].str.match(r"^[a-zA-ZåäöÅÄÖ\|]+$")))

df.loc[cond1 | cond2, "eng_lemma"] = df.loc[cond1 | cond2, "eng_lemma"].str.replace(r"\|[a-zA-Z]+","", regex=True)
df.loc[cond1 | cond2, "swe_lemma"] = df.loc[cond1 | cond2, "swe_lemma"].str.replace(r"\|[a-zA-ZåäöÅÄÖ]+","", regex=True)

silver_stage_one = df[(cond1 | cond2)]
still_bronze = df[~(cond1 | cond2)]

still_bronze.to_csv(path+file, index=False)
silver_stage_one.to_csv(path+"lemma_data_silver_stage1.csv", index=False)


