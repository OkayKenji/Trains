import pandas as pd
from geopy.distance import geodesic
from geopy.distance import great_circle
import logging

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

        return xmin <= float(x) <= xmax and ymin <= float(y) <= ymax

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
    
    def execute(self,stops,calculate_station):
        stop_info = stops[stops.stop_name == calculate_station]
        lat = stop_info['stop_lat'].iloc[0]
        lon = stop_info['stop_lon'].iloc[0]
        stop_lat_long = (lat,lon)
        nearest, distance = self.query(stop_lat_long)
        # print(self.bounds)

        return nearest, distance

class CalculateDistance:
    def __init__(self, shapes):
        self.shapes = shapes  
    def safe_str_conversion(self, value):
        try:
            # If the value contains 'E' (likely to be scientific notation), treat it as a string.
            if 'e' in str(value).lower():
                return str(value)  # Return the value as a string without conversion
            
            # Convert value to float first (in case it's a float or a string representation of a number)
            return str(int(float(value)))
        except ValueError:
            # If the value can't be converted to a number, return it as is (as a string)
            return str(value)
    def shape_to_dist(self,shape_id,starting_lat_long,ending_lat_long):
        sub_df = self.shapes[self.shapes.shape_id.astype(str).isin([self.safe_str_conversion(shape_id)])]
        
        logging.debug(f"{len(sub_df)}")

        if 'shape_pt_sequence' in self.shapes.columns:
            sub_df = sub_df.sort_values(by='shape_pt_sequence')
        sub_df = sub_df.reset_index() # in case sorting breaks indexing
        starting_lat, staring_long = starting_lat_long
        ending_lat, ending_long = ending_lat_long
        start_idx = sub_df[(sub_df["shape_pt_lat"] == starting_lat) & (sub_df["shape_pt_lon"] == staring_long)].index.min()
        end_idx = sub_df[(sub_df["shape_pt_lat"] == ending_lat) & (sub_df["shape_pt_lon"] == ending_long)].index.max()

        start_idx, end_idx = min(start_idx, end_idx), max(start_idx, end_idx)
        
        sub_df = sub_df.loc[start_idx:end_idx]

        

        coordinates = [(lat, lon) for lat, lon in zip(sub_df['shape_pt_lat'], sub_df['shape_pt_lon'])]
        distances = [
            geodesic(coordinates[i], coordinates[i + 1]).miles
            for i in range(len(coordinates) - 1)
        ]
        total_distance = sum(distances)
        return total_distance

class MainDistanceCalculator:
    def __init__(self, shapes, shape_distances={}):
        self.shapes = shapes
        self.shape_distances = shape_distances
    def safe_str_conversion(self, value):
        try:
            # If the value contains 'E' (likely to be scientific notation), treat it as a string.
            if 'e' in str(value).lower():
                return str(value)  # Return the value as a string without conversion
            
            # Convert value to float first (in case it's a float or a string representation of a number)
            return str(int(float(value)))
        except ValueError:
            # If the value can't be converted to a number, return it as is (as a string)
            return str(value)


    def calculate_distance(self, departure_station,arrival_station,stops,shape_id):
        if departure_station > arrival_station:
            departure_station, arrival_station = arrival_station, departure_station
        if f'{departure_station}-{arrival_station}-{shape_id}' in self.shape_distances:
            logging.info(f'Collision with: {departure_station}-{arrival_station}-{shape_id}')
            return self.shape_distances[f'{departure_station}-{arrival_station}-{shape_id}']
        else: 
            logging.info(f'First time with: {departure_station}-{arrival_station}-{shape_id}')

            if (shape_id == "NA" or shape_id == "nan" or pd.isna(shape_id)):
                return "NA"
            logging.debug(f'{shape_id}, {type(shape_id)}') # nan
            df = self.shapes
            sub_df = df[df.shape_id.astype(str).isin([self.safe_str_conversion(shape_id)])]
            if 'shape_pt_sequence' in df.columns:
                sub_df = sub_df.sort_values(by='shape_pt_sequence')
            lat_lon_list = sub_df[['shape_pt_lat', 'shape_pt_lon']].values.tolist()
            if shape_id == "436E0248":
                print(self.safe_str_conversion(shape_id))
            # Calculate min and max latitude/longitude from your dataset
            min_lat = sub_df['shape_pt_lat'].min()
            max_lat = sub_df['shape_pt_lat'].max()
            min_lon = sub_df['shape_pt_lon'].min()
            max_lon = sub_df['shape_pt_lon'].max()
            logging.debug(f"{len(sub_df['shape_pt_lat'])}")
            bounds = (min_lat-1, min_lon-1,  max_lat+1,max_lon+1)

            quad_tree = QuadTree(bounds)

            for point in lat_lon_list:
                quad_tree.insert(point)

        


            nearest_A, _ = quad_tree.execute(stops,departure_station)

            nearest_B, _ = quad_tree.execute(stops,arrival_station)

            logging.debug(f"{nearest_A} {nearest_B}")

            dist = CalculateDistance(self.shapes)
            total_distance = dist.shape_to_dist(shape_id,nearest_A,nearest_B)
            self.shape_distances[f'{departure_station}-{arrival_station}-{shape_id}'] = total_distance
            
            logging.debug(f"{total_distance} miles")
            return total_distance
    def test(self):
        return self.shape_distances
