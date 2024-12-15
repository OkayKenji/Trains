import pandas as pd
import os
import time as t
from datetime import timedelta as td
import itables
import webbrowser
from datetime import datetime

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

def loadData():
    global railroad 
    global train_classification 

    railroad = 'septa'
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

def main():
    # prepare data
    calendar_dates, routes, stop_times, stops, trips, calendar, railroad = loadData()

    # get dates from user & finds the services that run that day
    listOfServices = getServices(calendar_dates, railroad, calendar)

    # gets all of the trains that run that day
    listOfTrains = getTrains(listOfServices, trips)
    listOfTrains = listOfTrains.astype({f'{train_classification}': 'str', 'trip_headsign': 'str', f'{train_classification}': 'str', 'direction_id': 'str', 'shape_id': 'str'})
    print("Wait a while as we process data...")
    reformated = reformat(stops, routes, listOfTrains, stop_times)
    reformated = sorted(reformated, key=lambda reformated: (isinstance( reformated[1], str),  reformated[1]))
# x: (isinstance(x, str), x)
    stops = stops.loc[:, ['stop_name']]
    for row in reformated:
        stop_list = row[0]
        train_number = row[1]
        line = row[3]
        stops[f'{train_number} ({line})'] = stops['stop_name'].map(stop_list.set_index('stop_name')['departure_time']).fillna('')
    
    # Render table using itables.show() for interactive display (this will work only in a Jupyter/IPython environment)
    itables.show(stops)

    # Alternatively, Save the HTML table and open it in the browser:
    # Render the table as HTML using pandas
    html_table = stops.to_html()

    stops.to_csv('test.csv')

    # Save the HTML table to a file
    with open('test.html', 'w') as f:
        f.write(html_table)
    
    # Automatically open the file in the browser
    webbrowser.open('test.html', new=2)

if __name__ == "__main__":
    main()
