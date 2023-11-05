import requests
import sys


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
            print(response.json().get("message",
                                      f"Operation completed for {stock_id} from {start_date} to {end_date}, but no message returned."))
        else:
            print(
                f"Request for {stock_id} from {start_date} to {end_date} failed with status code {response.status_code}: {response.text}")
            print(response.json().get("message"))

    except requests.RequestException as e:
        print(f"Request failed due to an error: {e}")


if __name__ == "__main__":
    # if len(sys.argv) < 4:
    #     print("Usage: python example_data_fetch_and_stash_into_redis.py <stock_id> <start_date> <end_date>")
    #     sys.exit(1)

    # usage python example_data_fetch_and_stash_into_redis.py TSM 2023-01-01 2023-10-10
    # stash_stock_data(sys.argv[1], sys.argv[2], sys.argv[3])

    stash_stock_data("GOOGL", "2022-01-01", "2022-10-10")
