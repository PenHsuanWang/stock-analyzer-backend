import numpy as np
import pandas as pd
from typing import List, Dict
from .preprocessor_base import PreprocessorBase


class TimeSeriesPreprocessor(PreprocessorBase):
    def __init__(self, df: pd.DataFrame, window_size: int):
        """
        Initialize the TimeSeriesPreprocessor.

        :param df: Input DataFrame.
        :param window_size: Size of the window for creating time series segments.
        """
        super().__init__(df)
        self.window_size = window_size

    def transform(self, selected_columns: List[str]) -> Dict[str, np.ndarray]:
        """
        Transforms the DataFrame into time series data.

        This method converts selected columns from the DataFrame into time series format,
        which is particularly useful for preparing data for time series analysis and
        neural network models like LSTM.

        :param selected_columns: List of column names to be transformed into time series.
        :return: A dictionary with keys as column names and values as time series data arrays.
        """
        series_dict = {}
        for column in selected_columns:
            if column in self.df.columns:
                series = self.df[column].to_numpy()
                series_dict[column] = self.create_windows(series)
        return series_dict

    def create_windows(self, series: np.ndarray) -> np.ndarray:
        """
        Creates sliding windows from a time series.

        This method takes a single time series array and generates a sequence of
        overlapping windows, each of the specified window size.

        :param series: A numpy array representing a single time series.
        :return: A numpy array of sliding windows created from the input series.
        """
        windows = [series[i:(i + self.window_size)] for i in range(len(series) - self.window_size + 1)]
        return np.array(windows)

