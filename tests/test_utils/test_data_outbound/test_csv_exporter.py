# test_csv_exporter.py
import pandas as pd
import os
from src.utils.data_outbound.csv_exporter import CSVExporter


def test_csv_exporter():
    # test DataFrame
    test_data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    test_filepath = "test_output.csv"

    # initialized CSVExporter and export data
    exporter = CSVExporter()
    exporter.export_data(test_data, test_filepath)

    # check the file is created
    assert os.path.exists(test_filepath)

    os.remove(test_filepath)
