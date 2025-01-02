import pandas as pd
import time as t
from datetime import timedelta as td
import re
from datetime import datetime
import json
import ast
import time
from distance import MainDistanceCalculator
import logging
import os

logging.basicConfig(level=logging.WARNING,
    format='%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | \nMessage: %(message)s'
)


class GenerateTrainList:
    """
    _summary_ Loads necessary files 
    """
    def __init__(self,railroad: str,train_classification: str,date="20250103"):
        self.railroad = railroad 
        self.train_classification = train_classification 

        base_path = './gtfs_data'

        if (railroad == 'rtd'):
            return

        # may be missing
        if os.path.isfile(f'{base_path}/{railroad}/calendar_dates.txt'):
            self.calendar_dates = pd.read_csv(f'{base_path}/{railroad}/calendar_dates.txt')
        else:
            logging.debug(f'{railroad}: calendar_dates is omitted')
            self.calendar_dates = pd.DataFrame()

        # may be missing
        if os.path.isfile(f'{base_path}/{railroad}/calendar.txt'):
            logging.debug(f'{railroad}: calendar is omitted')
            self.calendar = pd.read_csv(f'{base_path}/{railroad}/calendar.txt')
        else:
            self.calendar = pd.DataFrame()

        self.routes = pd.read_csv(f'{base_path}/{railroad}/routes.txt')
        self.stop_times =pd.read_csv(f'{base_path}/{railroad}/stop_times.txt')
        self.stops = pd.read_csv(f'{base_path}/{railroad}/stops.txt')
        self.trips = pd.read_csv(f'{base_path}/{railroad}/trips.txt')
        self.shapes = pd.read_csv(f'{base_path}/{railroad}/shapes.txt')

        # Fix data types
        if ( railroad == 'rtd/RTD_Denver_Direct_Operated_Commuter_Rail_GTFS' or railroad == 'rtd/RTD_Denver_Purchased_Transportation_Commuter_Rail_GTFS'):
            self.stop_times = self.stop_times.astype( { 'trip_id': 'str'})

        self.date = date  

    def getServices(self):
        # https://gtfs.org/documentation/schedule/reference/#calendar_datestxt
        if not self.calendar.empty:
            # Convert the date strings to pandas datetime objects
            self.calendar['start_date'] = pd.to_datetime(self.calendar['start_date'], format='%Y%m%d')
            self.calendar['end_date'] = pd.to_datetime(self.calendar['end_date'], format='%Y%m%d')

            # Define the current date
            date_object = pd.to_datetime(self.date, format='%Y%m%d')

            # Filter rows where current_date is between start_date and end_date
            self.calendar = self.calendar[(self.calendar['start_date'] <= date_object) & (self.calendar['end_date'] >= date_object)]
            
            date_object = datetime.strptime(self.date, "%Y%m%d").date()
            if date_object.weekday() == 0:
                listOfServices = self.calendar[self.calendar.monday == 1]
            elif date_object.weekday() == 1:
                listOfServices = self.calendar[self.calendar.tuesday == 1]
            elif date_object.weekday() == 2:
                listOfServices = self.calendar[self.calendar.wednesday == 1]
            elif date_object.weekday() == 3:
                listOfServices = self.calendar[self.calendar.thursday == 1]
            elif date_object.weekday() == 4:
                listOfServices = self.calendar[self.calendar.friday == 1]
            elif date_object.weekday() == 5:
                listOfServices = self.calendar[self.calendar.saturday == 1]
            elif date_object.weekday() == 6:
                listOfServices = self.calendar[self.calendar.sunday == 1]

            if not self.calendar_dates.empty:
                self.calendar_dates = self.calendar_dates.astype({'date': 'str'})
                
                listOfServices = pd.concat([listOfServices, self.calendar_dates[
                    (self.calendar_dates['date'] == self.date) & 
                    (self.calendar_dates['exception_type'].astype(str) == "1")
                ]], ignore_index=True)

                servicesToRemove = self.calendar_dates[
                    (self.calendar_dates['date'] == self.date) & 
                    (self.calendar_dates['exception_type'].astype(str) == "2")
                ]

                if len(servicesToRemove) > 0:
                    listOfServices = listOfServices[~listOfServices['service_id'].isin(servicesToRemove['service_id'])]

            return listOfServices[['service_id']]
        elif not self.calendar_dates.empty:
            self.calendar_dates = self.calendar_dates.astype({'date': 'str'})
            listOfServices = self.calendar_dates[
                (self.calendar_dates['date'] == self.date) & 
                (self.calendar_dates['exception_type'].astype(str) == "1")
            ]            
            return listOfServices[['service_id']]
        print(self.calendar, self.calendar_dates)
        logging.warning(f'{self.railroad}: Both calendar_dates and calendar missing!')
        return None

    def getTrains(self, listOfServices): 
        listOfTrains = self.trips[self.trips.service_id.isin(listOfServices.service_id)]
        return listOfTrains

    def cvtRouteStringToNumber(self,route_id):
        route_name = self.routes[self.routes.route_id == route_id]
        if route_name.empty == True:
            return None
        else:
            if (self.railroad == 'rtd/RTD_Denver_Direct_Operated_Commuter_Rail_GTFS' or self.railroad == 'rtd/RTD_Denver_Purchased_Transportation_Commuter_Rail_GTFS'):
                return route_name.route_short_name.to_numpy()[0]
            else:
                return route_name.route_long_name.to_numpy()[0]

    def assign_station_names(self,row):
        stop_name = self.stops.loc[self.stops['stop_id'] == row['stop_id'], 'stop_name']
        if not stop_name.empty:
            return stop_name.iloc[0]
        if self.railroad != 'marc' and self.railroad != 'vre' and self.railroad != 'exo' and self.railroad != 'mbta' and self.railroad != 'amtrak' and  self.railroad != 'rtd/RTD_Denver_Direct_Operated_Commuter_Rail_GTFS' and self.railroad != 'rtd/RTD_Denver_Purchased_Transportation_Commuter_Rail_GTFS':
            return None # give up
        stop_name = self.stops.loc[self.stops['station_id_additional'].apply(lambda x: str(row['stop_id']) in ast.literal_eval(x)), 'stop_name']

        if not stop_name.empty:
            return stop_name.iloc[0]
        else:
            return None                   

    def reformat(self, listOfTrains): 
        # Filter stop_times to reduce size of what search through
        self.stop_times = self.stop_times[self.stop_times.trip_id.isin(listOfTrains.trip_id)]
        reformated = []

        grouped = self.stop_times.groupby('trip_id')

        for i, (train, group) in enumerate(grouped):
            group = group.drop(['trip_id', 'arrival_time'], axis=1)

            if group.empty:
                continue
            group['stop_name'] = group.apply(self.assign_station_names, axis=1, args=())

            if (self.railroad == 'metra'):
                train_id = re.sub(r"_", '', re.sub(r"_\d_$", '', re.sub(r"[A-Za-z ()\-]+", '', listOfTrains.loc[listOfTrains.trip_id == train, self.train_classification].iloc[0])))
            else:
                train_id = listOfTrains.loc[listOfTrains.trip_id == train, self.train_classification].iloc[0]
            reformated.append([
                group.drop(['stop_id'], axis=1),
                train_id,
                listOfTrains.loc[listOfTrains.trip_id == train, 'trip_headsign'].iloc[0],
                self.cvtRouteStringToNumber(listOfTrains.loc[listOfTrains.trip_id == train, 'route_id'].iloc[0]),
                listOfTrains.loc[listOfTrains.trip_id == train, 'shape_id'].iloc[0] if 'shape_id' in listOfTrains.columns else 'NA'
            ])
        return reformated

    def rtd_exempt(self):
        print("\tRTD Exception...")

        with open('./data/json/datartd/RTD_Denver_Direct_Operated_Commuter_Rail_GTFS.json', 'r') as file1:
            data1 = json.load(file1)

        with open('./data/json/datartd/RTD_Denver_Purchased_Transportation_Commuter_Rail_GTFS.json', 'r') as file2:
            data2 = json.load(file2)

        arr = data1 + data2

        pretty_json = json.dumps(arr)

        with open(f'./data/json/datartd.json', 'w') as file:
            file.write(pretty_json)
        
    def main(self):
        logging.info(f"Processing: {self.railroad}")
        local_start_time = time.time()

        # RTD is a combination of two separate GTFS 
        if self.railroad == "rtd":
            self.rtd_exempt()
            local_end_time = time.time()
            local_execution_time = local_end_time - local_start_time
            logging.info(f"\tLocal Execution time: {local_execution_time:.4f} seconds")
            return 
        
        # get dates from user & finds the services that run that day
        listOfServices = self.getServices()

        # gets all of the trains that run that day
        listOfTrains = self.getTrains(listOfServices)
        

        if ( self.railroad != 'metrolink'):
            listOfTrains = listOfTrains.astype({'shape_id': 'str'})
        listOfTrains = listOfTrains.astype({f'{self.train_classification}': 'str',
                                            'trip_headsign': 'str',
                                            'direction_id': 'str'})
        logging.info(f"\tf{self.railroad}Wait a while as we process the data...)")
        

        reformated = self.reformat(listOfTrains)

        reformated = sorted(reformated, key=lambda train: (isinstance( train[1].zfill(4), str),  train[1].zfill(4)))
        all_stops = self.stops.loc[:, ['stop_name']]

        for row in reformated:
            stop_list = row[0]
            stop_list = stop_list.drop_duplicates(subset='stop_name')  # Ensure uniqueness by removing duplicates

            stop_list['eee'] = stop_list['departure_time'] + " (" + stop_list['stop_sequence'].astype(str) + ")"
            train_number = row[1]
            line = row[3]
            stop_map = stop_list.set_index("stop_name")["eee"]
            all_stops = all_stops.assign(**{f'{train_number} ({line})': all_stops['stop_name'].map(stop_map).fillna('')})

        all_stops.columns = all_stops.columns.str.replace('Train ', '', regex=False)
        all_stops.columns = all_stops.columns.str.replace('CTrail ', '', regex=False)
        all_stops.columns = all_stops.columns.str.replace( r"^\d{8}-[A-Za-z]{2}-", '', regex=True)
       
        all_stops.to_csv(f'./data/csv/{self.railroad}.csv')
        logging.info("\tWait a while as we format the data...")
        arr = []

        for _, sublist in enumerate(reformated):
            if len(sublist) > 1 and sublist[1] == 4:  # Checking the second element
                logging.debug(sublist)
                break

        main_distance_calculator = MainDistanceCalculator(self.shapes)
        for _, k in enumerate(all_stops):
            match = re.match(r'([\w\s\.]+)\s+\(([éô0-9a-zA-Z\/\-\&\-\s]+)\)', k)
            if match:
                train_stops = all_stops[k].to_frame()               
                train_stops['station_names'] = all_stops['stop_name']
                train_stops.set_index('station_names', inplace=True)
                train_stops.rename(columns={k: 'stop_times'}, inplace=True)
                train_stops[['departure_time', 'stop_index']] = train_stops['stop_times'].str.extract(r'([0-9:]+)\s+\(([0-9]+)\)')
                train_stops[['departure_time', 'stop_index']] = train_stops[['departure_time', 'stop_index']].fillna('n/a') 
                train_stops.drop('stop_times',axis=1,inplace=True)
                if self.railroad == 'marc': 
                    result = [sublist for sublist in reformated if sublist[1] == f'Train {match.group(1)}']
                    starting_station = result[0][0].iloc[0] if len(result) > 0 else "N/A"
                    ending_station = result[0][0].iloc[len(result[0][0])-1] if len(result) > 0 else "N/A"
                    distance = result[0][4] if len(result) > 0 else "N/A"
                elif self.railroad == 'hl':
                    result = [sublist for sublist in reformated if sublist[1] == f'CTrail {match.group(1)}']
                    starting_station = result[0][0].iloc[0] if len(result) > 0 else "N/A"
                    ending_station = result[0][0].iloc[len(result[0][0])-1] if len(result) > 0 else "N/A"
                    distance = result[0][4] if len(result) > 0 else "N/A"
                elif self.railroad == 'go':  
                    result = [sublist for sublist in reformated if re.sub(r"^\d{8}-[A-Za-z]{2}-", '', sublist[1]) == f'{match.group(1)}']
                    starting_station = result[0][0].iloc[0] if len(result) > 0 else "N/A"
                    ending_station = result[0][0].iloc[len(result[0][0])-1] if len(result) > 0 else "N/A"
                    distance = result[0][4] if len(result) > 0 else "N/A"     
                else:
                    result = [sublist for sublist in reformated if sublist[1] == f'{match.group(1)}']
                    starting_station = result[0][0].iloc[0] if len(result) > 0 else "N/A"
                    ending_station = result[0][0].iloc[len(result[0][0])-1] if len(result) > 0 else "N/A"
                    distance = result[0][4] if len(result) > 0 else "N/A"
                new_ele = { 
                    'train_number': match.group(1),
                    'train_line': match.group(2),
                    'stops' : train_stops.to_dict(orient='index'),
                    'distance' : main_distance_calculator.calculate_distance(
                        starting_station['stop_name'],
                        ending_station['stop_name'],
                        self.stops,
                        distance
                    ) 
            }

                arr.append(new_ele)
        # Save dictionary as JSON to a file
        pretty_json = json.dumps(arr)

        with open(f'./data/json/data{self.railroad}.json', 'w') as file:
            file.write(pretty_json)
        local_end_time = time.time()

        local_execution_time = local_end_time - local_start_time

        print(f"\tLocal Execution time: {local_execution_time:.4f} seconds")
        # exit(0)

if __name__ == "__main__":
    # Start the timer
    start_time = time.time()

    # elements = ["exo","lirr","marc","metrolink","mnrr","nicd","septa","trirail","vre","mbta","sunrail","amtrak","sle","hl","via","rtd"]
    elements = [
        {
            "railroad" : "njt",
            "train_classification": 'block_id',
        },
        {
            "railroad" : "ace",
            "train_classification": 'trip_id',
        },
        {
            "railroad" : "go",
            "train_classification": 'trip_id',
        },
        {
            "railroad" : "rtd/RTD_Denver_Direct_Operated_Commuter_Rail_GTFS",
            "train_classification": 'trip_id',
        },
        {
            "railroad" : "rtd/RTD_Denver_Purchased_Transportation_Commuter_Rail_GTFS",
            "train_classification": 'trip_id',
        },
        {
            "railroad" : "metra",
            "train_classification": 'trip_id',
        },
        {
            "railroad" : "exo",
            "train_classification": 'trip_short_name',
        },
        {
            "railroad" : "lirr",
            "train_classification": 'trip_short_name',
        },
        {
            "railroad" : "marc",
            "train_classification": 'trip_short_name',
        },
        {
            "railroad" : "metrolink",
            "train_classification": 'trip_short_name',
        },
        {
            "railroad" : "mnrr",
            "train_classification": 'trip_short_name',
        },
        {
            "railroad" : "nicd",
            "train_classification": 'trip_short_name',
        },
        {
            "railroad" : "septa",
            "train_classification": 'trip_short_name',
        },
        # {
        #     "railroad" : "trirail",
        #     "train_classification": 'trip_short_name',
        # },
        {
            "railroad" : "vre",
            "train_classification": 'trip_short_name',
        },
        {
            "railroad" : "mbta",
            "train_classification": 'trip_short_name',
        },
        {
            "railroad" : "sunrail",
            "train_classification": 'trip_short_name',
        },
        {
            "railroad" : "amtrak",
            "train_classification": 'trip_short_name',
        },
        {
            "railroad" : "sle",
            "train_classification": 'trip_short_name',
        },
        {
            "railroad" : "hl",
            "train_classification": 'trip_short_name',
        },
        {
            "railroad" : "via",
            "train_classification": 'trip_short_name',
        },
        {
            "railroad" : "rtd",
            "train_classification": 'trip_short_name',
        }
    ]
        # elements = ["exo","lirr","marc","metrolink","mnrr","nicd","septa","trirail","vre","mbta","sunrail","amtrak","sle","hl","via","rtd"]



    for ele in elements: 
        x = GenerateTrainList(
            ele['railroad'],
            ele['train_classification'],
        )
        # Call the function
        x.main()

    # Calculate the time taken
    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Execution time: {execution_time:.4f} seconds")
    
