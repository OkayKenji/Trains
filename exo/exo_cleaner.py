import pandas as pd

# Read the data
df = pd.read_csv('./exo/stops.txt')

# Identify duplicates based on stop_name, stop_lat, and stop_lon
duplicates = df.groupby(['stop_name']).agg({'stop_id': list}).reset_index()

# To preserve the original order, we'll iterate over the original dataframe
final_result = []

# Keep track of the already processed stop_ids to avoid duplicates
processed_stop_ids = set()

for _, group in duplicates.iterrows():
    group_data = df[(df['stop_name'] == group['stop_name'])]
    
    # Process the rows in their original order (preserving order)
    for idx, row in group_data.iterrows():
        stop_id = row['stop_id']
        
        # If this stop_id has already been processed, skip it
        if stop_id in processed_stop_ids:
            continue
        
        # Mark this stop_id as processed
        processed_stop_ids.add(stop_id)
        
        # First occurrence (no need to change), update the station_id_additional column
        if len(group['stop_id']) > 1:
            row['station_id_additional'] = str(group['stop_id'][1:]).replace('[','["').replace(']','"]')
        else:
            row['station_id_additional'] = "[]"
        
        final_result.append(row)

# Convert final_result back into a DataFrame
final_df = pd.DataFrame(final_result)

# Save the cleaned DataFrame back to CSV, keeping the original order
final_df.to_csv('./exo/stops.txt', index=False)

# Print the cleaned DataFrame
print(final_df)
