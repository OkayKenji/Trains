import pandas as pd

# Read the data
df = pd.read_csv('./exo/stops.txt')

# Initialize a list to store the cleaned result
final_result = []

# Keep track of the already processed rows to avoid adding duplicates
processed_rows = set()

# Iterate through the dataframe, preserving the original order
for idx, row in df.iterrows():
    # Identify the group (by stop_name)
    group = df[df['stop_name'] == row['stop_name']]
    
    # If this group has been processed before, skip adding duplicates
    if row['stop_name'] in processed_rows:
        continue
    
    # Mark this stop_name as processed
    processed_rows.add(row['stop_name'])
    
    # If there are duplicates (more than one stop_id in the group), 
    # move extra stop_ids to the 'station_id_additional' column
    additional_ids = group['stop_id'].tolist()[1:]  # All but the first stop_id
    if additional_ids:
        row['station_id_additional'] = str(additional_ids).replace('[','"[').replace(']',']"')
    else:
        row['station_id_additional'] = "[]"
    
    # Add the first occurrence (with the 'station_id_additional' column updated) to the final result
    final_result.append(row)

# Convert the final result into a DataFrame
final_df = pd.DataFrame(final_result)


final_df = final_df.drop_duplicates(subset='stop_name', keep='first')

# Save the cleaned DataFrame back to CSV, keeping the original order
final_df.to_csv('./exo/stops.txt', index=False)

# Print the cleaned DataFrame
print(final_df)
