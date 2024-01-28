import numpy as np
import pandas as pd
from typing import List, Dict
from .preprocessor_base import PreprocessorBase


class TimeSeriesPreprocessor(PreprocessorBase):
    """
    A preprocessor for transforming time series data.

    This class extends PreprocessorBase and implements the transformation of time
    series data into a format suitable for time series analysis or neural network
    models. It focuses on creating overlapping windows from time series data,
    which can be used for various time series forecasting models.

    Attributes:
        window_size (int): The size of the window used to create time series segments.
    """

    def __init__(self, window_size: int):
        """
        Initialize the TimeSeriesPreprocessor.

        :param window_size: Size of the window for creating time series segments.
        """
        super().__init__()

        self.window_size = window_size

    @staticmethod
    def transform(df: pd.DataFrame, window_size: int, selected_columns: List[str]) -> Dict[str, np.ndarray]:
        """
        Transforms the DataFrame into time series data.

        This method converts selected columns from the DataFrame into time series format,
        which is particularly useful for preparing data for time series analysis and
        neural network models like LSTM.

        :param df: Input DataFrame to be transformed.
        :param window_size: Size of the window for creating time series segments.
        :param selected_columns: List of column names to be transformed into time series.
        :return: A dictionary with keys as column names and values as time series data arrays.
        """
        series_dict = {}
        for column in selected_columns:
            if column in df.columns:
                series = df[column].to_numpy()
                series_dict[column] = TimeSeriesPreprocessor.create_windows(series, window_size)
        return series_dict

    @staticmethod
    def create_windows(series: np.ndarray, window_size: int) -> np.ndarray:
        """
        Creates sliding windows from a time series.

        This method takes a single time series array and generates a sequence of
        overlapping windows, each of the specified window size.

        :param series: A numpy array representing a single time series.
        :param window_size: Size of the window for creating time series segments.
        :return: A numpy array of sliding windows created from the input series.
        """
        windows = [series[i:(i + window_size)] for i in range(len(series) - window_size + 1)]
        return np.array(windows)
