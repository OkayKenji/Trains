import requests
import zipfile
import os

url = 'https://www.viarail.ca/sites/all/files/gtfs/viarail.zip'
file_name = 'gtfsvia.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfsvia.zip'
extract_to = './gtfs_data/via'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("rm gtfsvia.zip")