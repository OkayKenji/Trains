import requests
import zipfile
import os

url = 'https://corporate.sunrail.com/gtfs/google_transit.zip'
file_name = 'gtfssunrail.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfssunrail.zip'
extract_to = './sunrail'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("rm gtfssunrail.zip")