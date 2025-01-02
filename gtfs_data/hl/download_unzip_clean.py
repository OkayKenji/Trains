import requests
import zipfile
import os
import pandas as pd

url = 'https://ctrides.com/hlgtfs.zip'
file_name = 'gtfshl.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfshl.zip'
extract_to = './hl'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("rm gtfshl.zip")
