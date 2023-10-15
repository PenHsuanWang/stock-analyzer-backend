import requests


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
    # Define some test parameters for the daily return computation
    stock_id = "TSM"  # This should be a stock ID that you have stored in Redis
    start_date = "2023-01-01"  # Adjust these dates according to your data
    end_date = "2023-10-10"

    # Make the request
    request_daily_return(stock_id, start_date, end_date)
