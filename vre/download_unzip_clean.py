import requests
import zipfile
import os
import pandas as pd

url = 'https://gtfs.vre.org/containercdngtfsupload/google_transit.zip'
file_name = 'gtfsvre.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfsvre.zip'
extract_to = './vre'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("rm gtfsvre.zip")

df = pd.read_csv('./vre/stops.txt')
df1 = df[pd.isna(df['parent_station'])] 
df2 = df[~pd.isna(df['parent_station'])]  
df1['station_id_additional'] = [[] for _ in range(len(df1))]

for index, row in df2.iterrows():
    df1.loc[df1['stop_id'] == row['parent_station'], 'station_id_additional'] = df1.loc[df1['stop_id'] == row['parent_station'], 'station_id_additional'].apply(lambda x: x + [row['stop_id']])

df1 = df1[df1['stop_name'] != 'ServiceAlerts']
df1 = df1[df1['stop_name'] != 'TestPlayer1']
df1 = df1[df1['stop_name'] != 'Station Monitor']

df_sorted = pd.read_csv('./vre/stopsSorted.txt')

df1 = df1.set_index('stop_name').loc[df_sorted['stop_name']].reset_index()

df1.to_csv('./vre/stops.txt',index=False)

