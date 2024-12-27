import requests
import zipfile
import os
import pandas as pd

url = 'https://cdn.mbta.com/MBTA_GTFS.zip'
file_name = 'gtfsmbta.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfsmbta.zip'
extract_to = './mbta'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("rm gtfsmbta.zip")




df = pd.read_csv('./mbta/routes.txt')
df = df.drop(df[(df.network_id != "commuter_rail") & (df.network_id != "cr_foxboro") & (df.network_id != "cape_flyer")].index)
df.to_csv("./mbta/routes.txt",index=False)
route_list = df['route_id'].to_list()
print(route_list)

df = pd.read_csv('./mbta/trips.txt')
df = df[df['route_id'].isin(route_list)]
df.to_csv("./mbta/trips.txt",index=False)

service_list = list(set(df['service_id'].to_list()))
trip_list = list(set(df['trip_id'].to_list()))

df = pd.read_csv('./mbta/calendar.txt')
df = df[df['service_id'].isin(service_list)]
df.to_csv("./mbta/calendar.txt",index=False)

df = pd.read_csv('./mbta/stop_times.txt')
df = df[df['trip_id'].isin(trip_list)]
df.to_csv("./mbta/stop_times.txt",index=False)


df = pd.read_csv('./mbta/stops.txt')
print(len(df))
df = df[(df["zone_id"] != "LocalBus") & (df["zone_id"] != "ExpressBus-Downtown") & (df["stop_url"].notna())]
df.to_csv('e.csv',index=False)
print(len(df))

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

final_df.to_csv("./mbta/stops.txt",index=False)