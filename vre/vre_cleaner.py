import pandas as pd
import math

df = pd.read_csv('./vre/stops.txt')

df1 = df[pd.isna(df['parent_station'])] 
df2 = df[~pd.isna(df['parent_station'])]  
df1['station_id_additional'] = [[] for _ in range(len(df1))]  # Create an empty list for each row

for index, row in df2.iterrows():
    df1.loc[df1['stop_id'] == row['parent_station'], 'station_id_additional'] = df1.loc[df1['stop_id'] == row['parent_station'], 'station_id_additional'].apply(lambda x: x + [row['stop_id']])

df1 = df1[df1['stop_name'] != 'ServiceAlerts']
df1 = df1[df1['stop_name'] != 'TestPlayer1']
df1 = df1[df1['stop_name'] != 'Station Monitor']

print(df1)
print(df1.to_csv('./vre/stops.txt'))

#  