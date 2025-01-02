import requests
import zipfile
import os
import pandas as pd

url = 'https://content.amtrak.com/content/gtfs/GTFS.zip'
file_name = 'gtfsamtrak.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfsamtrak.zip'
extract_to = './amtrak'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("rm gtfsamtrak.zip")

df = pd.read_csv('./amtrak/stops.txt')
df['stop_name'] = df['stop_name'] + " - " + df['stop_id']
df.to_csv("./amtrak/stops.txt",index=False)