import requests

def request_full_analysis(stock_id: str, start_date: str, end_date: str, window_sizes: list[int]):
    # Define the API endpoint for full analysis computation
    url = "http://localhost:8000/stock_data/compute_full_analysis_and_store"
    # Define the payload with stock details and window sizes for moving average calculation
    data = {
        "prefix": "raw_stock_data",
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
            print(response.json().get("message", "Full analysis completed and stored successfully."))
        else:
            print(f"Full analysis request failed with status code {response.status_code}: {response.text}")
    except requests.RequestException as e:
        print(f"Full analysis request failed due to an error: {e}")


if __name__ == "__main__":
    # Define parameters
    stock_id = "TSM"
    start_date = "2023-01-01"
    end_date = "2023-10-10"
    window_sizes = [5, 10, 20]

    # Request full analysis (both moving averages and daily returns) and store in Redis
    request_full_analysis(stock_id, start_date, end_date, window_sizes)

    # The remainder of the code is for fetching and printing the data from Redis,
    # which remains unchanged since it's for demonstration purposes.
    # ...
