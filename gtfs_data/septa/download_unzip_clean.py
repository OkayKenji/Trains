import requests
import zipfile
import os

url = 'http://www3.septa.org/developer/google_rail.zip'
file_name = 'gtfssepta.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfssepta.zip'
extract_to = './gtfs_data/septa'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("rm gtfssepta.zip")