import pandas as pd
import time as t
from datetime import timedelta as td
import re
from datetime import datetime
import json

import warnings 
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)
# warnings.simplefilter(action='ignore', category=pd.errors.UserWarning)

def getServices(calendar_dates, railroad, calendar):
    calendar_dates = calendar_dates.astype({'date': 'str'})
    listOfServices = calendar_dates[calendar_dates.date == getDate()]
    
    if not listOfServices.empty:
        return listOfServices
    if railroad == 'septa':
        date_object = datetime.strptime(getDate(), "%Y%m%d").date()
        print(calendar)
        if date_object.weekday() < 5:
            listOfServices = calendar[calendar.monday == 1]
            return listOfServices
        elif date_object.weekday() == 5:
            listOfServices = calendar[calendar.saturday == 1]
            return listOfServices
        elif date_object.weekday() == 6:
            listOfServices = calendar[calendar.sunday == 1]
            return listOfServices



def getDate():
    return "20241213"

def loadData(name_rail):
    global railroad 
    global train_classification 
    railroad = name_rail

    train_classification = 'block_id' if railroad == 'njt' else 'trip_short_name'
    return pd.read_csv(f'./{railroad}/calendar_dates.txt'), pd.read_csv(f'./{railroad}/routes.txt'), pd.read_csv(f'./{railroad}/stop_times.txt', dtype={'track': 'str'}), pd.read_csv(f'./{railroad}/stops.txt'), pd.read_csv(f'./{railroad}/trips.txt'), pd.read_csv(f'./{railroad}/calendar_dates.txt') if railroad != 'septa' else pd.read_csv(f'./{railroad}/calendar.txt'), railroad

def getTrains(listOfServices, trips): 
    print(len(listOfServices))
    listOfTrains = []
    for service in listOfServices.service_id:
        listOfTrains.append(trips[trips.service_id == service])
    return pd.DataFrame(pd.concat(listOfTrains))

def cvtStringToNumber(stop_name, stops):
    trainName = stops[stops.stop_name == stop_name]
    if trainName.empty == True:
        return None
    else:
        return trainName.stop_id.to_numpy()[0]

def cvtNumberToString(stop_num, stops):
    stopName = stops[stops.stop_id == stop_num]
    if stopName.empty == True:
        return None
    else:
        return stopName.stop_name.to_numpy()[0]

def cvtRouteStringToNumber(routes, route_id):
    route_name = routes[routes.route_id == route_id]
    if route_name.empty == True:
        return None
    else:
        return route_name.route_long_name.to_numpy()[0]

def add_values(row, stops):
    stop_name = stops.loc[stops['stop_id'] == row['stop_id'], 'stop_name']
    return stop_name.iloc[0] if not stop_name.empty else None

def reformat(stops, routes, listOfTrains, stop_times): 
    reformated = []
    tempPercent = 0
    print(f'{0}%...')
    for index, train in enumerate(listOfTrains.trip_id):
        if ((index / len(listOfTrains)) * 100 > tempPercent + 10):
            print(f'{tempPercent + 10}%...')
            tempPercent += 10
        filtered_df = stop_times[stop_times.trip_id == train]
        filtered_df = filtered_df.drop(['trip_id', 'arrival_time', 'pickup_type', 'drop_off_type'], axis=1)
        filtered_df['stop_name'] = filtered_df.apply(add_values, axis=1, args=(stops,))
        temp = [filtered_df.drop(['stop_id'], axis=1), int(listOfTrains[train_classification].iloc[index]) if listOfTrains[train_classification].iloc[index].isdigit() else str(listOfTrains[train_classification].iloc[index])  , listOfTrains.trip_headsign.iloc[index], cvtRouteStringToNumber(routes, listOfTrains.route_id.iloc[index])]
        reformated.append(temp)
    print(f'{100}%...')
    return reformated

import pandas as pd

def fix_time_format(time_str):
    if '24:' in time_str or '25:' in time_str:
        # Split the string into hours, minutes, and seconds
        hours, minutes, seconds = time_str.split(':')
        
        # Replace '24' with '00' for the hours part
        if int(hours) == 24:
            time_str = f"00:{minutes}:{seconds}"
        if int(hours) == 25:
            time_str = f"01:{minutes}:{seconds}"

        # Convert to datetime and add one day
        time_obj = pd.to_datetime(time_str, format='%H:%M:%S', errors='coerce')
        if time_obj is not pd.NaT:
            time_obj += pd.Timedelta(days=1)
    else:
        try:
            # Attempt to parse the time normally
            time_obj = pd.to_datetime(time_str, format='%H:%M:%S', errors='coerce')
        except ValueError:
            return None  # Return None for invalid times

    return time_obj


# Function to fix times like 24:xx:xx and make them the next day
def fix_24_hour_time(time_obj):
    # Check if the hour is 24, which is invalid, and needs to be corrected
    if time_obj.hour == 24:
        time_obj += pd.Timedelta(days=-1)
        time_obj = time_obj.replace(hour=0)
    return time_obj

def find_first_last_valid_index(series):
    # Treat both NaN and empty strings as missing values
    valid_indices = series[~series.isna() & (series != '')].index
    first_valid_index = valid_indices[0] if len(valid_indices) > 0 else None
    last_valid_index = valid_indices[-1] if len(valid_indices) > 0 else None
    return first_valid_index, last_valid_index

def main():
    elements = ['mnrr','lirr','septa','njt','exo']
    # elements = ['lirr']
    for ele in elements: 
        # prepare data
        calendar_dates, routes, stop_times, stops, trips, calendar, railroad = loadData(ele)

        # get dates from user & finds the services that run that day
        listOfServices = getServices(calendar_dates, railroad, calendar)

        # gets all of the trains that run that day
        listOfTrains = getTrains(listOfServices, trips)
        listOfTrains = listOfTrains.astype({f'{train_classification}': 'str', 'trip_headsign': 'str', f'{train_classification}': 'str', 'direction_id': 'str', 'shape_id': 'str'})
        print("Wait a while as we process data...")
        reformated = reformat(stops, routes, listOfTrains, stop_times)
        reformated = sorted(reformated, key=lambda reformated: (isinstance( reformated[1], str),  reformated[1]))
        stops = stops.loc[:, ['stop_name','stopping_routes']]

        for row in reformated:
            stop_list = row[0]
            stop_list = stop_list.drop_duplicates(subset='stop_name')  # Ensure uniqueness

            stop_list['eee'] = stop_list['departure_time'] + " (" + stop_list['stop_sequence'].astype(str) + ")"      
            train_number = row[1]
            line = row[3]

            line_only_stops = stops[stops.stopping_routes.str.contains(line)]
            line_only_stops[f'{train_number} ({line})'] = (
                line_only_stops['stop_name']
                .map(stop_list.set_index("stop_name")["departure_time"])
                .fillna('')
            )

            # Fix invalid times like '24:xx:xx'
            line_only_stops[f'{train_number} ({line})'] = (
                line_only_stops[f'{train_number} ({line})']
                .apply(fix_time_format)
            )

            # Handle NaT or missing values before interpolation
            line_only_stops[f'{train_number} ({line})'] = line_only_stops[f'{train_number} ({line})'].fillna(pd.NaT)

            first_valid_index, last_valid_index = find_first_last_valid_index(
                line_only_stops[f'{train_number} ({line})']
            )

            if first_valid_index is not None and last_valid_index is not None:
                line_only_stops.loc[first_valid_index:last_valid_index, f'{train_number} ({line})'] = (
                    line_only_stops.loc[first_valid_index:last_valid_index, f'{train_number} ({line})']
                    .interpolate()
                )

            stops[f'{train_number} ({line})'] = (
                stops['stop_name']
                .map(line_only_stops.set_index("stop_name")[f'{train_number} ({line})'])
                .fillna('')
            )

            # # Fix any remaining invalid times
            stops[f'{train_number} ({line})'] = stops[f'{train_number} ({line})'].apply(fix_24_hour_time)

            # # Remove the date part and keep only the time (HH:MM:SS)
            stops[f'{train_number} ({line})'] = stops[f'{train_number} ({line})'].dt.strftime('%H:%M:%S (0)')


        # html_table = stops.to_html()

        stops.drop(['stopping_routes'],axis=1).to_csv(f'./csv/{ele}.csv')

        # print(stops.to_dict())

       




        arr = []
        for i, k in enumerate(stops):
            match = re.match(r'(\w+)\s+\(([éô0-9a-zA-Z\/\-\&\s]+)\)', k)
            if match:
                eggs = pd.DataFrame(stops[k].to_list())
                eggs['station_names'] = pd.DataFrame(stops['stop_name'].to_list())[0]  # Accessing the Series by index
                eggs.set_index('station_names', inplace=True)
                eggs.rename(columns={0: 'stopping'}, inplace=True)
                eggs['stopping'] = eggs['stopping'].astype(str)
                eggs[['departure_time', 'stop_index']] = eggs['stopping'].str.extract(r'([0-9:]+)\s+\(([0-9]+)\)')
                eggs[['departure_time', 'stop_index']] = eggs[['departure_time', 'stop_index']].fillna('n/a') 
                eggs.drop('stopping',axis=1,inplace=True)
                
                # print(pd.DataFrame(stops['stop_name'].to_list())  )
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

        exit(0)


if __name__ == "__main__":
    main()
