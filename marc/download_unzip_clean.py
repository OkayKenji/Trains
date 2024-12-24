import requests
import zipfile
import os
import pandas as pd

url = 'https://feeds.mta.maryland.gov/gtfs/marc'
file_name = 'gtfsmarc.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfsmarc.zip'
extract_to = './marc'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("rm gtfsmarc.zip")


df = pd.read_csv('./marc/stops.txt')
df['stop_name'] = df['stop_name'].str.replace(r'DUFFIELFS', 'DUFFIELDS', regex=True)

df['stop_name_trimmed'] = df['stop_name'].str[:-2]
final_result = []

processed_rows = set()

for idx, row in df.iterrows():
    group = df[df['stop_name_trimmed'] == row['stop_name_trimmed']]

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

final_df = final_df.drop_duplicates(subset='stop_name_trimmed', keep='first')

final_df['stop_name'] = df['stop_name'].str.replace(r'(sb|nb|wb|eb)$', '', regex=True)

# Step 1: Identify the row(s) where stop_name is "UNION STATION MARC Washington"
row_to_move = final_df[final_df['stop_name'] == "UNION STATION MARC Washington"]

if row_to_move.empty:
    print("Row not found.")
else:
    final_df = final_df[final_df['stop_name'] != "UNION STATION MARC Washington"]
    
    final_df = pd.concat([final_df, row_to_move]).reset_index(drop=True)

final_df.to_csv('./marc/stops.txt', index=False)
