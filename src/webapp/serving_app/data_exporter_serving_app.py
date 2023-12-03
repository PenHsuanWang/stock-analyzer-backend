import threading
import pandas as pd
from src.utils.data_outbound.csv_exporter import CSVExporter
from src.utils.data_outbound.http_data_sender import HTTPDataSender


class DataExporterApp:
    _app = None
    _app_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._app_lock:
            if cls._app is None:
                cls._app = super().__new__(cls)
            return cls._app

    @staticmethod
    def export_to_csv(data: pd.DataFrame, filepath: str) -> None:
        """
        Export data to a CSV file.

        :param data: DataFrame to be exported.
        :param filepath: File path where to save the CSV.
        """
        exporter = CSVExporter()
        exporter.export_data(data, filepath)

    @staticmethod
    def send_data_http(data: pd.DataFrame, url: str, method: str = 'POST') -> None:
        """
        Send data to an HTTP server.

        :param data: DataFrame or NumPy array to be sent.
        :param url: URL of the HTTP server.
        :param method: HTTP method to be used.
        """
        sender = HTTPDataSender()
        sender.export_data(data, url, method)


def get_app():
    return DataExporterApp()
