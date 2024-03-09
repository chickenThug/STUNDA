
import json
import pandas as pd
from collections import defaultdict
from utils import *

# Reads json object containing english-swedish term pairs and transform it to pandas dataframe format
def read_data_and_transform_data(file_path):
    transformed_data = []
    with open(file_path, 'r') as file:
        for line in file:
            # Load each line as a JSON object
            entry = json.loads(line)
            transformed_data.append({"id": entry["src"] + entry["row"], 
                   "eng_lemma": entry["eng"]["lemma"],
                   "swe_lemma": entry["swe"]["lemma"],
                   "status": "unprocessed",
                   "pos": entry["pos"],
                   "src" : entry["src"]
                   })

    return pd.json_normalize(transformed_data)

# helper function to count words
def count_words(text):
    return len(text.split())

# helper function to assess if there exist inflecftions in the lemma
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

def clean_and_simple_checks(df, write_to_file):
    """
    Clean and perform simple checks on the DataFrame lemma data.

    Args:
    - df (DataFrame): DataFrame containing lemma data with columns 'eng_lemma' and 'swe_lemma'.
    - write_to_file (bool): Flag indicating whether to write parentheses data to file.

    Returns:
    - DataFrame: Filtered DataFrame containing entries ready for the next processing step.

    """

    # Remove excess whitespace and convert to lower case
    df["eng_lemma"] = df["eng_lemma"].str.replace(r"\s+", " ", regex=True).str.lower()
    df["swe_lemma"] = df["swe_lemma"].str.replace(r"\s+", " ", regex=True).str.lower()

    # remove [*] and [**] from entries
    df["eng_lemma"] = df["eng_lemma"].str.replace(r"\[\*\*?\]", "", regex=True).str.strip()
    df["swe_lemma"] = df["swe_lemma"].str.replace(r"\[\*\*?\]", "", regex=True).str.strip()

    # copy paranthesis from entry
    df["eng_paranthesis"] = df["eng_lemma"].str.extract(r"(\([^\(]+\))")
    df["swe_paranthesis"] = df["swe_lemma"].str.extract(r"(\([^\(]+\))")

    # remove paranthesis from entry
    df["eng_lemma"] = df["eng_lemma"].str.replace(r"\([^\(]+\)", "", regex=True).str.strip()
    df["swe_lemma"] = df["swe_lemma"].str.replace(r"\([^\(]+\)", "", regex=True).str.strip()

    # save paranthesis data to file
    paranthesis_data = df[(~df["eng_paranthesis"].isna()) | (~df["swe_paranthesis"].isna())]

    if write_to_file:
        paranthesis_data.to_csv("temp/data/parentheis_data.csv", index=False)

    # define condition for checking if a swedish and english lemma exist
    lemma_exist_cond = (df['eng_lemma'] == "") | (df['swe_lemma'] == "")

    # condition to ensure more or equal words in english lemma
    word_count_condition = df["eng_lemma"].apply(count_words) >= df["swe_lemma"].apply(count_words)

    # condition to ensure there aren't inflections in the lemma
    inflection_condition = df["eng_lemma"].apply(no_inflections) & df["swe_lemma"].apply(no_inflections)

    # condition to ensure only accpeted characters are present in the lemma
    character_condition = (df["eng_lemma"].str.match(r"^[a-zA-Z\-\d ]+$")) & (df["swe_lemma"].str.match(r"^[a-zA-ZåäöÅÄÖ\- \d]+$"))

    # mark the entries ready for the next stage
    df.loc[word_count_condition & inflection_condition & character_condition & ~lemma_exist_cond, "status"] = "shallow processed"

    # mark entries with data quality issues
    df.loc[~word_count_condition | ~inflection_condition | ~character_condition & ~lemma_exist_cond, "status"] = "data quality issues"

    # Mark entries with no english or swedish lemma as lacking translation
    df.loc[lemma_exist_cond, "status"] = "no translation"

    if write_to_file:
        df[df["status"] == "data quality issues"].to_csv("temp/data/data_quality_issues.csv", index=False)

    print("Status after first processing step")
    print(df.status.value_counts())

    return df[df["status"] == "shallow processed"].copy()

def spell_check(df, write_to_file):
    """
    Perform spell check on English and Swedish lemmas using dictionary lookups.

    Args:
    - df (DataFrame): DataFrame containing lemma data with columns 'eng_lemma' and 'swe_lemma'.
    - write_to_file (bool): Flag indicating whether to write incorrect spelling data to file.

    Returns:
    - DataFrame: Filtered DataFrame containing entries with correct spelling.

    """

    english_spell_condition = df["eng_lemma"].apply(is_word_in_english)
    swedish_spell_condition = df["swe_lemma"].apply(swedish_spell_check)

    # mark entries
    df.loc[english_spell_condition & swedish_spell_condition, "status"] = "spelling ok"

    df.loc[english_spell_condition & ~swedish_spell_condition, "status"] = "swedish misspelt"

    df.loc[~english_spell_condition & swedish_spell_condition, "status"] = "english misspelt"

    df.loc[~english_spell_condition & ~swedish_spell_condition, "status"] = "both misspelt"

    print("Status after first processing step")
    print(df.status.value_counts())

    if write_to_file:
        df[df["status"] != "spelling ok"].to_csv("temp/data/incorrect_spelling.csv", index=False)

    return df[df["status"] == "spelling ok"].copy()
 

def english_pos_and_lemmatizing(df, write_to_file):
    df["english_pos"] = df["eng_lemma"].apply(english_pos)

    df["eng_lemma"], df["status"] = zip(*df.apply(lambda x: english_lemmatizer(x["eng_lemma"], x["english_pos"]), axis=1))

    print(df.status.value_counts())

    return df

def swedish_pos_and_lemmatizing(df, write_to_file):


    df["swedish_pos"] = df["swe_lemma"].apply(granska_pos)
    df["simple_swedish_pos"] = df["swedish_pos"].apply(convert_to_simple_pos)

    print(df.simple_swedish_pos.value_counts())








def main():
    path = "data/"
    file = "stunda-terms.jsonl"

    # reads and transforms data from json format to a pandas dataframe
    transformed_data = read_data_and_transform_data(path + file)

    shallow_processed_data = clean_and_simple_checks(transformed_data, False)

    spelling_processed_data = spell_check(shallow_processed_data, False)

    lemmatized_processed_data = english_pos_and_lemmatizing(spelling_processed_data, False)

    swedish_pos_and_lemmatizing(lemmatized_processed_data, False)

main()