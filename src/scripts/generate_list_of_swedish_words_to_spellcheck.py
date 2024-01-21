import json


path = "../data/"
file = "stunda-terms-processed.jsonl"

def read_jsonl_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            # Load each line as a JSON object
            json_object = json.loads(line)
            data.append(json_object)
    return data


data = read_jsonl_file(path + file)


with open("../public_data/list_of_swedish_terms.txt", 'w') as file:
    # Write lemma and its inflections to file for spell check purposes
    written_words = {}
    for entry in data:
        if entry["status"] == "1":
            for word in entry["swe"]["lemma"].split(" "):
                word = word.strip()
                if written_words.get(word) is None:
                    file.write(word + ' ')
                    written_words[word] = True
            for term in entry["swe"]["inflection"]:
                for word in term.split(" "):
                    if written_words.get(word) is None:
                        file.write(word + ' ')
                        written_words[word] = True