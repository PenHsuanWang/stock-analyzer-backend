import threading

import pandas as pd
import redis
from stockana.data_io.data_fetcher import YFinanceFetcher


class StockDataFetcherApp:

    _app = None
    _app_lock = threading.Lock

    _is_initialized = None

    def __new__(cls, *args, **kwargs):
        with cls._app_lock:
            if cls._app is None:
                cls._app = super(StockDataFetcherApp).__new__(cls)
                cls._app._is_initialized = False
            return cls._app

    def __init__(self):
        if not self._is_initialized:
            self._redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)  # adjust as necessary
            self._data_fetcher = YFinanceFetcher()

    def fetch_data_and_get_as_dataframe(self, stock_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        provide stock id and time range, calling the data fetcher to extract stock price data via yfinance api
        :param stock_id:
        :param start_date:
        :param end_date:
        :return:
        """
        try:
            self._data_fetcher.fetch_from_source(stock_id, start_date, end_date)
        except Exception as e:
            print(f"error happen when fetching data. please check the input stock_id and time range. Full stack error: {e}")
            raise RuntimeError

        df = self._data_fetcher.get_as_dataframe()

        return df

    def fetch_data_and_stash(self, stock_id: str, start_date: str, end_date: str) -> None:
        """
        the purpose of analysis stock price EDA. the fetch raw data need to be stashed and wait for
        following analysis operation. Put the data into redis storage place
        :param stock_id:
        :param start_date:
        :param end_date:
        :return:
        """
        df = self.fetch_data_and_get_as_dataframe(stock_id, start_date, end_date)
        key = f"stock_data:{stock_id}:{start_date}:{end_date}"

        # Convert DataFrame to JSON and store it in Redis
        self._redis_client.set(key, df.to_json(orient="records"))

def get_app():
    app = StockDataFetcherApp()
    return app

