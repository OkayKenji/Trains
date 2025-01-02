import pandas as pd
import requests
import zipfile
import os
url = 'https://assets.metrolinx.com/raw/upload/Documents/Metrolinx/Open%20Data/GO-GTFS.zip'
file_name = 'gtfsgo.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfsgo.zip'
extract_to = './gtfs_data/go'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

# os.system("cp ./gtfs_data/go/stopsSorted.txt ./gtfs_data/go/stops.txt")
os.system("rm gtfsgo.zip")

df = pd.read_csv('./gtfs_data/go/routes.txt')
df = df[pd.to_numeric(df['route_short_name'], errors='coerce').isna()]
df.to_csv("./gtfs_data/go/routes.txt",index=False)
route_list = df['route_id'].to_list()

df = pd.read_csv('./gtfs_data/go/trips.txt')
df = df[df['route_id'].isin(route_list)]
df.to_csv("./gtfs_data/go/trips.txt",index=False)

service_list = list(set(df['service_id'].to_list()))
trip_list = list(set(df['trip_id'].to_list()))

df = pd.read_csv('./gtfs_data/go/calendar.txt')
df = df[df['service_id'].isin(service_list)]
df.to_csv("./gtfs_data/go/calendar.txt",index=False)

df = pd.read_csv('./gtfs_data/go/stop_times.txt')
df = df[df['trip_id'].isin(trip_list)]
df.to_csv("./gtfs_data/go/stop_times.txt",index=False)
stop_list = list(set(df['stop_id'].to_list()))


df = pd.read_csv('./gtfs_data/go/stops.txt')
df = df[df['stop_id'].isin(stop_list)]
df.to_csv("./gtfs_data/go/stops.txt",index=False)

df_sorted = pd.read_csv('./gtfs_data/go/stopsSorted.txt')

df = df.set_index('stop_name').loc[df_sorted['stop_name']].reset_index()
df.to_csv('./gtfs_data/go/stops.txt',index=False)
