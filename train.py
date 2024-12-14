import pandas as pd
import os
import time as t
from datetime import timedelta as td


def getServices(calendar_dates,railroad):
    calendar_dates = calendar_dates.astype({'date':'str'})
    while True:
        listOfServices = calendar_dates[calendar_dates.date == getDate()]
        if not listOfServices.empty:
            break
        else:
            if railroad == 'mnrr':
                print("Opps! That was not a valid date. 07/14/2022 to 11/20/2022 only.")
            else:
                print("Opps! That was not a valid date. 07/13/2022 to 09/05/2022 only.")
    return listOfServices

def getDate():
    return "20241213"

def loadData():
    while True:
        railroad = 'mnrr'
        
        if railroad == 'mnrr':
            print("Wait a moment as we read in data...")
            return pd.read_csv(f'./calendar_dates.txt'), pd.read_csv(f'./routes.txt'), pd.read_csv(f'./stop_times.txt',dtype={'track' : 'str'}), pd.read_csv(f'./stops.txt'),  pd.read_csv(f'./trips.txt'), pd.read_csv(f'./calendar_dates.txt'), railroad
        elif railroad == 'lirr':
            print("Wait a moment as we read in data...")
            return pd.read_csv(f'data/LIRR/calendar_dates.txt'), pd.read_csv(f'data/LIRR/routes.txt'), pd.read_csv(f'data/LIRR/stop_times.txt'), pd.read_csv(f'data/LIRR/stops.txt'),  pd.read_csv(f'data/LIRR/trips.txt'), None, None, railroad
        else:
            print("Error, invalid name, try again.")

def getTrains(listOfServices,trips): 
    print(len(listOfServices))
    listOfTrains = []
    for service in listOfServices.service_id:
        listOfTrains.append(trips[trips.service_id == service])
    return pd.DataFrame(pd.concat(listOfTrains))

def cvtStringToNumber(stop_name,stops):
    trainName = stops[stops.stop_name == stop_name]
    if trainName.empty == True:
        return None
    else:
        return trainName.stop_id.to_numpy()[0]

def cvtNumberToString(stop_num,stops):
    stopName = stops[stops.stop_id == stop_num]
    if stopName.empty == True:
        return None
    else:
        return stopName.stop_name.to_numpy()[0]

def cvtRouteStringToNumber(routes,route_id):
    route_name = routes[routes.route_id == route_id]
    if route_name.empty == True:
        return None
    else:
        return route_name.route_long_name.to_numpy()[0]

def add_values(row, stops):
    # Use `.loc` instead of `.query` for better clarity with Series data
    stop_name = stops.loc[stops['stop_id'] == row['stop_id'], 'stop_name']
    # Return the first match, or a default value if no match is found
    return stop_name.iloc[0] if not stop_name.empty else None


def reformat(stops,routes,listOfTrains,stop_times): 
    reformated = []
    tempPercent = 0
    print(f'{0}%...')
    for index,train in enumerate(listOfTrains.trip_id):
        if ((index/len(listOfTrains))*100 > tempPercent+10 ):
            print(f'{tempPercent+10}%...')
            tempPercent += 10
        filtered_df = stop_times[stop_times.trip_id == train]
        filtered_df = filtered_df.drop(['trip_id', 'arrival_time', 'pickup_type', 'drop_off_type',],axis=1)
        
        filtered_df['stop_name'] = filtered_df.apply(add_values, axis=1, args=(stops,))

        # print()
        
        temp = [filtered_df.drop(['stop_id'],axis=1), listOfTrains.block_id.iloc[index],listOfTrains.trip_headsign.iloc[index],cvtRouteStringToNumber(routes,listOfTrains.route_id.iloc[index])]
        reformated.append(temp)
    print(f'{100}%...')
    return reformated


def main():

    # prepare data
    calendar_dates, routes, stop_times, stops, trips, calendar, railroad = loadData()

    # get dates from user & finds the services that run that day
    listOfServices = getServices(calendar_dates,railroad)

    # gets all of the trains that run that day
    listOfTrains = getTrains(listOfServices,trips)
    listOfTrains = listOfTrains.astype({'block_id':'str','trip_headsign':'str','block_id':'str','direction_id':'str','shape_id':'str'})
    print("Wait a while as we process data...")
    reformated = reformat(stops, routes,listOfTrains,stop_times)
    reformated = sorted(reformated, key=lambda reformated: reformated[1])
    # reformated
    # print(reformated)

    stops = stops.loc[:, ['stop_name']]
    for row in reformated:
        stop_list = row[0]
        train_number = row[1]
        # term = row[2]
        line = row[3]
        # stations_df['match'] = stations_df['stop_name'].isin(sub_df['stop_name']).map({True: '✔', False: ''})
        print(row)
        stops[f'{train_number} ({line})'] = stops['stop_name'].map(
    stop_list.set_index('stop_name')['departure_time']
).fillna('')
    stops.to_csv('test.csv')    
if __name__ == "__main__":
    main()