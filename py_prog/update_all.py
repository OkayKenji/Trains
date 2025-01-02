import threading
import subprocess
import os
import glob
def action(ele):
    subprocess.run(['python', f'./gtfs_data/{ele}/download_unzip_clean.py'])
    print(f'Done: {ele}')


def main():
    threads = []
    elements = ["ace","exo","lirr","marc","metrolink","mnrr","nicd","njt","septa","trirail","vre","mbta","sunrail","sle","amtrak","sle","hl","go","via","rtd"]

    for ele in elements:
        thread = threading.Thread(target=action, args=(ele,))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()


    # List of patterns to match the files you want to delete
    patterns = [
        # '*/shapes.txt',
        '*/agency.txt',
        '*/fare*.txt',
        '*/feed_*.txt',
        '*/facilities*.txt',
        '*/levels*.txt',
        '*/lines*.txt',
        '*/linked*.txt',
        '*/multi*.txt',
        '*/pathwa*.txt',
        '*/route_p*.txt',
        '*/stop_are*.txt',
        '*/timeframes*.txt',
        '*/areas.txt'
    ]

    # Loop through each pattern and delete matching files
    for pattern in patterns:
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

main()