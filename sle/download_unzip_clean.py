import requests
import zipfile
import os
import pandas as pd

url = 'https://content.amtrak.com/content/gtfs/GTFS.zip'
file_name = 'gtfssle.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfssle.zip'
extract_to = './sle'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("rm gtfssle.zip")

df = pd.read_csv('./sle/agency.txt')
df = df[df.agency_name == "Shore Line East"]
df.to_csv("./sle/agency.txt",index=False)
agency_id_list = df['agency_id'].to_list()

df = pd.read_csv('./sle/routes.txt')
df = df[df['agency_id'].isin(agency_id_list)]
df.to_csv("./sle/routes.txt",index=False)
route_list = df['route_id'].to_list()
print(route_list)

df = pd.read_csv('./sle/trips.txt')
df = df[df['route_id'].isin(route_list)]
df.to_csv("./sle/trips.txt",index=False)

service_list = list(set(df['service_id'].to_list()))
trip_list = list(set(df['trip_id'].to_list()))

df = pd.read_csv('./sle/calendar.txt')
df = df[df['service_id'].isin(service_list)]
df.to_csv("./sle/calendar.txt",index=False)

df = pd.read_csv('./sle/stop_times.txt')
df = df[df['trip_id'].isin(trip_list)]
df.to_csv("./sle/stop_times.txt",index=False)
stop_list = list(set(df['stop_id'].to_list()))


df = pd.read_csv('./sle/stops.txt')
df = df[df['stop_id'].isin(stop_list)]
df.to_csv("./sle/stops.txt",index=False)

final_result = []

df['stop_name'] = df['stop_name'] + " - " + df['stop_id']


df_sorted = pd.read_csv('./sle/stopsSorted.txt')

df = df.set_index('stop_name').loc[df_sorted['stop_name']].reset_index()

df.to_csv("./sle/stops.txt",index=False)