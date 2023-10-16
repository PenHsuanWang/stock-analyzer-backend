import requests
from src.core.manager.data_manager import DataIOButler, DataNotFoundError

def stash_stock_data(stock_id: str, start_date: str, end_date: str):
    # Define the API endpoint
    url = "http://localhost:8000/stock_data/fetch_and_stash"
    # Define the payload with stock details
    data = {
        "stock_id": stock_id,
        "start_date": start_date,
        "end_date": end_date
    }
    try:
        # Make the POST request
        response = requests.post(url, json=data)
        # Check response
        if response.status_code == 200:
            print(response.json().get("message", f"Operation completed for {stock_id} from {start_date} to {end_date}, but no message returned."))
        else:
            print(f"Request for {stock_id} from {start_date} to {end_date} failed with status code {response.status_code}: {response.text}")
    except requests.RequestException as e:
        print(f"Request failed due to an error: {e}")

def request_moving_average(stock_id: str, start_date: str, end_date: str, window_sizes: list[int]):
    # Define the API endpoint for moving average computation
    url = "http://localhost:8000/stock_data/compute_and_store_moving_average"
    # Define the payload with stock details and window sizes
    data = {
        "stock_id": stock_id,
        "start_date": start_date,
        "end_date": end_date,
        "window_sizes": window_sizes
    }
    try:
        # Make the POST request
        response = requests.post(url, json=data)
        # Check response
        if response.status_code == 200:
            print(response.json().get("message", "Operation completed, but no message returned."))
        else:
            print(f"Request failed with status code {response.status_code}: {response.text}")
    except requests.RequestException as e:
        print(f"Request failed due to an error: {e}")


def request_daily_return(stock_id: str, start_date: str, end_date: str):
    # Define the API endpoint for daily return computation
    url = "http://localhost:8000/stock_data/compute_and_store_daily_return"

    # Define the payload with stock details
    data = {
        "stock_id": stock_id,
        "start_date": start_date,
        "end_date": end_date
    }

    try:
        # Make the POST request
        response = requests.post(url, json=data)

        # Check response
        if response.status_code == 200:
            print(response.json().get("message", "Operation completed, but no message returned."))
        else:
            print(f"Request failed with status code {response.status_code}: {response.text}")

    except requests.RequestException as e:
        print(f"Request failed due to an error: {e}")


if __name__ == "__main__":
    # Define parameters
    stock_id = "GOOGL"
    start_date = "2023-01-01"
    end_date = "2023-10-10"
    window_sizes = [5, 10, 20]

    # Fetch stock data and stash into Redis
    stash_stock_data(stock_id, start_date, end_date)

    # Compute moving averages and store in Redis
    request_moving_average(stock_id, start_date, end_date, window_sizes)

    # Compute daily returns and store in Redis
    request_daily_return(stock_id, start_date, end_date)

    # check the data in the redis

    data_io_butler = DataIOButler()

    # List all keys in Redis matching the pattern 'stock_data:*'
    keys = data_io_butler.get_all_exist_data_key()
    if not keys:
        print("No stock data keys found in Redis.")
        exit()

    for key in keys:
        print(key.decode('utf-8'))

    # Just fetching data for the first key as an example
    key = keys[0].decode('utf-8')  # Convert bytes to string
    print(f"Fetching data for key: {key}")

    # Extract stock_id, start_date, and end_date from the key
    _, stock_id, start_date, end_date = key.split(":")  # Assumes the key format is consistent


    def fetch_and_print():
        try:
            # Remove await since get_data is not asynchronous
            data_frame = data_io_butler.get_data(stock_id, start_date, end_date)
            print(data_frame.tail())
        except DataNotFoundError as e:
            print(str(e))


    fetch_and_print()
