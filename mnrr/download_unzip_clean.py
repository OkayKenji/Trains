import requests
import zipfile
import os

url = 'https://rrgtfsfeeds.s3.amazonaws.com/gtfsmnr.zip'
file_name = 'gtfsmnrr.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfsmnrr.zip'
extract_to = './mnrr'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("rm *.zip")