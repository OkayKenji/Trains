import requests
import zipfile
import os
import pandas as pd

url = 'https://schedules.metrarail.com/gtfs/schedule.zip'
file_name = 'gtfsmetra.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfsmetra.zip'
extract_to = './gtfs_data/metra'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("rm gtfsmetra.zip")

files_to_fix = ["agency","calendar_dates","calendar","routes","shapes","stop_times","stops","trips"]

for file in files_to_fix:
    df = pd.read_csv(f'./gtfs_data/metra/{file}.txt')
    df.columns = df.columns.str.strip()
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    df.to_csv(f'./gtfs_data/metra/{file}.txt',index=False)

