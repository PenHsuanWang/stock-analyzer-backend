import requests
import json

BASE_URL = "http://localhost:8000"  # Assuming FastAPI server is running on localhost and port 8000

def check_data_exists(stock_id: str, start_date: str, end_date: str) -> bool:
    endpoint = "/stock_data/check_data_exists"
    response = requests.post(
        f"{BASE_URL}{endpoint}",
        json={
            "stock_id": stock_id,
            "start_date": start_date,
            "end_date": end_date
        }
    )
    data = response.json()
    return data.get("exists", False)

def get_stock_data(stock_id: str, start_date: str, end_date: str):
    endpoint = "/stock_data/get_data"
    response = requests.post(
        f"{BASE_URL}{endpoint}",
        json={
            "stock_id": stock_id,
            "start_date": start_date,
            "end_date": end_date
        }
    )
    print(response.text)
    data = response.json()
    return data.get("stock_data")

def update_stock_data(stock_id: str, start_date: str, end_date: str, updated_dataframe: dict) -> bool:
    endpoint = "/stock_data/update_data"
    response = requests.post(
        f"{BASE_URL}{endpoint}",
        json={
            "stock_id": stock_id,
            "start_date": start_date,
            "end_date": end_date,
            "updated_dataframe": updated_dataframe
        }
    )
    data = response.json()
    return data.get("updated", False)

def delete_stock_data(stock_id: str, start_date: str, end_date: str) -> bool:
    endpoint = "/stock_data/delete"
    response = requests.post(
        f"{BASE_URL}{endpoint}",
        json={
            "stock_id": stock_id,
            "start_date": start_date,
            "end_date": end_date
        }
    )
    data = response.json()
    return data.get("deleted", False)

if __name__ == "__main__":
    # Test the provided functions
    stock_id = "TSM"
    start_date = "2023-01-01"
    end_date = "2023-10-10"

    # Check if data exists
    print(f"Data exists for {stock_id} from {start_date} to {end_date}: {check_data_exists(stock_id, start_date, end_date)}")
    # Get stock data
    stock_data = get_stock_data(stock_id, start_date, end_date)
    print(stock_data)

    print("Fetched stock data:")
    print(json.dumps(stock_data, indent=4))

    # Update stock data - for the purpose of this example, we'll just send the fetched data back without any changes
    updated = update_stock_data(stock_id, start_date, end_date, stock_data.to_dict(orient="records"))
    print(f"Stock data updated: {updated}")

    # Delete stock data
    # Uncomment the below lines if you really want to delete the stock data
    # deleted = delete_stock_data(stock_id, start_date, end_date)
    # print(f"Stock data deleted: {deleted}")
