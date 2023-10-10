import requests
import pandas as pd
import json
from io import StringIO

# Define the API endpoint
url = "http://localhost:8000/stock_data/fetch_and_get_as_dataframe"

# Define the payload with stock details
data = {
    "stock_id": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2023-10-10"
}

# Make the POST request
response = requests.post(url, json=data)

if response.status_code == 200:
    # First parsing of the JSON content
    first_parse = json.loads(response.text)

    # Check if the parsed content is still a string (double serialization issue)
    if isinstance(first_parse, str):
        data_list = json.loads(first_parse)
    else:
        data_list = first_parse

    # Create the dataframe
    dataframe = pd.DataFrame(data_list)
    print(dataframe.head())
else:
    print(f"Request failed with status code {response.status_code}: {response.text}")
