import requests
import re
import zipfile
import os

# URL of the page where the HTML is located
url = 'https://acerail.com/developer-resources/'

# Custom headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive'
}

# Step 1: Send the GET request with custom headers
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    html_content = response.text  # Get the HTML content of the page
    
    # Save the HTML content to a file (optional)
    with open('indexACE.html', 'w') as file:
        file.write(html_content)

    # Step 2: Use a regular expression to find all .zip links
    pattern = r'https://cdn[^"]*\.zip'
    matches = re.findall(pattern, html_content)

    
    url = matches[0]
    file_name = 'gtfsace.zip'

    response = requests.get(url)
    with open(file_name, 'wb') as file:
        file.write(response.content)

    zip_file_path = 'gtfsace.zip'
    extract_to = './ace'

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    os.system("cp ./ace/stopsSorted.txt ./ace/stops.txt")
    os.system("rm gtfsace.zip")
    os.system("rm indexACE.html")

else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
