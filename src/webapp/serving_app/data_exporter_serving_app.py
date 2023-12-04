import threading
import pandas as pd
from abc import ABC, abstractmethod

from src.core.manager.data_manager import DataIOButler
from src.utils.database_adapters.base import AbstractDatabaseAdapter
from src.utils.database_adapters.redis_adapter import RedisAdapter
from src.utils.data_outbound.csv_exporter import CSVExporter
from src.utils.data_outbound.http_data_sender import HTTPDataSender


class DataFetchStrategy:
    def __init__(self, adapter: AbstractDatabaseAdapter):
        self.data_io_butler = DataIOButler(adapter)

    @abstractmethod
    def fetch_data(self, key: str):
        pass


class SingleStockDataFetchStrategy(DataFetchStrategy):
    def fetch_data(self, key: str) -> pd.DataFrame:
        # decompose the key to extract the parameters
        _, stock_id, start_date, end_date = key.split(':')
        return self.data_io_butler.get_data(
            prefix='stock_data',
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date
        )


class GroupStockDataFetchStrategy(DataFetchStrategy):
    def fetch_data(self, key: str) -> dict:
        # decompose the key to extract the parameters
        _, group_id, start_date, end_date = key.split(':')
        return self.data_io_butler.get_dataframes_group(
            group_id=group_id,
            start_date=start_date,
            end_date=end_date
        )


class DataExporterApp:
    _app = None
    _app_lock = threading.Lock()
    _fetch_strategies = {
        "stock_data:": SingleStockDataFetchStrategy(RedisAdapter()),
        "group_stock_data:": GroupStockDataFetchStrategy(RedisAdapter()),
    }

    def __new__(cls, *args, **kwargs):
        with cls._app_lock:
            if cls._app is None:
                cls._app = super().__new__(cls)
            return cls._app

    def export_data(self, key: str, export_type: str, *args, **kwargs) -> None:
        """
        Fetch data based on the key prefix and export or send it using the specified type.

        :param key: Key to identify the data or data group in Redis.
        :param export_type: Type of export ('csv' or 'http').
        :param args: Additional arguments for the export type.
        :param kwargs: Additional keyword arguments for the export type.
        """
        strategy = None
        for prefix, fetch_strategy in self._fetch_strategies.items():
            if key.startswith(prefix):
                strategy = fetch_strategy
                break
        if strategy is None:
            raise ValueError("Invalid key format or unsupported key type.")

        data = strategy.fetch_data(key)

        if export_type == 'csv':
            CSVExporter().export_data(data, *args, **kwargs)
        elif export_type == 'http':
            HTTPDataSender().export_data(data, *args, **kwargs)
        else:
            raise ValueError("Unsupported export type: {export_type}")


def get_app():
    return DataExporterApp()