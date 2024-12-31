from sklearn.neighbors import NearestNeighbors
from geopy.distance import geodesic
import numpy as np
import pandas as pd
df = pd.read_csv('./mnrr/shapes.txt')
sub_df = df[df.shape_id.isin([14])]
if 'shape_pt_sequence' in df.columns:
    sub_df = sub_df.sort_values(by='shape_pt_sequence')
lat_lon_list = sub_df[['shape_pt_lat', 'shape_pt_lon']].values.tolist()



stop = ()

# Sample data: shape points (latitude, longitude)
shape_points = np.array(lat_lon_list)

# Query point (stop) to find the nearest shape point
stop = np.array([[40.958997,-73.820564]])  # Some stop in New York

# Initialize NearestNeighbors with 1 nearest neighbor and geodesic distance
nbrs = NearestNeighbors(n_neighbors=1, metric='euclidean')
nbrs.fit(shape_points)

# Find nearest shape point to the stop
distances, indices = nbrs.kneighbors(stop)

# Output
nearest_shape = shape_points[indices[0][0]]
nearest_distance = geodesic((stop[0][0], stop[0][1]), (nearest_shape[0], nearest_shape[1])).meters
print(f"Nearest point: {nearest_shape}, Distance: {nearest_distance:.2f} meters")
