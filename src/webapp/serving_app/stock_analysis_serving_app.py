"""
The stock analysis serving application integrated all applications related with stock analysis
Only operating the data that have been store in internal db. Do not responsible to fetch new dataset set from
outer sources.
"""

import threading
import redis.exceptions
import logging
import pandas as pd

from fastapi import HTTPException

from core.analyzer.moving_average_analyzer import MovingAverageAnalyzer
from core.analyzer.daily_return_analyzer import DailyReturnAnalyzer
from core.analyzer.cross_asset_analyzer import CrossAssetAnalyzer
from core.manager.data_manager import DataIOButler, DataNotFoundError

logger = logging.getLogger()


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
                cls._app_instance._cross_asset_analyzer = CrossAssetAnalyzer()
            return cls._app_instance

    def calculating_ma_and_daily_return_and_saved_as_analyzed_prefix(
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
            #  To do refactor, extract and save analyzed dataframe at here
            stock_data = self._data_io_butler.get_data(prefix, stock_id, start_date, end_date)
            analyzed_data = self._ma_analyzer.calculate_moving_average(stock_data, window_sizes)
            analyzed_data = self._daily_return_analyzer.calculate_daily_return(analyzed_data)
            self._data_io_butler.save_data("analyzed_stock_data", stock_id, start_date, end_date, analyzed_data)
        except DataNotFoundError:
            error_message = f"No data found for stock ID {stock_id} from {start_date} to {end_date}."
            logger.error(error_message)
            raise HTTPException(status_code=404, detail=error_message)

        except redis.exceptions.RedisError as re:
            error_message = f"Redis error occurred: {re}"
            logger.error(error_message)
            raise HTTPException(status_code=500, detail=error_message)

        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            logger.exception(error_message)
            raise HTTPException(status_code=500, detail=error_message)

    @staticmethod
    def calculate_and_store_correlation(
            stock_ids: list[str], start_date: str, end_date: str, metric: str) -> pd.DataFrame:
        """
        Fetches stock data and calculates the correlation between the assets.

        :param stock_ids: List of stock IDs to calculate correlation.
        :param start_date: Start date for the correlation calculation.
        :param end_date: End date for the correlation calculation.
        :param metric: The metric on which to base the correlation calculation.
        :return: DataFrame with correlation results.
        """
        data_io_butler = DataIOButler()
        series_list = []

        for stock_id in stock_ids:
            try:
                stock_data = data_io_butler.get_data("analyzed_stock_data", stock_id, start_date, end_date)
                stock_series = stock_data[metric]
                stock_series.name = stock_id
                series_list.append(stock_series)
            except DataNotFoundError:
                print(f"No data found for stock ID {stock_id} from {start_date} to {end_date}.")
                continue
            except Exception as e:
                print(f"An error occurred: {e}")

        cross_asset_analyzer = CrossAssetAnalyzer()
        correlation_df = cross_asset_analyzer.calculate_correlation(series_list)
        return correlation_df


def get_stock_analysis_serving_app():
    return StockAnalysisServingApp()
