"""
CrossAssetAnalyzer Module

This module provides functionalities to calculate correlations between multiple stock assets based on various metrics such as close price and daily return.
"""

import pandas as pd
from stockana import calc_cross_asset


class CrossAssetAnalyzer:

    @staticmethod
    def calculate_correlation(series_list: list[pd.Series]) -> pd.DataFrame:
        """
        Calculate the correlation matrix for a list of pandas Series.

        :param series_list: A list of pandas Series where each series represents a stock's data.
        :return: A DataFrame representing the correlation matrix.
        """
        if not series_list:
            return pd.DataFrame()

        correlation_df = calc_cross_asset.calculate_correlation(series_list)
        return correlation_df