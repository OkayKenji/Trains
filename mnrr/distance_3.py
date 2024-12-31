import pandas as pd
from geopy.distance import great_circle
from geopy.distance import geodesic
import time
start_time = time.time()


df = pd.read_csv('./mnrr/shapes.txt')
sub_df = df[df.shape_id.isin([14])]
if 'shape_pt_sequence' in df.columns:
    sub_df = sub_df.sort_values(by='shape_pt_sequence')
# lat_lon_list = sub_df[['shape_pt_lat', 'shape_pt_lon']].values.tolist()

df = pd.read_csv('./mnrr/stops.txt')
for index, row in df.iterrows():
    # Accessing values in each row
    shape_id = row['stop_name']
    latee = row['stop_lat']
    lonee = row['stop_lon']
    stop = (latee,lonee)
        # Stop location

    # Variables to store the closest point and distance
    closest_point = None
    min_distance = float('inf')  # Start with an infinitely large distance

    # Loop through each row in the DataFrame
    for index, row in sub_df.iterrows():
        # Get the latitude and longitude of the shape point
        lat, lon = float(row['shape_pt_lat']), float(row['shape_pt_lon'])
        
        # Calculate the distance from the stop to the current shape point
        distance = geodesic((lat, lon), stop).meters
        
        # Check if the current distance is smaller than the minimum distance
        if distance < min_distance:
            min_distance = distance
            closest_point = (lat, lon)
    print(f"Nearest point for {shape_id}: {closest_point}, Distance: {min_distance:.2f} meters")

end_time = time.time()
execution_time = end_time - start_time

print(f"Execution time: {execution_time:.4f} seconds")