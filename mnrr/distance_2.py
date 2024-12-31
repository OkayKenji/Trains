from sklearn.neighbors import NearestNeighbors
from geopy.distance import geodesic
import numpy as np
import pandas as pd
import time
start_time = time.time()


df = pd.read_csv('./mnrr/shapes.txt')
sub_df = df[df.shape_id.isin([14])]
if 'shape_pt_sequence' in df.columns:
    sub_df = sub_df.sort_values(by='shape_pt_sequence')
lat_lon_list = sub_df[['shape_pt_lat', 'shape_pt_lon']].values.tolist()



stop = ()

# Sample data: shape points (latitude, longitude)
shape_points = np.array(lat_lon_list)

# Query point (stop) to find the nearest shape point


# Custom geodesic distance function for NearestNeighbors
def geodesic_distance(x, y):
    return geodesic((x[0], x[1]), (y[0], y[1])).meters

# Create the NearestNeighbors model with custom metric
nbrs = NearestNeighbors(n_neighbors=1, metric=geodesic_distance)
nbrs.fit(shape_points)

df = pd.read_csv('./mnrr/stops.txt')
for index, row in df.iterrows():
    # Accessing values in each row
    shape_id = row['stop_name']
    lat = row['stop_lat']
    lon = row['stop_lon']
    stop = np.array([[lat,lon]])  # Some stop in New York


    # Find nearest shape point to the stop
    distances, indices = nbrs.kneighbors(stop)

    # Output
    nearest_shape = shape_points[indices[0][0]]
    nearest_distance = geodesic((stop[0][0], stop[0][1]), (nearest_shape[0], nearest_shape[1])).meters
    print(f"Nearest point for {shape_id}: {nearest_shape}, Distance: {nearest_distance:.2f} meters")


end_time = time.time()
execution_time = end_time - start_time

print(f"Execution time: {execution_time:.4f} seconds")