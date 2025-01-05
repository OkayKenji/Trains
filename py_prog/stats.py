import datetime
import json
import time
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

def graphs(trip_durations):
    mean = np.mean(trip_durations)
    std_dev = np.std(trip_durations)
    med = np.median(trip_durations)
    # plt.hist(trip_durations, bins=len(trip_durations), alpha=0.6, color='b')
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = stats.norm.pdf(x, mean, std_dev)
    plt.plot(x, p, 'k', linewidth=2)
    plt.title(f'Normal Distribution (mean={mean:.2f}, med={med:.2f} std_dev={std_dev:.2f})')
    plt.xlabel('Trip (stops)')
    plt.ylabel('Density')

    # Show the plot
    plt.show()



def main():
    elements = ["ace","exo","lirr","marc","metrolink","mnrr","nicd","njt","septa","trirail","vre","mbta","sunrail","amtrak","sle","hl","go","via", "rtd","metra"]
    # elements = ["go"]
    for ele in elements: 
        print(f"Processing: {ele}")

        with open(f'./data/json/data{ele}.json', 'r') as file:
            train_list = json.load(file)
            if (len(train_list) <= 0):
                print(f"\tWarning! Empty List.")
                print(f"\tNumber of trains: 0")
            train_lines = sorted(list({train["train_line"] for train in train_list}))
            longest_length = int(max(len(train_line) for train_line in train_lines)) + 2
            longest_length = longest_length if (longest_length > len("Total number of trains:")) else len("Total number of trains:")
            for train_line in train_lines:
                total_train_in_route = sum(1 for train in train_list if train["train_line"] == train_line)
                print(f'\t{f"{train_line}:":<{longest_length}} {total_train_in_route} ({total_train_in_route/len(train_list)*100:.1f}%)')
            print(f'\t{"Total number of trains:":<{longest_length}} {len(train_list)}')
            num_stops = []
            for train in train_list:
                df = pd.DataFrame(train['stops']).transpose()
                df_cleaned = df[df['departure_time'] != 'n/a']
                df_cleaned.loc[:, 'stop_index'] = df_cleaned['stop_index'].astype(int)
                df_cleaned = df_cleaned.sort_values(by='stop_index')

                timeA = df_cleaned.iloc[0].departure_time
                timeB = df_cleaned.iloc[len(df_cleaned)-1].departure_time
                timeA = f'1900-01-{1+(int(timeA[:timeA.find(":")])//24)} {int(timeA[:timeA.find(":")])%24}:{timeA[timeA.find(":")+1:]}' if re.match(r"^([2-9][4-9]|[3-9]\d|\d{3,}):.*",timeA) else f'1900-01-01 {timeA}'
                timeB = f'1900-01-{1+(int(timeB[:timeB.find(":")])//24)} {int(timeB[:timeB.find(":")])%24}:{timeB[timeB.find(":")+1:]}' if re.match(r"^([2-9][4-9]|[3-9]\d|\d{3,}):.*",timeB) else f'1900-01-01 {timeB}'
                timeA = datetime.datetime.strptime(timeA, '%Y-%m-%d %H:%M:%S')
                timeB = datetime.datetime.strptime(timeB, '%Y-%m-%d %H:%M:%S')
                num_stops.append({
                    'train_id' : train['train_number'],
                    'number_of_stops': len(df_cleaned),
                    'first_stop_time' : df_cleaned.iloc[0].departure_time,
                    'last_stop_time' : df_cleaned.iloc[len(df_cleaned)-1].departure_time,
                    'travel_time': int((timeB-timeA).total_seconds()),
                    'distance' : train['distance']
                })

            min_by_stops = min(num_stops, key=lambda x: x["number_of_stops"])
            max_by_stops = max(num_stops, key=lambda x: x["number_of_stops"])
            trip_durations = [trip['number_of_stops'] for trip in num_stops]
            avg_stops = np.mean(trip_durations)
            median_stops = np.median(trip_durations)
            print(f'\tShortest Trip (stop # wise): {min_by_stops["number_of_stops"]} stops on {min_by_stops["train_id"]}')
            print(f'\tLongest Trip (stop # wise): {max_by_stops["number_of_stops"]} stops on {max_by_stops["train_id"]}')
            print(f'\tOn average trains make: {avg_stops:.0f} stops')
            print(f'\tMedian # of train: {median_stops:.0f} stops')

            if (ele != "metrolink" and ele != "sle"):
                cleaned_data = [item for item in num_stops if item["distance"] != "NA"]
                min_by_distance = min(cleaned_data, key=lambda x: x["distance"])
                max_by_distance = max(cleaned_data, key=lambda x: x["distance"])
                trip_durations = [trip['distance'] for trip in cleaned_data]
                # graphs(trip_durations)
                avg_distance = np.mean(trip_durations)
                median_distance = np.median(trip_durations)
                print(f'\tShortest Trip (distance wise): {min_by_distance["distance"]:.1f} miles on {min_by_distance["train_id"]}')
                print(f'\tLongest Trip (distance wise): {max_by_distance["distance"]:.1f} miles on {max_by_distance["train_id"]}')
                print(f'\tOn average trains travels: {avg_distance:.1f} miles')
                print(f'\tMedian travel distance: {median_distance:.1f} miles')

            min_by_time = min(num_stops, key=lambda x: x["travel_time"])
            max_by_time = max(num_stops, key=lambda x: x["travel_time"])
            trip_durations = [trip['travel_time'] for trip in num_stops]
            avg_time = np.mean(trip_durations)
            median_time = np.median(trip_durations)
            print(f'\tShortest Trip (time wise): {min_by_time["travel_time"]/60:.1f} minutes on {min_by_time["train_id"]}')
            print(f'\tLongest Trip (time wise): {max_by_time["travel_time"]/60:.1f} minutes on {max_by_time["train_id"]}')
            print(f'\tOn average trains take: {avg_time/60:.1f} minutes')
            print(f'\tMedian time of trips: {median_time/60:.1f} minutes')
            
            if (ele != "rtd"):

                # Get stops and their info
                df = pd.read_csv(f'./data/csv/{ele}.csv') # assuming running form root
                df_ref = pd.read_csv(f'./gtfs_data/{ele}/stops.txt')
                # df_ace = pd.read_csv(f'./gtfs_data/{ele}/shapes.txt')

                # Clean and calculate max trains per stop
                df.drop('Unnamed: 0', axis=1, inplace=True)
                row_stop_counts = df.drop(columns=["stop_name"]).notna().sum(axis=1)
                df_ref['counts'] = row_stop_counts
                df_ref = df_ref[['stop_name','counts']]
                df_ref = df_ref.sort_values(by='counts',ascending=False).iloc[0:3].reset_index(drop=True)
                print("\tTop three stations: ")
                for index,row in df_ref.iterrows():
                    print(f'\t\t{index+1}. {row["stop_name"]} ({row["counts"]} trains)')
 

if __name__ == "__main__":
    # Start the timer
    start_time = time.time()

    # Call the function
    main()

    # Calculate the time taken
    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Execution time: {execution_time:.4f} seconds")
    print(f'Data last updated: {str( datetime.datetime.now())}')
