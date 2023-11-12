import requests
import pandas as pd

BASE_URL = "http://localhost:8000"

def stash_stock_data(stock_id, start_date, end_date):
    # Function to fetch and stash stock data into Redis
    endpoint = f"{BASE_URL}/stock_data/fetch_and_stash"
    data = {
        "stock_id": stock_id,
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.post(endpoint, json=data)
    if response.status_code == 200:
        print("Stock data fetched and stashed successfully.")
    else:
        print(f"Failed to stash stock data: {response.text}")


def check_and_prepare_stock_data(stock_id, start_date, end_date):
    # Check if raw stock data exists
    endpoint = f"{BASE_URL}/stock_data/check_data_exists"
    data = {
        "prefix": "raw_stock_data",
        "stock_id": stock_id,
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.post(endpoint, json=data)

    # If raw data does not exist, fetch and stash it
    if not response.json().get('exists', False):
        stash_stock_data(stock_id, start_date, end_date)
        return True
    return response.json().get('exists', False)


def get_analyzed_data(stock_id, start_date, end_date):
    # Function to fetch analyzed stock data
    endpoint = f"{BASE_URL}/stock_data/get_data"
    data = {
        "prefix": "analyzed_stock_data",
        "stock_id": stock_id,
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.post(endpoint, json=data)
    if response.status_code == 200:
        return pd.DataFrame(response.json()['data'])
    else:
        print(f"Failed to get analyzed stock data: {response.text}")
        return None

def perform_full_stock_analysis(stock_id: str, start_date: str, end_date: str, window_sizes: list[int]):
    # Ensure raw stock data is prepared
    if not check_and_prepare_stock_data(stock_id, start_date, end_date):
        print("Stock data preparation failed.")
        return

    # Define the API endpoint for full analysis
    url = f"{BASE_URL}/stock_data/compute_full_analysis_and_store"
    data = {
        "prefix": "raw_stock_data",
        "stock_id": stock_id,
        "start_date": start_date,
        "end_date": end_date,
        "window_sizes": window_sizes
    }

    # Make the POST request for analysis
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(response.json().get("message", "Full analysis completed and data stored."))

            # Get the analyzed data
            analyzed_data = get_analyzed_data(stock_id, start_date, end_date)
            if analyzed_data is not None:
                pd.set_option('display.max_rows', None)
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', None)
                print("Analyzed Data:")
                print(analyzed_data.head(30))
        else:
            print(f"Full analysis request failed with status code {response.status_code}: {response.text}")
    except requests.RequestException as e:
        print(f"Full analysis request failed due to an error: {e}")

if __name__ == "__main__":
    stock_id = "TSM"
    start_date = "2020-01-01"
    end_date = "2020-12-31"
    window_sizes = [5, 10, 20]

    perform_full_stock_analysis(stock_id, start_date, end_date, window_sizes)
