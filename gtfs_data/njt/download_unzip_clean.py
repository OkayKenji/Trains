import requests
import zipfile
import os

url = 'https://www.njtransit.com/rail_data.zip'
file_name = 'gtfsnjt.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfsnjt.zip'
extract_to = './gtfs_data/njt'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("cp ./gtfs_data/njt/stopsSorted.txt ./gtfs_data/njt/stops.txt")
os.system("rm gtfsnjt.zip")