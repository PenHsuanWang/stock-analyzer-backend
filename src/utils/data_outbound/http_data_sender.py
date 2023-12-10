import pandas as pd
import numpy as np
import requests
from typing import Union, Dict, Any


class HTTPDataSender:
    """
    A data exporter that sends data to an external HTTP server.

    This class handles the sending of data in the form of Pandas DataFrame,
    NumPy array, or a dictionary of DataFrames to a specified HTTP server
    using the provided method, with error handling and response processing.
    """

    def __init__(self, headers: Dict[str, Any] = None):
        """
        Initialize the HTTPDataSender with optional headers.

        :param headers: A dictionary of HTTP headers to include in the request.
        """
        self.headers = headers or {
            "Content-Type": "application/json",  # Default header
            # "Authorization": "Bearer YOUR_TOKEN",  # Uncomment and replace with your token if required
        }

    def export_data(self, data: Union[pd.DataFrame, np.ndarray, Dict[str, pd.DataFrame]], url: str, method: str = 'POST') -> Any:
        """
        Send data to an HTTP server.

        :param data: A Pandas DataFrame, NumPy array, or a dictionary of DataFrames to be sent.
        :param url: The URL of the HTTP server to send data to.
        :param method: HTTP method to use for sending data (default is POST).
        :return: The processed response from the HTTP server.
        :raises requests.RequestException: If a request error occurs.
        """
        if isinstance(data, pd.DataFrame):
            payload = data.to_json()
        elif isinstance(data, np.ndarray):
            payload = data.tolist()
        elif isinstance(data, dict):
            payload = {key: value.to_json() for key, value in data.items()}
        else:
            raise ValueError("Unsupported data type")

        try:
            response = requests.request(method, url, headers=self.headers, data=payload)
            response.raise_for_status()  # Raises a HTTPError if the HTTP request returned an unsuccessful status code
            return response.json()  # Assuming the ML system responds with JSON
        except requests.RequestException as e:
            print(f"An error occurred while sending data: {e}")
            raise

# Example usage:
# http_sender = HTTPDataSender({"Authorization": "Bearer YOUR_API_TOKEN"})
# response = http_sender.export_data(df, "http://ml-system-endpoint/api/data", "POST")
# print(response)
