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
final_result = []

processed_rows = set()

for idx, row in df.iterrows():
    group = df[df['stop_name'] == row['stop_name']]
    
    if row['stop_name'] in processed_rows:
        continue
    
    processed_rows.add(row['stop_name'])

    additional_ids = group['stop_id'].tolist()[1:]  # All but the first stop_id
    if additional_ids:
        row['station_id_additional'] = str(additional_ids).replace('[','"[').replace(']',']"')
    else:
        row['station_id_additional'] = "[]"
    
    final_result.append(row)

final_df = pd.DataFrame(final_result)

final_df = final_df.drop_duplicates(subset='stop_name', keep='first')

final_df.to_csv("./amtrak/stops.txt",index=False)