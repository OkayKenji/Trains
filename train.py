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
            return pd.read_csv(f'./calendar_dates.txt'), pd.read_csv(f'./routes.txt'), pd.read_csv(f'./stop_times.txt',dtype={'track' : 'str'}), pd.read_csv(f'./stops.txt'),  pd.read_csv(f'./trips.txt'), pd.read_csv(f'./calendar_dates.txt'), pd.read_csv(f'./transfers.txt'), railroad
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

def reformat(routes,listOfTrains,stop_times): 
    reformated = []
    tempPercent = 0
    print(f'{0}%...')
    for index,train in enumerate(listOfTrains.trip_id):
        if ((index/len(listOfTrains))*100 > tempPercent+10 ):
            print(f'{tempPercent+10}%...')
            tempPercent += 10
        filtered_df = stop_times[stop_times.trip_id == train]
        filtered_df = filtered_df.drop(['trip_id', 'arrival_time', 'pickup_type', 'drop_off_type', 'track', 'note_id'],axis=1)

        temp = [filtered_df,listOfTrains.trip_short_name.iloc[index],listOfTrains.trip_headsign.iloc[index],cvtRouteStringToNumber(routes,listOfTrains.route_id.iloc[index])]
        reformated.append(temp)
    print(f'{100}%...')
    return reformated


def main():

    # prepare data
    calendar_dates, routes, stop_times, stops, trips, calendar, transfers, railroad = loadData()

    # get dates from user & finds the services that run that day
    listOfServices = getServices(calendar_dates,railroad)

    # gets all of the trains that run that day
    listOfTrains = getTrains(listOfServices,trips)
    listOfTrains = listOfTrains.astype({'trip_short_name':'str','trip_headsign':'str','trip_short_name':'str','direction_id':'str','shape_id':'str'})
    print("Wait a while as we process data...")
    reformated = reformat(routes,listOfTrains,stop_times)
    reformated = sorted(reformated, key=lambda reformated: reformated[1])
    print(reformated)
    
if __name__ == "__main__":
    main()