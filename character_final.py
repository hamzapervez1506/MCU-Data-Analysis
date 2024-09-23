import time
import csv
from key import PUBLIC_KEY, PRIVATE_KEY  # Import public and private keys from a separate file
from hashlib import md5
import requests
import pandas as pd

CHARACTER_URL = 'http://gateway.marvel.com/v1/public/characters'  # Marvel Characters API endpoint
characters_list = []  # Initialize an empty list to store characters' information

# Function to generate timestamp and hash parameters required for API authentication
def get_hash_and_ts_params():
    ts = str(time.time())  # Get the current timestamp
    combined = ''.join([ts, PRIVATE_KEY, PUBLIC_KEY])  # Concatenate timestamp, private key, and public key
    hash_value = md5(combined.encode('ascii')).hexdigest()  # Calculate the MD5 hash of the combined string
    return {'ts': ts, 'hash': hash_value}  # Return a dictionary with timestamp and hash values

# Function to make paged requests to the Marvel Characters API and save results to a CSV file
def paged_requests(page_size=100):
    params = {'apikey': PUBLIC_KEY, 'limit': page_size}  # Set initial parameters for API request
    csv_file_name = "marvel_characters.csv"  # Specify the CSV file name

    with open(csv_file_name, mode="w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter="%")  # Create a CSV writer object
        csv_writer.writerow(["ID", "Name", "Description", "Thumbnail URL"])  # Write header row to the CSV file

        for i in range(16):  # Iterate over a specified number of pages (16 in this case)
            hash_params = get_hash_and_ts_params()  # Get timestamp and hash parameters
            params.update(hash_params)  # Update the API request parameters with timestamp and hash
            params.update({'offset': page_size * i})  # Update the offset parameter for pagination

            while True:
                try:
                    resp = requests.get(CHARACTER_URL, params)  # Make a GET request to the Marvel Characters API
                    resp.raise_for_status()  # Raise an exception if the response status code is an error
                    j = resp.json()  # Parse the JSON response

                    for char in j['data']['results'][:100]:  # Iterate over the characters in the current page (up to 100)
                        # Extract relevant information about each character
                        char_id = char["id"]
                        char_name = char["name"]
                        char_description = char["description"]
                        thumbnail_path = char["thumbnail"]["path"]
                        thumbnail_extension = char["thumbnail"]["extension"]
                        thumbnail_url = f"{thumbnail_path}.{thumbnail_extension}"

                        # Write a row to the CSV file for each character
                        csv_writer.writerow([char_id, char_name, char_description, thumbnail_url])

                    break  # Break the while loop if the request is successful
                except requests.exceptions.RequestException as e:
                    print(f"Request failed: {e}. Retrying...")
                    time.sleep(10)  # Wait for 10 seconds before retrying

if __name__ == '__main__':
    paged_requests()  # Call the paged_requests function
    print('Done')  # Print 'Done' when the process is completed
