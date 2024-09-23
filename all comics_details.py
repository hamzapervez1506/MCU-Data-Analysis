import time
import csv
from key import PUBLIC_KEY, PRIVATE_KEY  # Import public and private keys from a separate file
from hashlib import md5
import pandas as pd
import requests  # Import the requests library for making HTTP requests

COMIC_URL = 'http://gateway.marvel.com/v1/public/comics'  # Marvel Comics API endpoint

# Function to generate timestamp and hash parameters required for API authentication
def get_hash_and_ts_params():
    ts = str(time.time())  # Get the current timestamp
    combined = ''.join([ts, PRIVATE_KEY, PUBLIC_KEY])  # Concatenate timestamp, private key, and public key
    hash_value = md5(combined.encode('ascii')).hexdigest()  # Calculate the MD5 hash of the combined string
    return {'ts': ts, 'hash': hash_value}  # Return a dictionary with timestamp and hash values

# Function to make paged requests to the Marvel Comics API and save results to a CSV file
def paged_requests(page_size=100):
    params = {'apikey': PUBLIC_KEY, 'limit': page_size}  # Set initial parameters for API request
    csv_file_name = "marvel_all_comics_details.csv"  # Specify the CSV file name

    # Open the CSV file in write mode
    with open(csv_file_name, mode="w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter="%")  # Create a CSV writer object

        # Write header row to the CSV file
        csv_writer.writerow(["Comic ID", "Title", "Format", "Variant Description", "Description", "Thumbnail URL", "Price 1", "Price Type 1"])

        for i in range(584):  # Iterate over a specified number of pages (584 in this case)
            hash_params = get_hash_and_ts_params()  # Get timestamp and hash parameters
            params.update(hash_params)  # Update the API request parameters with timestamp and hash
            params.update({'offset': page_size * i})  # Update the offset parameter for pagination
            resp_comics = requests.get(COMIC_URL, params)  # Make a GET request to the Marvel Comics API
            resp_comics.raise_for_status()  # Raise an exception if the response status code is an error
            j_comics = resp_comics.json()  # Parse the JSON response

            for comic in j_comics['data']['results'][:100]:  # Iterate over the comics in the current page (up to 100)
                # Extract relevant information about each comic
                comic_id = comic["id"]
                comic_name = comic["title"]
                comic_format = comic["format"]
                variant_description = comic["variantDescription"]
                description = comic['description']
                thumbnail_path = comic["thumbnail"]["path"]
                thumbnail_extension = comic["thumbnail"]["extension"]
                thumbnail_url = f"{thumbnail_path}.{thumbnail_extension}"
                price_1 = comic["prices"][0]["price"]
                price_type_1 = comic["prices"][0]["type"]

                # Write a row to the CSV file for each comic
                csv_writer.writerow([comic_id, comic_name, comic_format, variant_description, description, thumbnail_url, price_1, price_type_1])

if __name__ == '__main__':
    paged_requests()  # Call the paged_requests function
    print('Done')  # Print 'Done' when the process is completed
