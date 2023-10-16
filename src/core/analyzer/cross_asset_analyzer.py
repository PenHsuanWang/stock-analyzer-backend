"""
CrossAssetAnalyzer Module

This module provides functionalities to calculate correlations between multiple stock assets based on various metrics such as close price and daily return.
"""

import pandas as pd
from stockana import calc_cross_asset
from core.manager.data_manager import DataIOButler, DataNotFoundError


class CrossAssetAnalyzer:
    """
    The CrossAssetAnalyzer class provides methods to analyze correlations between various stock assets.

    Attributes:
        data_io_butler (DataIOButler): An instance of DataIOButler to handle data extraction from Redis.
    """

    def __init__(self):
        self.data_io_butler = DataIOButler()

    def calculate_close_price_correlation(self, stock_ids: list[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Extract data from Redis for multiple stocks and calculate their correlation based on close price.

        :param stock_ids: List of Stock IDs from yfinance.
        :return: DataFrame of correlations
        """
        return self._calculate_correlation_based_on_column(stock_ids, start_date, end_date, 'Close')

    def calculate_daily_return_correlation(self, stock_ids: list[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Extract data from Redis for multiple stocks and calculate their correlation based on daily return.

        :param stock_ids: List of Stock IDs from yfinance.
        :return: DataFrame of correlations
        """
        return self._calculate_correlation_based_on_column(stock_ids, start_date, end_date, 'Daily_Return')

    def _calculate_correlation_based_on_column(self, stock_ids: list[str], start_date: str, end_date: str, column: str) -> pd.DataFrame:
        """
        General method to extract data from Redis for multiple stocks and calculate their correlation based on a specified column.

        :param stock_ids: List of Stock IDs from yfinance.
        :param column: Column based on which the correlation should be calculated.
        :return: DataFrame of correlations
        """

        series_list = []

        for stock_id in stock_ids:
            try:
                # Extract stock data from Redis
                stock_data = self.data_io_butler.get_data(stock_id, start_date, end_date)
                series_list.append(stock_data[column])

            except DataNotFoundError:
                print(f"No data found for stock ID {stock_id} from {start_date} to {end_date} in Redis.")
                continue
            except Exception as e:
                print(f"An error occurred: {e}")

        # Calculate correlation
        correlation_df = calc_cross_asset.calculate_correlation(series_list)
        return correlation_df
