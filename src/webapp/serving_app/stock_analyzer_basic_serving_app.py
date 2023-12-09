"""
The stock analyzer basic serving application integrated all applications related with initial operations of
stock analysis, included data fetch and basic analysis, such as moving average calculation, daily return, and
candle stick operation. Fetch raw data and do basic analysis and store into redis database for stash.
"""

import threading
import redis.exceptions
import logging
import pandas as pd


from fastapi import HTTPException

from src.core.analyzer.moving_average_analyzer import MovingAverageAnalyzer
from src.core.analyzer.daily_return_analyzer import DailyReturnAnalyzer
from src.core.analyzer.cross_asset_analyzer import CrossAssetAnalyzer
from src.core.analyzer.candlestick_pattern_analyzer import CandlestickPatternAnalyzer
from src.core.analyzer.advance_financial_analyzer import AdvancedFinancialAnalyzer

from src.core.manager.data_manager import DataIOButler, DataNotFoundError

from src.utils.data_inbound.data_fetcher import YFinanceFetcher
from src.utils.database_adapters.redis_adapter import RedisAdapter

logger = logging.getLogger()


class StockAnalyzerBasicServingApp:
    _app_instance = None
    _app_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._app_lock:
            if cls._app_instance is None:
                cls._app_instance = super().__new__(cls)
                cls._data_fetcher = YFinanceFetcher()
                cls._app_instance._data_io_butler = DataIOButler(adapter=RedisAdapter())
                cls._app_instance._ma_analyzer = MovingAverageAnalyzer()
                cls._daily_return_analyzer = DailyReturnAnalyzer()
                cls._app_instance._cross_asset_analyzer = CrossAssetAnalyzer()
                cls._app_instance._candlestick_pattern_analyzer = CandlestickPatternAnalyzer()
                cls._app_instance._advanced_financial_analyzer = AdvancedFinancialAnalyzer()
            return cls._app_instance

    def _fetch_data_and_get_as_dataframe(self, stock_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        provide stock id and time range, calling the data fetcher to extract stock price data via yfinance api
        :param stock_id:
        :param start_date:
        :param end_date:
        :return:
        """
        try:
            self._data_fetcher.fetch_from_source(stock_id=stock_id, start_date=start_date, end_date=end_date)
        except Exception as e:
            print(f"error happen when fetching data. please check the input stock_id and time range. Full stack error: {e}")
            raise RuntimeError

        df = self._data_fetcher.get_as_dataframe()

        return df

    def _apply_candlestick_pattern_analyzer(self, stock_data: pd.DataFrame) -> pd.DataFrame:

        # Ensure required columns exist in the data
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(column in stock_data.columns for column in required_columns):
            missing_columns = [column for column in required_columns if column not in stock_data.columns]
            raise ValueError(f"Missing required columns in stock data: {missing_columns}")

        # Process data for candlestick pattern analysis
        processed_data = stock_data[required_columns].copy()
        patterns_df = self._candlestick_pattern_analyzer.analyze_patterns(processed_data)

        return patterns_df

    def fetch_and_do_full_basic_analysis_and_save(
            self, prefix: str, stock_id: str, start_date: str, end_date: str,
            window_sizes: list[int]
    ) -> None:
        """

        :param prefix:
        :param stock_id:
        :param start_date:
        :param end_date:
        :param window_sizes:
        :return:
        """

        try:
            # fetch data
            raw_df = self._fetch_data_and_get_as_dataframe(stock_id, start_date, end_date)
        except Exception as e:
            print("Failed to fetch data")
            error_message = f"An unexpected error occurred: {e} during fetching data"
            logger.exception(error_message)
            raise HTTPException(status_code=500, detail=error_message)

        try:
            # do full analysis
            analyzed_data = self._ma_analyzer.calculate_moving_average(raw_df, window_sizes)
            analyzed_data = self._daily_return_analyzer.calculate_daily_return(analyzed_data)
            analyzed_data["Pattern"] = self._apply_candlestick_pattern_analyzer(analyzed_data)["Pattern"]  # extract the `Pattern` Column and added to analyzed_data

            # save to redis
            self._data_io_butler.save_data(
                data=analyzed_data,
                prefix=prefix,
                stock_id=stock_id,
                start_date=start_date,
                end_date=end_date
            )

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

    def fetch_and_do_full_advanced_analysis_and_save(
            self, prefix: str, stock_id: str, start_date: str, end_date: str,
            short_window: int, long_window: int, volume_window: int
    ) -> None:
        """
        Fetches stock data, performs advanced financial analysis, and stores it into Redis.

        :param prefix: Prefix for Redis key.
        :param stock_id: Stock identifier.
        :param start_date: Start date for fetching data.
        :param end_date: End date for fetching data.
        :param short_window: Short window period for indicators.
        :param long_window: Long window period for indicators.
        :param volume_window: Volume window period for volume-related indicators.
        """
        try:
            # fetch data
            raw_df = self._fetch_data_and_get_as_dataframe(stock_id, start_date, end_date)
            # perform advanced analysis
            advanced_analyzed_data = self._advanced_financial_analyzer.apply_advanced_analysis(
                raw_df, short_window, long_window, volume_window)
            # save to redis
            self._data_io_butler.save_data(
                data=advanced_analyzed_data,
                prefix=prefix,
                stock_id=stock_id,
                start_date=start_date,
                end_date=end_date
            )
        except Exception as e:
            error_message = f"An error occurred during advanced financial analysis: {e}"
            logger.exception(error_message)
            raise HTTPException(status_code=500, detail=error_message)

    def calculate_correlation(
            self, stock_ids: list[str], start_date: str, end_date: str, metric: str) -> pd.DataFrame:
        """
        Fetches stock data and calculates the correlation between the assets.

        :param stock_ids: List of stock IDs to calculate correlation.
        :param start_date: Start date for the correlation calculation.
        :param end_date: End date for the correlation calculation.
        :param metric: The metric on which to base the correlation calculation.
        :return: DataFrame with correlation results.
        """
        series_list = []

        for stock_id in stock_ids:
            try:
                stock_data = self._app_instance._data_io_butler.get_data(
                    prefix="stock_data",
                    stock_id=stock_id,
                    start_date=start_date,
                    end_date=end_date
                )
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


def get_stock_analyzer_basic_serving_app():
    return StockAnalyzerBasicServingApp()
