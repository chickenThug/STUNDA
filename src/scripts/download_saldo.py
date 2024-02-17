import requests

url = "https://svn.spraakdata.gu.se/sb-arkiv/pub/lmf/saldo/saldo.xml"  # Replace this with the actual URL

response = requests.get(url)

if response.status_code == 200:  # 200 indicates success
    with open("data/saldo.xml", "wb") as f:
        f.write(response.content)
    print("File downloaded successfully!")
else:
    print("Failed to download file:", response.status_code)