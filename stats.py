import datetime
import json
import time
    
def main():
    elements = ["ace","exo","lirr","marc","metrolink","mnrr","nicd","njt","septa","trirail","vre","mbta","sunrail","amtrak","sle","hl","go","via", "rtd"]
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

