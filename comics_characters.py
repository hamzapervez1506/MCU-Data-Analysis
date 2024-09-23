import time
import csv
from key import PUBLIC_KEY, PRIVATE_KEY  # Import public and private keys from a separate file
from hashlib import md5
import requests

CHARACTER_URL = 'http://gateway.marvel.com/v1/public/characters'  # Marvel Characters API endpoint
COMIC_LIMIT = 100  # Maximum number of comics to retrieve per request

# Function to generate timestamp and hash parameters required for API authentication
def get_hash_and_ts_params():
    ts = str(time.time())  # Get the current timestamp
    combined = ''.join([ts, PRIVATE_KEY, PUBLIC_KEY])  # Concatenate timestamp, private key, and public key
    hash_value = md5(combined.encode('ascii')).hexdigest()  # Calculate the MD5 hash of the combined string
    return {'ts': ts, 'hash': hash_value}  # Return a dictionary with timestamp and hash values

# Function to retrieve comic IDs for a specific character
def get_comic_ids(character_id, offset=0):
    COMIC_URL = f'http://gateway.marvel.com/v1/public/characters/{character_id}/comics'
    hash_params = get_hash_and_ts_params()
    params = {'apikey': PUBLIC_KEY, 'offset': offset, 'limit': COMIC_LIMIT, **hash_params}

    retries = 3  # Number of retries for API requests
    for attempt in range(retries):
        try:
            resp_comics = requests.get(COMIC_URL, params=params)
            resp_comics.raise_for_status()
            comics = resp_comics.json()['data']['results']
            comic_ids = [comic["id"] for comic in comics]
            return comic_ids
        except requests.exceptions.RequestException as e:
            print(f"Error in request: {e}")
            if attempt < retries - 1:
                print(f"Retrying (attempt {attempt + 1} of {retries})...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print("Max retries reached. Exiting.")
                raise

# Function to write a CSV row for a character and comic ID
def write_csv_row(csv_writer, character_id, comic_id):
    csv_writer.writerow([character_id, comic_id])

# Function to process a character and retrieve their comics
def process_character(character, csv_writer, i):
    character_id = character["id"]
    character_name = character["name"]
    offset = 0

    while True:
        comic_ids = get_comic_ids(character_id, offset=offset)

        for comic_id in comic_ids:
            print(i, character_id, character_name, comic_id)
            write_csv_row(csv_writer, character_id, comic_id)

        if len(comic_ids) < COMIC_LIMIT:
            break  # Break the loop if we have retrieved all comics
        offset += COMIC_LIMIT

# Function to make paged requests to the Marvel Characters API and retrieve comics for each character
def paged_requests(page_size=100):
    params = {'apikey': PUBLIC_KEY, 'limit': page_size}
    csv_file_name = "marvel_characters_comics.csv"

    with open(csv_file_name, mode="w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=",")
        csv_writer.writerow(["Character ID", "Comic ID"])  # Write header row to the CSV file

        for i in range(1, 17):  # Assuming character IDs start from 1
            hash_params = get_hash_and_ts_params()
            params.update(hash_params)
            params.update({'offset': page_size * i})

            retries = 3  # Number of retries for API requests
            for attempt in range(retries):
                try:
                    resp_characters = requests.get(CHARACTER_URL, params=params)
                    resp_characters.raise_for_status()

                    for character in resp_characters.json()['data']['results']:
                        process_character(character, csv_writer, i)

                    break  # Break the retry loop if successful
                except requests.exceptions.RequestException as e:
                    print(f"Error in request: {e}")
                    if attempt < retries - 1:
                        print(f"Retrying (attempt {attempt + 1} of {retries})...")
                        time.sleep(60 ** attempt)  # Exponential backoff
                    else:
                        print("Max retries reached. Skipping to the next iteration.")
                        break

if __name__ == '__main__':
    paged_requests()  # Call the paged_requests function
    print('Done')  # Print 'Done' when the process is completed






