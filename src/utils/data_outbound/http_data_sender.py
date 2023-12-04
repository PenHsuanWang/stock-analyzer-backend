import pandas as pd
import numpy as np
import requests
from typing import Union, Dict
from .base import DataExporter


class HTTPDataSender(DataExporter):
    """
    A data exporter that sends data to an external HTTP server.

    This class handles the sending of data in the form of Pandas DataFrame,
    NumPy array, or a dictionary of DataFrames to a specified HTTP server
    using the provided method.
    """

    def export_data(self, data: Union[pd.DataFrame, np.ndarray, Dict[str, pd.DataFrame]], url: str, method: str = 'POST') -> requests.Response:
        """
        Send data to an HTTP server.

        :param data: A Pandas DataFrame, NumPy array, or a dictionary of DataFrames to be sent.
        :param url: The URL of the HTTP server to send data to.
        :param method: HTTP method to use for sending data (default is POST).
        :return: The response from the HTTP server.
        :raises ValueError: If data type is not supported.
        """
        if isinstance(data, pd.DataFrame):
            data = data.to_json()
        elif isinstance(data, np.ndarray):
            data = data.tolist()
        elif isinstance(data, dict):
            # Convert each DataFrame in the dictionary to JSON
            data = {key: value.to_json() for key, value in data.items()}
        else:
            raise ValueError("Unsupported data type")

        response = requests.request(method, url, json={"data": data})
        return response