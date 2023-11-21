import requests
import pandas as pd

# Define base URL for the FastAPI server
BASE_URL = "http://localhost:8000"


# Function to fetch and stash stock data into Redis using the DataManagerApp
def stash_stock_data(stock_id, start_date, end_date):
    endpoint = f"{BASE_URL}/stock_data/fetch_and_stash"
    data = {
        "stock_id": stock_id,
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.post(endpoint, json=data)
    print(response.json())


# Function to check if stock data exists in Redis
def check_data_exists(prefix, stock_id, start_date, end_date):
    endpoint = f"{BASE_URL}/stock_data/check_data_exists"
    data = {
        "prefix": prefix,
        "stock_id": stock_id,
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.post(endpoint, json=data)
    return response.json()['exists']


# Function to get stock data from Redis
def get_stock_data(prefix, stock_id, start_date, end_date):
    endpoint = f"{BASE_URL}/stock_data/get_data"
    data = {
        "prefix": prefix,
        "stock_id": stock_id,
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.post(endpoint, json=data)
    return pd.DataFrame(response.json()['data'])


# Function to update stock data in Redis
def update_stock_data(prefix, stock_id, start_date, end_date, df):
    endpoint = f"{BASE_URL}/stock_data/update_data"
    data = {
        "prefix": prefix,
        "stock_id": stock_id,
        "start_date": start_date,
        "end_date": end_date,
        "updated_dataframe": df.to_dict(orient='records')
    }
    response = requests.post(endpoint, json=data)
    print(response.json())


# Function to delete stock data from Redis
def delete_stock_data(prefix, stock_id, start_date, end_date):
    endpoint = f"{BASE_URL}/stock_data/delete_data"
    data = {
        "prefix": prefix,
        "stock_id": stock_id,
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.post(endpoint, json=data)
    print(response.json())


def analyze_candlestick_patterns(stock_id, start_date, end_date):
    endpoint = f"{BASE_URL}/stock_data/analyze_candlestick_patterns"
    data = {
        "stock_ids": [stock_id],
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.post(endpoint, json=data)
    return pd.DataFrame(response.json())


# Example usage
if __name__ == "__main__":
    stock_id = "AAPL"
    start_date = "2023-01-01"
    end_date = "2023-10-10"
    prefix = "raw_stock_data"

    # Stash stock data
    stash_stock_data(stock_id, start_date, end_date)

    # Check if data exists
    if check_data_exists(prefix, stock_id, start_date, end_date):
        print(f"Data for {stock_id} exists.")

        # Get the stock data
        df = get_stock_data(prefix, stock_id, start_date, end_date)
        print(f"Fetched data for {stock_id}:")
        print(df.head())

        # Analyze candlestick patterns
        candlestick_patterns_df = analyze_candlestick_patterns(stock_id, start_date, end_date)
        print(f"Candlestick patterns for {stock_id}:")
        print(candlestick_patterns_df.head(30))
        candlestick_patterns_df.to_csv("./test_candlestick_ana_aapl.csv")

        # Make some changes to the data (for demonstration purposes, we'll just add a new column here)
        df['example_new_col'] = 42

        # Update the stock data with the changes
        update_stock_data(prefix, stock_id, start_date, end_date, df)

        # Eventually, delete the stock data
        delete_stock_data(prefix, stock_id, start_date, end_date)
    else:
        print(f"No data found for {stock_id} between {start_date} and {end_date}.")
