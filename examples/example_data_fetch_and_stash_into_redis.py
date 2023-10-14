import requests

# Define the API endpoint
url = "http://localhost:8000/stock_data/fetch_and_stash"

# Define the payload with stock details
data = {
    "stock_id": "TSM",
    "start_date": "2023-01-01",
    "end_date": "2023-10-10"
}

# Make the POST request
response = requests.post(url, json=data)

# Check response
if response.status_code == 200:
    print(response.json().get("message", "Operation completed, but no message returned."))
else:
    print(f"Request failed with status code {response.status_code}: {response.text}")
