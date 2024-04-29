
import argparse
import pandas as pd
from collections import defaultdict
from utils import *
import json
import time

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
    if len(df) == 0:
        return df

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

def pos(df):
    if len(df) == 0:
        return df
    # Find agreed pos
    df['agreed_pos'] = df.apply(lambda x: pos_agreement_term_based(x["swe_lemma"], x["eng_lemma"]), axis=1)

    df.loc[~df["agreed_pos"].isin(["N", "V", "A", "Ab", "P"]), "status"] = df.loc[~df["agreed_pos"].isin(["N", "V", "A", "Ab", "P"]), "agreed_pos"]

    df.loc[df["agreed_pos"].isin(["N", "V", "A", "Ab", "P"]), "status"] = 'found pos'

    return df

def lemmatize(df):
    """
    Perform Swedish POS tagging and lemmatization on a DataFrame.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing columns "swe_lemma" and "simple_swedish_pos".
    - write_to_file (bool): Indicates whether to write problematic entries to files.

    Returns:
    - pandas.DataFrame: Filtered DataFrame with successfully lemmatized entries.
    """

    if len(df) == 0:
        return df
    # get pos of english lemmas
    df['english_pos'] = df["eng_lemma"].apply(english_pos)

    # get pos of swedish lemmas
    df['swedish_pos'] = df["swe_lemma"].apply(granska_pos)

    # reduce information for easier checks
    df['simple_swedish_pos']= df["swedish_pos"].apply(convert_to_simple_pos)

    # condition to check for suspected sarskrivning
    sarskrivning_condition = df["simple_swedish_pos"].str.contains(r"NNS? NNS?", regex=True)

    df.loc[sarskrivning_condition, "status"] = "suspected särskriving"

    # lemmatize swedish lemma 
    df['swe_lemma'], df['swe_lemmatizer_status'] = zip(*df.apply(lambda x: advanced_swedish_lemmatizer(x["swe_lemma"], x["simple_swedish_pos"], x["swedish_pos"]), axis=1))

    df['eng_lemma'] = df.apply(lambda x: english_lemmatizer_v2(x["eng_lemma"], x["agreed_pos"], x["english_pos"]), axis=1)

    df.loc[~sarskrivning_condition & (df['swe_lemmatizer_status'] == 'ok'), 'status'] = "automatically verified"
    df.loc[~sarskrivning_condition & (df['swe_lemmatizer_status'] != 'ok'), 'status'] = df.loc[~sarskrivning_condition & (df['swe_lemmatizer_status'] != 'ok'), 'swe_lemmatizer_status']

    return df

def clean_pos(df):
    df.fillna('', inplace=True)
    df.loc[df['POS'] == 'no pos found', 'POS'] = ''

    def has_multiple_words(row):
        return ' ' in row['Swedish lemma'] or ' ' in row['English lemma']

    # Apply the function to update 'POS' column
    df.loc[df.apply(has_multiple_words, axis=1) & (df['POS'] != ''), 'POS'] = 'NP'
    return df

def main():
    parser = argparse.ArgumentParser(description="Automatically process english-swedish computer science term pairs")
    parser.add_argument("-s", "--strings", nargs=2, help="Two term pairs")
    parser.add_argument("-f", "--file", help="Input txt file")
    parser.add_argument("-jf", "--jsonfile", help="Input json file")
    parser.add_argument("-jfl", "--jsonlfile", help="Input jsonl file")


    args = parser.parse_args()

    single_input = False

    term_pairs = []

    if args.strings:
        term_pairs.append({"eng_lemma" : args.strings[0], "swe_lemma": args.strings[1]})
        single_input = True
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as file:
            term_pairs = file.readlines()
            term_pairs = [{'eng_lemma' : term_pair.rstrip().split(',')[0], 'swe_lemma': term_pair.rstrip().split(',')[1]} for term_pair in term_pairs]
    elif args.jsonfile:
        with open(args.jsonfile, 'r', encoding='utf-8') as file:
            # Load JSON data from the file
            data = json.load(file)
            for key, value in data.items():
                for swe_term in value:
                    term_pairs.append({"eng_lemma": key, "swe_lemma": swe_term, "src":"paired keywords"})
    elif args.jsonlfile:
        with open(args.jsonlfile, 'r', encoding='utf-8') as file:
            # Iterate through each line in the file
            for line in file:
                # Load the JSON object from the line
                data = json.loads(line)
                term_pairs.append({"eng_lemma": data["eng"]["lemma"], "swe_lemma":data["swe"]["lemma"], "src": data["src"]})
    else:
        print("Please provide either two strings with -s/--strings or a file with -f/--file flag.")
        exit(1)

    t0 = time.time()
    df = pd.DataFrame(term_pairs)

    # Time the cleaning and simple checks
    start_time = time.time()
    df = clean_and_simple_checks(df)
    print("finished simple checks in {:.2f} seconds".format(time.time() - start_time))

    df_stop1 = df[df["status"] != "shallow processed"]
    df_cont = df[df["status"] == "shallow processed"]

    # Time the spell check
    start_time = time.time()
    df = spell_check(df_cont.copy())
    print("finished spell check in {:.2f} minutes".format((time.time() - start_time)/60))

    df_stop2 = df[df["status"] != "spelling ok"]
    df_cont = df[df["status"] == "spelling ok"]

    # Time the part-of-speech tagging
    start_time = time.time()
    df = pos(df_cont.copy())
    print("finished part-of-speech tagging in {:.2f} minutes".format((time.time() - start_time)/60))

    df_stop3 = df[df['status'] != 'found pos']
    df_cont = df[df['status'] == 'found pos']

    # Time the lemmatization
    start_time = time.time()
    df = lemmatize(df_cont.copy())
    print("finished lemmatization in {:.2f} minutes".format((time.time() - start_time)/60))

    # Concatenate all parts and calculate total processing time
    output_df = pd.concat([df_stop1, df_stop2, df_stop3, df])

    total_time = time.time() - t0
    print("Total processing time: {:.2f} minutes".format(total_time/60))


    if single_input:
        print("English lemma:", output_df.at[0, "eng_lemma"])
        print("Swedish lemma:", output_df.at[0, "swe_lemma"])
        print("Status       :", output_df.at[0, "status"])
        if 'agreed_pos' in output_df.columns and len(output_df.at[0, "eng_lemma"].split(" ")) == 1 and len(output_df.at[0, "swe_lemma"].split(" ")) == 1:
            print("POS          :", output_df.at[0, "agreed_pos"])
    else:
        # from tabulate import tabulate
        output_df.rename(columns={'eng_lemma': 'English lemma', 'swe_lemma': 'Swedish lemma', 'agreed_pos': 'POS' }, inplace=True)
        output_df = clean_pos(output_df)
        output_df.to_csv("ready_for_karp_v2.csv", index=False)
        # output_df = output_df[["English lemma", 'Swedish lemma', 'POS', 'status']]
        # 
        # output_df.to_csv("ready_for_karp_v2.csv", index=False)
        # print(tabulate(output_df, headers='keys', tablefmt='psql', showindex=False))


main()

    
