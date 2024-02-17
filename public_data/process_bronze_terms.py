import pandas as pd
from collections import defaultdict

def count_words(text):
    return len(text.split())

def no_inflections(text):
    words = text.split()

    seen = defaultdict(lambda: False)

    for word in words:
        if len(word) == 1:
            continue
        else:
            if seen[word[:2]]:
                return False
            seen[word[:2]] = True
    return True


def split_bronze_terms():
    path = "public_data/unprocessed_bronze/"
    all_data_filename = "lemma_data_bronze.csv"

    df = pd.read_csv(path+all_data_filename)

    # Extract entries without translation
    no_translation_df = df[(df['swe_lemma'].isna())]

    # Write entries without translation to file
    no_translation_df.to_csv(path + "lemma_data_bronze_no_translation.csv", index=False)
    
    # Ignore entries without translation
    df = df[~(df['swe_lemma'].isna())]

    # Remove excess whitespace
    df["eng_lemma"] = df["eng_lemma"].str.replace(r"\s+", " ", regex=True)
    df["swe_lemma"] = df["swe_lemma"].str.replace(r"\s+", " ", regex=True)

    # extract entries with a forward slash
    contains_forwardslash_df = df[(df["eng_lemma"].str.contains(r"/")) | (df["swe_lemma"].str.contains(r"/"))]

    # Ignore entries with forward slash
    df = df[~((df["eng_lemma"].str.contains(r"/")) | (df["swe_lemma"].str.contains(r"/")))]

    # Write entries with forward slash 
    contains_forwardslash_df.to_csv(path + "lemma_data_bronze_contains_forwardslash.csv", index=False)

    
    # Ignore entries with more words in the swedish lemma
    df_silver = df[df["eng_lemma"].apply(count_words) >= df["swe_lemma"].apply(count_words)]

    
    # Ignore entries with unexpected characters
    df_silver = df_silver[(df_silver["eng_lemma"].str.match(r"^[a-zA-Z\-\d ]+$")) & (df_silver["swe_lemma"].str.match(r"^[a-zA-ZåäöÅÄÖ\- \d]+$"))]
    
    
    # Extract entries without inflections in the lemma
    df_silver = df_silver[df_silver["eng_lemma"].apply(no_inflections) & df_silver["swe_lemma"].apply(no_inflections)]

    df_silver_old = pd.read_csv("public_data/lemma_data_silver_stage1.csv")

    # Concatenate with existing terms in this stage
    df_silver_new = pd.concat([df_silver, df_silver_old])

    assert len(df_silver_new) ==  len(df_silver_old) + len(df_silver)
    
    # Write silver data to file
    df_silver_new.to_csv("public_data/lemma_data_silver_stage1.csv", index=False)

    # keep only terms which are not moved to a new file
    df_bronze = df[~df["id"].isin(df_silver["id"].to_list())]

    # write bronze terms to file
    df_bronze.to_csv(path + "lemma_data_bronze.csv", index=False)




split_bronze_terms()
