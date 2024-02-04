import requests
import json
from utils import get_all

# Define the URL endpoint you want to make a GET request to
resource_id = "stunda"
url =  f"https://ws.spraakbanken.gu.se/ws/karp/v7/query/split/stunda?q="

headers = {
    'Authorization': "Bearer " + json.load(open('data/secrets.json')).get("jwt_token", ""),
    'Content-Type': 'application/json',
    "entry_id": "01GX3DS1HJBMF7DNCJCQW9E6N3",}

params = {
    "size" : 10000
}


# Make the GET request
response = requests.get(url, headers=headers, params=params)


# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Print the response content
    data = response.json()  # Assuming the response is in JSON format
else:
    print('Error:', response.status_code)


list_of_entries = data["hits"]["stunda"]



delete_url = f"https://ws.spraakbanken.gu.se/ws/karp/v7/entries/stunda/"

print(data.keys())
i = 0
for entry in list_of_entries:
    i += 1
    post = entry["entry"]
    if post.get("src", "") == "Viggo":
        print(post)
        extension = entry["id"] + "/1.1"
        print(delete_url + extension)
        response = requests.delete(delete_url + extension, headers=headers)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
        # Print the response content
            print(response.json())  # Assuming the response is in JSON format
        else:
            print('Error:', response.status_code)

print("total processed", i)


