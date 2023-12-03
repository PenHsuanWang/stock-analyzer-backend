import pandas as pd
from .base import DataExporter


class CSVExporter(DataExporter):
    """
    A data exporter that exports data into CSV format.

    This class handles the exporting of Pandas DataFrame to a CSV file.
    """

    def export_data(self, data: pd.DataFrame, filepath: str) -> None:
        """
        Export a DataFrame to a CSV file.

        :param data: A Pandas DataFrame to be exported.
        :param filepath: The file path where the CSV will be saved.
        """
        data.to_csv(filepath)

