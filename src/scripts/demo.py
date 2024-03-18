
import argparse
import pandas as pd
from collections import defaultdict
from utils import *

def clean_and_simple_checks(df):
    """
    Clean and perform simple checks on the DataFrame lemma data to ensure data quality.

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

    # define condition for checking if a swedish and english lemma exist
    lemma_exist_cond = (df['eng_lemma'] == "") | (df['swe_lemma'] == "")

    # condition to ensure only accpeted characters are present in the lemma
    character_condition = (df["eng_lemma"].str.match(r"^[a-zA-Z\-\d ]+$")) & (df["swe_lemma"].str.match(r"^[a-zA-ZåäöÅÄÖ\- \d]+$"))

    # mark the entries ready for the next stage
    df.loc[character_condition & ~lemma_exist_cond, "status"] = "shallow processed"

    # mark entries with data quality issues
    df.loc[~character_condition & ~lemma_exist_cond, "status"] = "invalid characters in lemma"

    # Mark entries with no english or swedish lemma as lacking translation
    df.loc[lemma_exist_cond, "status"] = "no translation"

    return df

def spell_check(df):
    """
    Perform spell check on English and Swedish lemmas using dictionary lookups.

    Args:
    - df (DataFrame): DataFrame containing lemma data with columns 'eng_lemma' and 'swe_lemma'.
    - write_to_file (bool): Flag indicating whether to write incorrect spelling data to file.

    Returns:
    - DataFrame: Filtered DataFrame containing entries with correct spelling.

    """

    # Perform english spell check
    english_spell_condition = df["eng_lemma"].apply(is_word_in_english)

    # Perform swedish spell check
    swedish_spell_condition = df["swe_lemma"].apply(swedish_spell_check)

    # mark entries
    df.loc[english_spell_condition & swedish_spell_condition, "status"] = "spelling ok"

    df.loc[english_spell_condition & ~swedish_spell_condition, "status"] = "swedish misspelt"

    df.loc[~english_spell_condition & swedish_spell_condition, "status"] = "english misspelt"

    df.loc[~english_spell_condition & ~swedish_spell_condition, "status"] = "both misspelt"

    return df

def pos_and_lemmatizing(df):
    """
    Perform Swedish POS tagging and lemmatization on a DataFrame.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing columns "swe_lemma" and "simple_swedish_pos".
    - write_to_file (bool): Indicates whether to write problematic entries to files.

    Returns:
    - pandas.DataFrame: Filtered DataFrame with successfully lemmatized entries.
    """

    # Find agreed pos
    df['agreed_pos'] = df.apply(lambda x: pos_agreement_term_based(x["swe_lemma"], x["eng_lemma"]), axis=1)

    agreed_pos_exist = df["agreed_pos"].isin(["N", "V", "A", "Ab", "P"])

    df.loc[~agreed_pos_exist, "status"] = df.loc[~agreed_pos_exist, "agreed_pos"]

    # get pos of english lemmas
    df.loc[agreed_pos_exist, 'english_pos'] = df.loc[agreed_pos_exist]["eng_lemma"].apply(english_pos)

    # get pos of swedish lemmas
    df.loc[agreed_pos_exist, 'swedish_pos'] = df.loc[agreed_pos_exist]["swe_lemma"].apply(granska_pos)

    # reduce information for easier checks
    df.loc[agreed_pos_exist, 'simple_swedish_pos']= df.loc[agreed_pos_exist]["swedish_pos"].apply(convert_to_simple_pos)


    # condition to check for suspected sarskrivning
    sarskrivning_condition = df.loc[agreed_pos_exist]["simple_swedish_pos"].str.contains(r"NNS? NNS?", regex=True)

    df.loc[sarskrivning_condition, "status"] = "suspected särskriving"

    # lemmatize swedish lemma 
    df.loc[agreed_pos_exist, 'swe_lemma'], df.loc[agreed_pos_exist]["swe_lemmatizer_status"] = zip(*df.loc[agreed_pos_exist].apply(lambda x: advanced_swedish_lemmatizer(x["swe_lemma"], x["simple_swedish_pos"], x["swedish_pos"]), axis=1))

    df.loc[agreed_pos_exist, 'eng_lemma'] = df.loc[agreed_pos_exist].apply(lambda x: english_lemmatizer_v2(x["eng_lemma"], x["agreed_pos"], x["english_pos"]), axis=1)

    return df

def main():
    parser = argparse.ArgumentParser(description="Automatically process english-swedish computer science term pairs")
    parser.add_argument("-s", "--strings", nargs=2, help="Two term pairs")
    parser.add_argument("-f", "--file", help="Input file")

    args = parser.parse_args()

    single_input = False

    term_pairs = []

    if args.strings:
        term_pairs.append({"eng_lemma" : args.strings[0], "swe_lemma": args.strings[1]})
        single_input = True
    elif args.file:
        with open(args.file, 'r') as file:
            return file.read()
    else:
        print("Please provide either two strings with -s/--strings or a file with -f/--file flag.")
        exit(1)

    df = pd.DataFrame(term_pairs)

    df = clean_and_simple_checks(df)

    if len(df[df["status"] == "shallow processed"]) == 0:
        if single_input:
            print("English lemma:", df.at[0, "eng_lemma"])
            print("Swedish lemma:", df.at[0, "swe_lemma"])
            print("Error        :", df.at[0, "status"])
        return 
    
    df = spell_check(df[df["status"] == "shallow processed"].copy())

    if len(df[df["status"] == "spelling ok"]) == 0:
        if single_input:
            print("English lemma:", df.at[0, "eng_lemma"])
            print("Swedish lemma:", df.at[0, "swe_lemma"])
            print("Error        :", df.at[0, "status"])
        return 

    df = pos_and_lemmatizing(df[df["status"] == "spelling ok"].copy())

    print(df)

main()

    
