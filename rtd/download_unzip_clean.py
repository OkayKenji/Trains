import requests
import zipfile
import os
import subprocess

url = 'https://www.rtd-denver.com/files/gtfs/RTD_Denver_Direct_Operated_Commuter_Rail_GTFS.zip'
file_name = 'gtfsRTDDirect.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfsRTDDirect.zip'
extract_to = './rtd/RTD_Denver_Direct_Operated_Commuter_Rail_GTFS'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("rm gtfsRTDDirect.zip")

subprocess.run(['python', f'./rtd/RTD_Denver_Direct_Operated_Commuter_Rail_GTFS/clean.py'])
print(f'Done: RTD_Denver_Direct_Operated_Commuter_Rail_GTFS')

url = 'https://www.rtd-denver.com/files/gtfs/RTD_Denver_Purchased_Transportation_Commuter_Rail_GTFS.zip'
file_name = 'gtfsRTDPurchased.zip'

response = requests.get(url)
with open(file_name, 'wb') as file:
    file.write(response.content)

zip_file_path = 'gtfsRTDPurchased.zip'
extract_to = './rtd/RTD_Denver_Purchased_Transportation_Commuter_Rail_GTFS'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

os.system("rm gtfsRTDPurchased.zip")

subprocess.run(['python', f'./rtd/RTD_Denver_Purchased_Transportation_Commuter_Rail_GTFS/clean.py'])
print(f'Done: RTD_Denver_Purchased_Transportation_Commuter_Rail_GTFS')
