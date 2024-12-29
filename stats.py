import datetime
import json
import time
import pandas as pd
import re
def main():
    elements = ["ace","exo","lirr","marc","metrolink","mnrr","nicd","njt","septa","trirail","vre","mbta","sunrail","amtrak","sle","hl","go","via", "rtd"]
    # elements = ["via"]
    for ele in elements: 
        print(f"Processing: {ele}")

        with open(f'./json/data{ele}.json', 'r') as file:
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
                    'travel_time': int((timeB-timeA).total_seconds())
                })

            min_by_stops = min(num_stops, key=lambda x: x["number_of_stops"])
            max_by_stops = max(num_stops, key=lambda x: x["number_of_stops"])
            print(f'\tShortest Trip (stop # wise): {min_by_stops["number_of_stops"]} stops on {min_by_stops["train_id"]}')
            print(f'\tLongest Trip (stop # wise): {max_by_stops["number_of_stops"]} stops on {max_by_stops["train_id"]}')
            min_by_time = min(num_stops, key=lambda x: x["travel_time"])
            max_by_time = max(num_stops, key=lambda x: x["travel_time"])
            print(f'\tShortest Trip (time wise): {min_by_time["travel_time"]/60:.1f} minutes on {min_by_time["train_id"]}')
            print(f'\tLongest Trip (time wise): {max_by_time["travel_time"]/60:.1f} minutes on {max_by_time["train_id"]}')
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

