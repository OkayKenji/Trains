import pandas as pd

df = pd.read_csv('./gtfs_data/rtd/RTD_Denver_Purchased_Transportation_Commuter_Rail_GTFS/stops.txt')
df1 = df[pd.isna(df['parent_station'])] 
df2 = df[~pd.isna(df['parent_station'])]  
df2 = df2.astype({'parent_station' : 'int'})
df2 = df2.astype({'parent_station' : 'str'})
df1 = df1.astype({'stop_id' : 'int'})
df1 = df1.astype({'stop_id' : 'str'})
df1['station_id_additional'] = [['-1'] for _ in range(len(df1))]
for index, row in df2.iterrows():
    df1.loc[df1['stop_id'] == row['parent_station'], 'station_id_additional'] = df1.loc[df1['stop_id'] == row['parent_station'], 'station_id_additional']        .apply(lambda x: x + [str(row['stop_id'])])  # Convert stop_id to string

final_result = []

processed_rows = set()

for idx, row in df1.iterrows():
    group = df1[df1['stop_name'] == row['stop_name']]
    
    if row['stop_name'] in processed_rows:
        continue
    
    processed_rows.add(row['stop_name'])

    additional_ids = group['stop_id'].tolist()[1:]  # All but the first stop_id
    if additional_ids:
        additional_ids.append("-1")
        row['station_id_additional'] = str(additional_ids)

    # else:
    #     row['station_id_additional'] = "[]"
    
    final_result.append(row)

final_df = pd.DataFrame(final_result)

final_df = final_df.drop_duplicates(subset='stop_name', keep='first')

df_sorted = pd.read_csv('./gtfs_data/rtd/RTD_Denver_Purchased_Transportation_Commuter_Rail_GTFS/stopsSorted.txt')
final_df = final_df.set_index('stop_name').loc[df_sorted['stop_name']].reset_index()
final_df.to_csv('./gtfs_data/rtd/RTD_Denver_Purchased_Transportation_Commuter_Rail_GTFS/stops.txt', index=False)
