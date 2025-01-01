import pandas as pd
from geopy.distance import geodesic
from geopy.distance import great_circle
import time

class QuadTree:
    def __init__(self, bounds, max_points=4):
        self.bounds = bounds  # (xmin, ymin, xmax, ymax)
        self.max_points = max_points
        self.points = []
        self.children = None

    def subdivide(self):
        xmin, ymin, xmax, ymax = self.bounds
        midx = (xmin + xmax) / 2
        midy = (ymin + ymax) / 2
        self.children = [
            QuadTree((xmin, ymin, midx, midy), self.max_points),  # Bottom-left
            QuadTree((midx, ymin, xmax, midy), self.max_points),  # Bottom-right
            QuadTree((xmin, midy, midx, ymax), self.max_points),  # Top-left
            QuadTree((midx, midy, xmax, ymax), self.max_points),  # Top-right
        ]

    def insert(self, point):
        if not self.in_bounds(point):
            return False
        if len(self.points) < self.max_points:
            self.points.append(point)
            return True
        if not self.children:
            self.subdivide()
        for child in self.children:
            if child.insert(point):
                return True

    def in_bounds(self, point):
        x, y = point
        xmin, ymin, xmax, ymax = self.bounds
        return xmin <= x <= xmax and ymin <= y <= ymax

    def query(self, point, best=None, best_dist=float('inf')):
        if not self.in_bounds(point):
            return best, best_dist
        for p in self.points:
            dist = geodesic((point[0], point[1]), (p[0], p[1])).meters
            if dist < best_dist:
                best, best_dist = p, dist
        if self.children:
            for child in self.children:
                best, best_dist = child.query(point, best, best_dist)
        return best, best_dist
def main():
    start_time = time.time()

    df = pd.read_csv(f'./exo/shapes.txt')
    sub_df = df[df.shape_id.isin([10217])]
    if 'shape_pt_sequence' in df.columns:
        sub_df = sub_df.sort_values(by='shape_pt_sequence')
    lat_lon_list = sub_df[['shape_pt_lat', 'shape_pt_lon']].values.tolist()

    # Calculate min and max latitude/longitude from your dataset
    min_lat = sub_df['shape_pt_lat'].min()
    max_lat = sub_df['shape_pt_lat'].max()
    min_lon = sub_df['shape_pt_lon'].min()
    max_lon = sub_df['shape_pt_lon'].max()

    print(f"Min Latitude: {min_lat}, Max Latitude: {max_lat}")
    print(f"Min Longitude: {min_lon}, Max Longitude: {max_lon}")

    bounds = (min_lat-1, min_lon-1,  max_lat+1,max_lon+1)
    # bounds = (-180, -90, 180, 90)  # World bounds for latitude and longitude

    quad_tree = QuadTree(bounds)

    for point in lat_lon_list:
        quad_tree.insert(point)

    df = pd.read_csv('./exo/stops.txt')
    for index, row in df.iterrows():
        # Accessing values in each row
        shape_id = row['stop_name']
        lat = row['stop_lat']
        lon = row['stop_lon']
        stop = (lat,lon)
        nearest, distance = quad_tree.query(stop)
        print(f"Nearest point for {shape_id}: {nearest}, Distance: {distance:.2f} meters")

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Execution time: {execution_time:.4f} seconds")

main()
