import pandas as pd
import time as t
from datetime import timedelta as td
import re
from datetime import datetime
import json
import ast
import time

import warnings 
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
pd.set_option('mode.chained_assignment', None)


def getServices(calendar_dates, railroad, calendar):
    calendar_dates = calendar_dates.astype({'date': 'str'})
    listOfServices = calendar_dates[calendar_dates.date == getDate()]

    if not listOfServices.empty:
        return listOfServices
    if use_calendar:
        date_object = datetime.strptime(getDate(), "%Y%m%d").date()
        if date_object.weekday() == 0:
            listOfServices = calendar[calendar.monday == 1]
            return listOfServices
        if date_object.weekday() == 1:
            listOfServices = calendar[calendar.tuesday == 1]
            return listOfServices
        if date_object.weekday() == 2:
            listOfServices = calendar[calendar.wednesday == 1]
            return listOfServices
        if date_object.weekday() == 3:
            listOfServices = calendar[calendar.thursday == 1]
            return listOfServices
        if date_object.weekday() == 4:
            listOfServices = calendar[calendar.friday == 1]
            return listOfServices
        elif date_object.weekday() == 5:
            listOfServices = calendar[calendar.saturday == 1]
            return listOfServices
        elif date_object.weekday() == 6:
            listOfServices = calendar[calendar.sunday == 1]
            return listOfServices

def getDate():
    return "20250103"

def loadData(name_rail):
    global railroad 
    global train_classification 
    global use_calendar 
    railroad = name_rail
    use_calendar = railroad == 'septa' or railroad =='metrolink' or railroad == 'marc' or railroad == 'trirail' or railroad == 'sounder' or railroad == 'vre' or railroad == 'nicd' or railroad == "ace" or railroad == 'mbta' or railroad == 'sunrail' or railroad == 'amtrak' or "sle" or railroad == "hl"
    train_classification = ''
    if railroad == 'njt':
        train_classification = 'block_id'
    elif railroad == 'ace' or railroad == 'go':
        train_classification = 'trip_id'
    else:
        train_classification = 'trip_short_name'

    return pd.read_csv(f'./{railroad}/calendar_dates.txt'), pd.read_csv(f'./{railroad}/routes.txt'), pd.read_csv(f'./{railroad}/stop_times.txt', dtype={'track': 'str'}), pd.read_csv(f'./{railroad}/stops.txt'), pd.read_csv(f'./{railroad}/trips.txt'), pd.read_csv(f'./{railroad}/calendar_dates.txt') if (not use_calendar) else pd.read_csv(f'./{railroad}/calendar.txt'), railroad

def getTrains(listOfServices, trips): 
    listOfTrains = trips[trips.service_id.isin(listOfServices.service_id)]
    return listOfTrains

def cvtRouteStringToNumber(routes, route_id):
    route_name = routes[routes.route_id == route_id]
    if route_name.empty == True:
        return None
    else:
        return route_name.route_long_name.to_numpy()[0]

def assign_station_names(row, stops):
    stop_name = stops.loc[stops['stop_id'] == row['stop_id'], 'stop_name']
    if not stop_name.empty:
        return stop_name.iloc[0]
    
    if railroad != 'marc' and railroad != 'vre' and railroad != 'exo' and railroad != 'mbta' and railroad != 'amtrak':
        return None # give up
                              
    stop_name = stops.loc[stops['station_id_additional'].apply(lambda x: str(row['stop_id']) in ast.literal_eval(x)), 'stop_name']

    if not stop_name.empty:
        return stop_name.iloc[0]
    else:
        return None                   
    # ] if not stop_name.empty else None

def reformat(stops, routes, listOfTrains, stop_times): 
    # Filter stop_times to reduce size of what search through
    stop_times = stop_times[stop_times.trip_id.isin(listOfTrains.trip_id)]
    reformated = []

    grouped = stop_times.groupby('trip_id')

    total_trains = len(grouped)
    # print(total_trains)
    for i, (train, group) in enumerate(grouped):
        # if total_trains > 10 and i % (total_trains // 10) == 0:
        #     print(f'{(i / total_trains) * 100:.0f}%...')   
        group = group.drop(['trip_id', 'arrival_time'], axis=1)
        if group.empty:
            continue
        group['stop_name'] = group.apply(assign_station_names, axis=1, args=(stops,))
        
        reformated.append([
            group.drop(['stop_id'], axis=1),
            listOfTrains.loc[listOfTrains.trip_id == train, train_classification].iloc[0],
            listOfTrains.loc[listOfTrains.trip_id == train, 'trip_headsign'].iloc[0],
            cvtRouteStringToNumber(routes, listOfTrains.loc[listOfTrains.trip_id == train, 'route_id'].iloc[0])
        ])
    return reformated

def main():
    # elements = ["ace","exo","lirr","marc","metrolink","mnrr","nicd","njt","septa","trirail","vre","mbta","sunrail","amtrak","sle","hl"]
    elements = ["go"]
    for ele in elements: 
        print(f"Processing: {ele}")
        local_start_time = time.time()

        # prepare data
        calendar_dates, routes, stop_times, stops, trips, calendar, railroad = loadData(ele)

        # get dates from user & finds the services that run that day
        listOfServices = getServices(calendar_dates, railroad, calendar)


        # gets all of the trains that run that day
        listOfTrains = getTrains(listOfServices, trips)
        print(listOfTrains.to_csv('e1.csv'))
        listOfTrains = listOfTrains.astype({f'{train_classification}': 'str', 'trip_headsign': 'str', f'{train_classification}': 'str', 'direction_id': 'str'})
        print(listOfTrains.to_csv('e.csv'))
        print("\tWait a while as we process the data...")
        reformated = reformat(stops, routes, listOfTrains, stop_times)
        reformated = sorted(reformated, key=lambda train: (isinstance( train[1].zfill(4), str),  train[1].zfill(4)))
        all_stops = stops.loc[:, ['stop_name']]

        for row in reformated:
        
            stop_list = row[0]
            stop_list = stop_list.drop_duplicates(subset='stop_name')  # Ensure uniqueness by removing duplicates

            stop_list['eee'] = stop_list['departure_time'] + " (" + stop_list['stop_sequence'].astype(str) + ")"
            train_number = row[1]
            line = row[3]
            stop_map = stop_list.set_index("stop_name")["eee"]
            all_stops[f'{train_number} ({line})'] = all_stops['stop_name'].map(stop_map).fillna('')

        # html_table = stops.to_html()

        all_stops.columns = all_stops.columns.str.replace('Train ', '', regex=False)
        all_stops.columns = all_stops.columns.str.replace('CTrail ', '', regex=False)
        all_stops.columns = all_stops.columns.str.replace( r"^\d{8}-[A-Za-z]{2}-", '', regex=True)
        all_stops.to_csv(f'./csv/{ele}.csv')

        print("\tWait a while as we format the data...")
        arr = []

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
                new_ele = { 
                    'train_number': match.group(1),
                    'train_line': match.group(2),
                    'stops' : train_stops.to_dict(orient='index')
                }

                arr.append(new_ele)
        # Save dictionary as JSON to a file
        pretty_json = json.dumps(arr)

        with open(f'./json/data{ele}.json', 'w') as file:
            file.write(pretty_json)
        
        local_end_time = time.time()

        local_execution_time = local_end_time - local_start_time

        print(f"\tLocal Execution time: {local_execution_time:.4f} seconds")

if __name__ == "__main__":
    # Start the timer
    start_time = time.time()

    # Call the function
    main()

    # Calculate the time taken
    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Execution time: {execution_time:.4f} seconds")
    
