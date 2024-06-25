
import os

import sys
sys.path.insert(0, 'lib')
import argparse
import pandas as pd
from collections import defaultdict
from utils import *
import json
import time
from dotenv import load_dotenv


# Load environment variables from .env file
# Fix loading of correct .env file when on serer
load_dotenv()

banned_words = {
    "en": [
        "abortion",
        "anal",
        "anus",
        "arse",
        "ass",
        "ass-fucker",
        "asses",
        "asshole",
        "assholes",
        "ballbag",
        "balls",
        "bastard",
        "bellend",
        "bestial",
        "bestiality",
        "bitch",
        "bitches",
        "bitching",
        "bloody",
        "blowjob",
        "bollok",
        "boob",
        "boobs",
        "breasts",
        "buceta",
        "bum",
        "butt",
        "carpet muncher",
        "chink",
        "cipa",
        "clitoris",
        "cock",
        "cock-sucker",
        "cocks",
        "coon",
        "crap",
        "cum",
        "cumshot",
        "cunillingus",
        "cunt",
        "damn",
        "dick",
        "dildo",
        "dildos",
        "dink",
        "dog-fucker",
        "duche",
        "dyke",
        "ejaculate",
        "ejaculated",
        "ejaculates",
        "ejaculating",
        "ejaculation",
        "fag",
        "fagging",
        "faggot",
        "fagot",
        "fagots",
        "fanny",
        "felching",
        "fellatio",
        "flange",
        "fuck",
        "fucked",
        "fucker",
        "fuckers",
        "fucking",
        "fuckings",
        "fucks",
        "fudge packer",
        "god-damned",
        "goddamn",
        "hell",
        "hore",
        "horny",
        "jerk-off",
        "kock",
        "labia",
        "lust",
        "lusting",
        "masochist",
        "masturbate",
        "mother fucker",
        "nazi",
        "nigger",
        "niggers",
        "orgasim",
        "orgasm",
        "orgasms",
        "pecker",
        "penis",
        "piss",
        "pissed",
        "pisser",
        "pisses",
        "pissing",
        "pissoff",
        "poop",
        "porn",
        "porno",
        "pornography",
        "prick",
        "pricks",
        "pube",
        "pussies",
        "pussy",
        "rape",
        "rapist",
        "rectum",
        "retard",
        "rimming",
        "sadist",
        "screwing",
        "scrotum",
        "semen",
        "sex",
        "shag",
        "shagging",
        "shemale",
        "shit",
        "shite",
        "shits",
        "shitted",
        "shitting",
        "shitty",
        "skank",
        "slut",
        "sluts",
        "smegma",
        "smut",
        "snatch",
        "son-of-a-bitch",
        "spac",
        "spunk",
        "testicle",
        "tit",
        "tits",
        "titt",
        "turd",
        "vagina",
        "viagra",
        "vulva",
        "wang",
        "wank",
        "whore",
        "x rated",
        "xxx"
    ],
    "sv": [
        "abort",
        "anal",
        "anus",
        "röv",
        "ass-fucker",
        "åsnor",
        "idiot",
        "arslen",
        "bollväska",
        "bollar",
        "bastard",
        "bellend",
        "bestialisk",
        "tidelag",
        "tik",
        "tikar",
        "bitching",
        "blodig",
        "avsugning",
        "bollok",
        "boob",
        "tuttar",
        "bröst",
        "buceta",
        "luffare",
        "stånga",
        "mattan mattan",
        "spricka",
        "cipa",
        "klitoris",
        "kuk",
        "cock-suga",
        "tuppar",
        "coon",
        "skit",
        "sperma",
        "cumshot",
        "cunillingus",
        "fitta",
        "attans",
        "dildo",
        "dildos",
        "dink",
        "hund-fucker",
        "duche",
        "fördämning",
        "ejakulat",
        "ejakulerade",
        "utlösning",
        "ejakulation",
        "bög",
        "fagging",
        "faggots",
        "rumpa",
        "felching",
        "fellatio",
        "fläns",
        "knulla",
        "körd",
        "fucker",
        "fuckers",
        "jävla",
        "fuckings",
        "fucks",
        "fudge packer",
        "god-damned",
        "helvete",
        "hore",
        "kåt",
        "jerk-off",
        "kock",
        "blygdläppar",
        "lusta",
        "lusting",
        "masochist",
        "onanera",
        "mamma fucker",
        "nazist",
        "nigger",
        "niggers",
        "orgasim",
        "orgasm",
        "orgasmer",
        "pecker",
        "penis",
        "piss",
        "förbannad",
        "pisser",
        "pisses",
        "pissing",
        "dra åt helvete",
        "bajs",
        "porr",
        "pornografi",
        "pube",
        "mesar",
        "våldta",
        "våldtäktsman",
        "ändtarm",
        "hämma",
        "rimming",
        "sadist",
        "skruvning",
        "scrotum",
        "sädesvätska",
        "sex",
        "shag",
        "shagging",
        "shemale",
        "shite",
        "shits",
        "shitted",
        "shitting",
        "shitty",
        "skank",
        "slampa",
        "sluts",
        "smegma",
        "smut",
        "ryck",
        "son-of-a-tik",
        "spac",
        "testikel",
        "mes",
        "titt",
        "vagina",
        "viagra",
        "vulva",
        "wang",
        "wank",
        "hora",
        "x betygsatt",
        "xxx"
    ]
}

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

def generate_inflections(df):
    if len(df) == 0:
        return df

    df["swedish_inflections"] = df.apply(lambda x: swe_inflections(x.swe_lemma, x.agreed_pos), axis=1)
    df["english_inflections"] = df.apply(lambda x: eng_inflections(x.eng_lemma, x.agreed_pos), axis=1)

    return df
def clean_pos(df):
    df.fillna('', inplace=True)
    df.loc[df['POS'] == 'no pos found', 'POS'] = ''

    def has_multiple_words(row):
        return ' ' in row['Swedish lemma'] or ' ' in row['English lemma']

    # Apply the function to update 'POS' column
    df.loc[df.apply(has_multiple_words, axis=1) & (df['POS'] != ''), 'POS'] = 'NP'
    return df

def check_for_banned_words(df):
    def contains_banned_word(text, banned_words):
        words = text.split()
        for word in words:
            if word in banned_words:
                return True
        return False
    df['contains_banned'] = df['eng_lemma'].apply(lambda x: contains_banned_word(x, banned_words["en"]))

    df.loc[~df['contains_banned'], "contains_banned"] = df['swe_lemma'].apply(lambda x: contains_banned_word(x, banned_words["sv"]))

    df.loc[~df['contains_banned'], "contains_banned"] = df['src'].apply(lambda x: contains_banned_word(x, banned_words["en"] + banned_words["sv"]))

    return df
# TODO: add checking if term already exist
def term_already_exists(existing_terms, new_term):
    term = (new_term["eng_lemma"], new_term["swe_lemma"], new_term["agreed_pos"], new_term["src"])
    for existing_term in existing_terms:
        compare_term = (existing_term["entry"]["eng"]["lemma"], existing_term["entry"]["swe"]["lemma"], existing_term["entry"]["pos"])
        if term[:3] == compare_term:
            sources = existing_term["entry"]["src"].split(", ")
            if term[3] not in sources:
                existing_term["entry"]["src"] = existing_term["entry"]["src"] + ", " + new_term["src"]
                key = os.getenv('KARP_API_KEY')
                update_posts_via_api_key(existing_term["id"], existing_term["entry"], existing_term["version"], key, verbose=True)
            return True
    return False

        


def main():
    # CHANGE : Ändra inläsning --> läsa in från var/lib/stunda/terms/unprocessed
    parser = argparse.ArgumentParser(description="Automatically process english-swedish computer science term pairs")
    parser.add_argument("-s", "--strings", nargs=3, help="Two term pairs")
    parser.add_argument("-f", "--file", help="Input txt file")
    parser.add_argument("-jf", "--jsonfile", help="Input json file")
    parser.add_argument("-jfl", "--jsonlfile", help="Input jsonl file")
    parser.add_argument("-srv", "--server",action="store_true", help="flag for indicatig the file is being run on the server")


    args = parser.parse_args()

    single_input = False

    term_pairs = []

    df = None
    og_df = None

    if args.strings:
        load_dotenv()
        term_pairs.append({"eng_lemma" : args.strings[0], "swe_lemma": args.strings[1], "src": args.strings[2]})
        single_input = True
        df = pd.DataFrame(term_pairs)
    elif args.file:
        load_dotenv()
        with open(args.file, 'r', encoding='utf-8') as file:
            term_pairs = file.readlines()
            term_pairs = [{'eng_lemma' : term_pair.rstrip().split(',')[0], 'swe_lemma': term_pair.rstrip().split(',')[1], "src": term_pair.rstrip().split(',')[2]} for term_pair in term_pairs]
        df = pd.DataFrame(term_pairs)
    elif args.jsonfile:
        load_dotenv()
        with open(args.jsonfile, 'r', encoding='utf-8') as file:
            # Load JSON data from the file
            data = json.load(file)
            for key, value in data.items():
                for swe_term in value:
                    term_pairs.append({"eng_lemma": key, "swe_lemma": swe_term, "src":"paired keywords"})
        df = pd.DataFrame(term_pairs)
    elif args.jsonlfile:
        load_dotenv()
        with open(args.jsonlfile, 'r', encoding='utf-8') as file:
            # Iterate through each line in the file
            for line in file:
                # Load the JSON object from the line
                data = json.loads(line)
                term_pairs.append({"eng_lemma": data["eng"]["lemma"], "swe_lemma":data["swe"]["lemma"], "src": data["src"]})
            df = pd.DataFrame(term_pairs)
    elif args.server:
        load_dotenv(dotenv_path="/var/lib/stunda/data/.env")
        df = pd.read_csv("/var/lib/stunda/terms_test/unprocessed.csv", encoding='utf-8')
        og_df = df.copy()
        from datetime import datetime

        # Get the current date and time
        now = datetime.now()

        # Format as a string
        datetime_string = now.strftime('%Y-%m-%d %H:%M:%S')

        df.to_csv(f"/var/lib/stunda/historical_processed/unprocessed_{datetime_string}.csv", index=False, encoding="utf-8")
    else:
        print("Missing or incorrect arguments")
        exit(1)

    t0 = time.time()

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

    # Drop duplicate entries over swedish lemma, engish lemma, pos and source
    df = df.drop_duplicates(subset=["eng_lemma", "swe_lemma", "agreed_pos", "src"])

    # Aggregate the sources
    aggregated_sources_df = df.groupby(["swe_lemma", "eng_lemma", "agreed_pos"])["src"].apply(lambda x: ", ".join(x)).reset_index()  
    df = df.drop(columns="src").drop_duplicates() 
    df = df.merge(aggregated_sources_df, on=["swe_lemma", "eng_lemma", "agreed_pos"])

    # Generera böjningsformer
    df = generate_inflections(df)

    # Concatenate all parts and calculate total processing time
    output_df = pd.concat([df_stop1, df_stop2, df_stop3, df])

    # CHANGE : Lägg till bannade ord att tas bort, (kolla termer, källa) lägg in dessa poster i var/lib/stunda/terms/banned
    output_df = check_for_banned_words(output_df)

    # CHANGE: Kolla dubletter, om dublett --> lägg till källan till posten, flagga automatiskt OK och lägg i var/lib/stunda/terms/approved
    # TODO skippa entries med bannade ord och tilldela dessa false för att termen inte existerar
    existing_terms = get_all()["hits"]

    output_df["already_exist"] = False

    output_df.loc[~output_df.contains_banned, "already_exist"] = output_df.loc[~output_df.contains_banned].apply(lambda x: term_already_exists(existing_terms, x), axis=1)

    total_time = time.time() - t0
    print("Total processing time: {:.2f} minutes".format(total_time/60))

    # CHANGE : Lägg behandlade ord i var/lib/stunda/terms/processed
    if args.server or False:
        def set_reason(status):
            if status == "automatically verified":
                return ""
            else:
                return status

        output_df["reason"] = output_df["status"].apply(set_reason)

        output_df.loc[~(output_df.status == "automatically verified"), "status"] = "not automatically verified"
        
        df_banned = output_df.loc[output_df.contains_banned]
        df_exist_already = output_df.loc[output_df.already_exist]
        df_new_terms = output_df.loc[(~output_df.contains_banned) & (~output_df.already_exist)]

        columns_to_save = ["eng_lemma", "swe_lemma", "src", "status", "agreed_pos", "swedish_inflections", "english_inflections", "reason"]

        # Converting the selected DataFrame to a list of JSON objects
        jsonl_banned = json.loads(df_banned[columns_to_save].to_json(orient="records", force_ascii=False))

        with open("/var/lib/stunda/terms_test/banned.jsonl", 'a', encoding='utf-8') as file:
            for item in jsonl_banned:
                json_line = json.dumps(item, ensure_ascii=False) + '\n'
                file.write(json_line)

        # Converting the selected DataFrame to a list of JSON objects
        jsonl_new_terms = json.loads(df_new_terms[columns_to_save].to_json(orient="records", force_ascii=False))
        
        with open("/var/lib/stunda/terms_test/processed.jsonl", 'a', encoding='utf-8') as file:
            for item in jsonl_new_terms:
                json_line = json.dumps(item, ensure_ascii=False) + '\n'
                file.write(json_line)

        # Converting the selected DataFrame to a list of JSON objects
        jsonl_existing_terms = json.loads(df_exist_already[columns_to_save].to_json(orient="records", force_ascii=False))

        with open("/var/lib/stunda/terms_test/approved.jsonl", 'a', encoding='utf-8') as file:
            for item in jsonl_existing_terms:
                json_line = json.dumps(item, ensure_ascii=False) + '\n'
                file.write(json_line)

        og_df.head(0).to_csv("/var/lib/stunda/terms_test/unprocessed.csv", index=False, encoding='utf-8')
    else:
        if single_input:
            print("English lemma:", output_df.at[0, "eng_lemma"])
            print("Swedish lemma:", output_df.at[0, "swe_lemma"])
            print("Status       :", output_df.at[0, "status"])
            if 'agreed_pos' in output_df.columns and len(output_df.at[0, "eng_lemma"].split(" ")) == 1 and len(output_df.at[0, "swe_lemma"].split(" ")) == 1:
                print("POS          :", output_df.at[0, "agreed_pos"])
            print(df)
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

    
