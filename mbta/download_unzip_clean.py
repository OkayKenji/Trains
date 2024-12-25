import pandas as pd

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
df1 = df[pd.isna(df['parent_station'])] 
df2 = df[~pd.isna(df['parent_station'])]  
df1['station_id_additional'] = [[] for _ in range(len(df1))]

for index, row in df2.iterrows():
    df1.loc[df1['stop_id'] == row['parent_station'], 'station_id_additional'] = df1.loc[df1['stop_id'] == row['parent_station'], 'station_id_additional'].apply(lambda x: x + [row['stop_id']])
df1.to_csv('./mbta/stops.txt',index=False)
# commuter_rail
# cr_foxboro
# cape_flyer