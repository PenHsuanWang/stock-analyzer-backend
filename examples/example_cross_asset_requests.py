import requests

def request_asset_correlation(stock_ids: list[str], start_date: str, end_date: str, metric: str):
    # Define the API endpoint for asset correlation computation
    url = "http://localhost:8000/stock_data/compute_assets_correlation"

    # Define the payload with stock details
    data = {
        "stock_ids": stock_ids,
        "start_date": start_date,
        "end_date": end_date,
        "metric": metric
    }

    try:
        # Make the POST request
        response = requests.post(url, json=data)

        # Check response
        if response.status_code == 200:
            correlation_data = response.json()
            print("Asset Correlation Matrix based on:", metric)
            for key, value in correlation_data.items():
                print(key, value)
        else:
            print(f"Request failed with status code {response.status_code}: {response.text}")

    except requests.RequestException as e:
        print(f"Request failed due to an error: {e}")


if __name__ == "__main__":
    # Define some test parameters for the asset correlation computation
    stock_ids = ["AAPL", "TSM", "GOOGL"]  # Add more stock IDs that you have stored in Redis
    start_date = "2023-01-01"  # Adjust these dates according to your data
    end_date = "2023-10-10"
    metric = "Daily_Return"  # You can change this to 'Close', 'Open', etc., based on the desired metric

    # Make the request
    request_asset_correlation(stock_ids, start_date, end_date, metric)
