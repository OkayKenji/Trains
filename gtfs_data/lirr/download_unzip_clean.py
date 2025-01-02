import requests
import zipfile
import os

url = 'https://rrgtfsfeeds.s3.amazonaws.com/gtfslirr.zip'
file_name = 'gtfslirr.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfslirr.zip'
extract_to = './gtfs_data/lirr'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("cp ./gtfs_data/lirr/stopsSorted.txt ./gtfs_data/lirr/stops.txt")
os.system("rm gtfslirr.zip")