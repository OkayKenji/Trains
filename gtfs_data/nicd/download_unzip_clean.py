import requests
import zipfile
import os

url = 'http://www.mysouthshoreline.com/google/google_transit.zip'
file_name = 'gtfsnicd.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfsnicd.zip'
extract_to = './gtfs_data/nicd'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("rm gtfsnicd.zip")