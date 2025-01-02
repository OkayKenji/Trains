import re
import requests
import zipfile
import os
import shutil

# URL of the page where the HTML is located
url = 'https://ftis.org/Posts.aspx'

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
    with open('Posts.aspx', 'w') as file:
        file.write(html_content)
    print("index.html downloaded and saved.")


    with open('Posts.aspx', 'r') as file:
        lines = file.readlines()
        
    # Step 1: Find the first line matching 'Tri-Rail-google_transit-.*.zip'
    pattern = r'Tri-Rail-google_transit-.*\.zip'
    first_match_line = None

    # Loop through the lines and find the first match
    for line in lines:
        if re.search(pattern, line):
            first_match_line = line
            break  # Exit the loop after the first match

    if first_match_line:
        # Step 2: Extract the string between &quot; and &quot;
        quote_pattern = r'&quot;(.*?)&quot;'
        quote_match = re.search(quote_pattern, first_match_line)
        
        if quote_match:
            extracted_str = quote_match.group(1)
            
            # Step 3: Replace '#' with 'A'
            result = extracted_str.replace('#', 'A')
            
            # Print the final result
            url = "https://ftis.org/PostFileDownload.aspx?id="+result
            file_name = 'gtfstrirail.zip'

            response = requests.get(url)
            with open(file_name, 'wb') as file:
                file.write(response.content)

            zip_file_path = 'gtfstrirail.zip'
            extract_to = './trirail'

            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)

            os.system("rm gtfstrirail.zip")

                        
            # Define source and destination directories
            source_dir = './trirail/google_transit'
            destination_dir = './trirail/'

            # Check if the source directory exists
            if not os.path.exists(source_dir):
                print(f"Source directory {source_dir} does not exist.")
            else:
                # Ensure the destination directory exists, if not, create it
                if not os.path.exists(destination_dir):
                    os.makedirs(destination_dir)

                # Iterate over all files in the source directory
                for filename in os.listdir(source_dir):
                    # Full path to the source file
                    source_file = os.path.join(source_dir, filename)
                    
                    # Check if it is a file (not a directory)
                    if os.path.isfile(source_file):
                        # Full path to the destination file
                        destination_file = os.path.join(destination_dir, filename)
                        
                        # Move the file
                        shutil.move(source_file, destination_file)
                        print(f"Moved: {filename}")
            os.system("rmdir ./trirail/google_transit")
            os.system("rm *.aspx")
        else:
            print("No content found between &quot; and &quot;.")
    else:
        print("No match found for the Tri-Rail pattern.")