import requests
import zipfile
import os

url = 'https://metrolinktrains.com/globalassets/about/gtfs/gtfs.zip'
file_name = 'gtfsmetrolink.zip'

# Custom headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive'
}

response = requests.get(url, headers=headers)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfsmetrolink.zip'
extract_to = './metrolink'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("rm *.zip")