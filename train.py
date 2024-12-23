import pandas as pd
import time as t
from datetime import timedelta as td
import re
from datetime import datetime
import json
import ast

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
    use_calendar = railroad == 'septa' or railroad =='metrolink' or railroad == 'marc' or railroad == 'trirail' or railroad == 'sounder' or railroad == 'vre' or railroad == 'nicd' or railroad == "ace"
    train_classification = ''
    if railroad == 'njt':
        train_classification = 'block_id'
    elif railroad == 'ace':
        train_classification = 'trip_id'
    else:
        train_classification = 'trip_short_name'

    return pd.read_csv(f'./{railroad}/calendar_dates.txt'), pd.read_csv(f'./{railroad}/routes.txt'), pd.read_csv(f'./{railroad}/stop_times.txt', dtype={'track': 'str'}), pd.read_csv(f'./{railroad}/stops.txt'), pd.read_csv(f'./{railroad}/trips.txt'), pd.read_csv(f'./{railroad}/calendar_dates.txt') if (not use_calendar) else pd.read_csv(f'./{railroad}/calendar.txt'), railroad

def getTrains(listOfServices, trips): 
    listOfTrains = []
    for service in listOfServices.service_id:
        listOfTrains.append(trips[trips.service_id == service])
    return pd.DataFrame(pd.concat(listOfTrains))

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
    
    if railroad != 'exo':
        return None # give up
                              
    stop_name = stops.loc[stops['station_id_additional'].apply(lambda x: row['stop_id'] in ast.literal_eval(x)), 'stop_name']

    if not stop_name.empty:
        return stop_name.iloc[0]
    else:
        return None                   
    # ] if not stop_name.empty else None

def reformat(stops, routes, listOfTrains, stop_times): 
    reformated = []
    tempPercent = 0
    print(f'{0}%...')
    for index, train in enumerate(listOfTrains.trip_id):
        if ((index / len(listOfTrains)) * 100 > tempPercent + 10):
            print(f'{tempPercent + 10}%...')
            tempPercent += 10
        filtered_df = stop_times[stop_times.trip_id == train]
        filtered_df = filtered_df.drop(['trip_id', 'arrival_time'], axis=1)
        if (filtered_df.empty):
            print("Opps! Missing train data, skipping.")
            continue
        filtered_df['stop_name'] = filtered_df.apply(assign_station_names, axis=1, args=(stops,))
        temp = [filtered_df.drop(['stop_id'], axis=1), int(listOfTrains[train_classification].iloc[index]) if listOfTrains[train_classification].iloc[index].isdigit() else str(listOfTrains[train_classification].iloc[index])  , listOfTrains.trip_headsign.iloc[index], cvtRouteStringToNumber(routes, listOfTrains.route_id.iloc[index])]
        reformated.append(temp)
    print(f'{100}%...')
    return reformated

def main():
    # elements = ["ace","exo","lirr","marc","metrolink","mnrr","nicd","njt","septa","trirail","vre"]
    elements = ['exo']
    for ele in elements: 
        print("NOW - ",ele)
        # prepare data
        calendar_dates, routes, stop_times, stops, trips, calendar, railroad = loadData(ele)

        # get dates from user & finds the services that run that day
        listOfServices = getServices(calendar_dates, railroad, calendar)

        # gets all of the trains that run that day
        listOfTrains = getTrains(listOfServices, trips)
        listOfTrains = listOfTrains.astype({f'{train_classification}': 'str', 'trip_headsign': 'str', f'{train_classification}': 'str', 'direction_id': 'str'})
        print("Wait a while as we process data...")
        reformated = reformat(stops, routes, listOfTrains, stop_times)
        reformated = sorted(reformated, key=lambda reformated: (isinstance( reformated[1], str),  reformated[1]))
        stops = stops.loc[:, ['stop_name']]

        for row in reformated:
        
            stop_list = row[0]
            stop_list = stop_list.drop_duplicates(subset='stop_name')  # Ensure uniqueness by removing duplicates

            stop_list['eee'] = stop_list['departure_time'] + " (" + stop_list['stop_sequence'].astype(str) + ")"
            train_number = row[1]
            line = row[3]
            stops[f'{train_number} ({line})'] = stops['stop_name'].map(stop_list.set_index("stop_name")["eee"]).fillna('')

        # html_table = stops.to_html()

        stops.to_csv(f'./csv/{ele}.csv')

        # print(stops.to_dict())




        arr = []
        for i, k in enumerate(stops):
            match = re.match(r'([\w\s\.]+)\s+\(([éô0-9a-zA-Z\/\-\&\-\s]+)\)', k)
            if match:
                eggs = pd.DataFrame(stops[k].to_list())
                eggs['station_names'] = pd.DataFrame(stops['stop_name'].to_list())[0]  # Accessing the Series by index
                eggs.set_index('station_names', inplace=True)
                eggs.rename(columns={0: 'stopping'}, inplace=True)
                eggs[['departure_time', 'stop_index']] = eggs['stopping'].str.extract(r'([0-9:]+)\s+\(([0-9]+)\)')
                eggs[['departure_time', 'stop_index']] = eggs[['departure_time', 'stop_index']].fillna('n/a') 
                eggs.drop('stopping',axis=1,inplace=True)
                
                new_ele = { 
                    'train_number': match.group(1),
                    'train_line': match.group(2),
                    'stops' : eggs.to_dict(orient='index')
                }

                arr.append(new_ele)
                
            else:
                print("No match found.",k )
        #  = json.dumps(arr)
        # print(json_data)
        # Save dictionary as JSON to a file
        pretty_json = json.dumps(arr, indent=4)

        with open(f'./json/data{ele}.json', 'w') as file:
            file.write(pretty_json)

if __name__ == "__main__":
    main()
