import pandas as pd
import requests
from src.utils.data_outbound.http_data_sender import HTTPDataSender

# Define the base URL of the FastAPI server
BASE_URL = "http://localhost:8000"

# Function to send data over HTTP to another service
def send_data_over_http(data, url, method='POST'):
    # Create an instance of HTTPDataSender
    http_sender = HTTPDataSender()

    # Send the example data over HTTP using HTTPDataSender
    try:
        response = http_sender.export_data(data, url)
        # print("Raw Server Response:", response.text)  # Print raw response
        # try:
        #     print("Data sent over HTTP successfully. Server response:", response.json())
        # except ValueError:
        #     print("Data sent over HTTP successfully. Server response text:", response.text)
    except Exception as e:
        print(f"Failed to send data over HTTP: {e}")


# Example data extracted from the 'AAPL.csv' file
example_data = {
    'Date': ['2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-09',
             '2023-01-10', '2023-01-11', '2023-01-12', '2023-01-13', '2023-01-17'],
    'Open': [130.28, 126.89, 127.13, 126.01, 130.47, 130.26, 131.25, 133.88, 132.03, 134.83],
    'High': [130.90, 128.66, 127.77, 130.29, 133.41, 131.26, 133.51, 134.26, 134.92, 137.29],
    'Low': [124.17, 125.08, 124.76, 124.89, 129.89, 128.12, 130.46, 131.44, 131.66, 134.13],
    'Close': [125.07, 126.36, 125.02, 129.62, 130.15, 130.73, 133.49, 133.41, 134.76, 135.94],
    'Adj Close': [124.37, 125.66, 124.33, 128.90, 129.43, 130.00, 132.75, 132.67, 134.01, 135.18],
    'Volume': [112117500, 89113600, 80962700, 87754700, 70790800,
               63896200, 69458900, 71379600, 57809700, 63646600]
}

example_df = pd.DataFrame(example_data)

# The target HTTP endpoint for data export
target_url = "http://localhost:3333"

# Send the example data over HTTP
send_data_over_http(data=example_df, url=target_url)
