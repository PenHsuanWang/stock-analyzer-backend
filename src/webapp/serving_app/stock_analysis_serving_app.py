"""
The stock analysis serving application integrated all applications related with stock analysis
Only operating the data that have been store in internal db. Do not responsible to fetch new dataset set from
outer sources.
"""

import threading
from core.manager.data_manager import DataIOButler
from core.analyzer.moving_average_analyzer import MovingAverageAnalyzer
from core.analyzer.daily_return_analyzer import DailyReturnAnalyzer


class StockAnalysisServingApp:
    _app_instance = None
    _app_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._app_lock:
            if cls._app_instance is None:
                cls._app_instance = super().__new__(cls)
                cls._app_instance._data_io_butler = DataIOButler()
                cls._app_instance._ma_analyzer = MovingAverageAnalyzer()
                cls._daily_return_analyzer = DailyReturnAnalyzer()
            return cls._app_instance

    def calculating_moving_average_and_saved_as_analyzed_prefix(
            self, prefix: str, stock_id: str, start_date: str, end_date: str,
            window_sizes: list[int]) -> None:
        """
        Fetches raw stock data, stores it in Redis, calculates moving averages, and returns the 'Close' price data.
        saved the new data with moving average back to redis

        :param prefix: Prefix for the Redis key.
        :param stock_id: ID of the stock.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :param window_sizes: List of window sizes for moving average calculation.
        :return: Dictionary containing 'Close' price data and moving averages.
        """

        if prefix is not "analyzed_stock_data":
            prefix = "raw_stock_data"

        # Calculate Moving Average
        try:
            self._ma_analyzer.calculate_moving_average(prefix, stock_id, start_date, end_date, window_sizes)
        except Exception as e:
            print(f"Error of calculated moving average: {e}")

    def calculating_daily_return_and_saved_as_analyzed_prefix(
            self, prefix: str, stock_id: str, start_date: str, end_date: str) -> None:
        """
        Fetches stock data from Redis, calculates daily returns, and saves the updated data back to Redis with the 'analyzed_stock_data' prefix.

        :param prefix: Prefix for the Redis key. It should be 'raw_stock_data' for the input data.
        :param stock_id: ID of the stock.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        """
        if prefix != "raw_stock_data":
            raise ValueError("The prefix for fetching data should be 'raw_stock_data'.")

        # Calculate Daily Return
        try:
            self._daily_return_analyzer.calculate_daily_return("analyzed_stock_data", stock_id, start_date, end_date)
        except Exception as e:
            print(f"Error while calculating daily return: {e}")


def get_stock_analysis_serving_app():
    return StockAnalysisServingApp()
