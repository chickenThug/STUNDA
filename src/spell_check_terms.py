import json
import requests

# Skrutten Stava API
def spell_check(words, coding='json'):
    url = 'https://skrutten.csc.kth.se/granskaapi/spell/'

    if isinstance(words, list):
        words = '\n'.join(words)

    params = {'coding': coding, 'words': words}

    response = requests.post(url, data=params)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return None

# Swedish term file
file_path = 'public_data/list_of_swedish_terms.txt'

with open(file_path, 'r', encoding='utf-8') as file:
    words = file.read().split()

# Spell check all the words
checked_spelling = spell_check(words)

# Words with incorrect spelling
incorrect_spellings = [item for item in checked_spelling if not item['correct']]

print(len(checked_spelling))
print(len(incorrect_spellings))

# Save incorrectly spelled words to json-file
'''
output_file_path = 'incorrectly_spelled_swedish_terms.json'

def save_results_to_file(results, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for word_result in results:
            file.write(json.dumps(word_result, ensure_ascii=False) + '\n')

save_results_to_file(incorrect_spellings, output_file_path)
'''