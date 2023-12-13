import threading
import pandas as pd
from abc import ABC, abstractmethod

from src.core.manager.data_manager import DataIOButler
from src.utils.database_adapters.base import AbstractDatabaseAdapter
from src.utils.database_adapters.redis_adapter import RedisAdapter
from src.utils.data_outbound.csv_exporter import CSVExporter
from src.utils.data_outbound.http_data_sender import HTTPDataSender


class DataGetStrategy:
    def __init__(self, adapter: AbstractDatabaseAdapter):
        self.data_io_butler = DataIOButler(adapter)

    @abstractmethod
    def get_data_from_db(self, key: str):
        pass


class SingleStockDataGetStrategy(DataGetStrategy):
    def get_data_from_db(self, key: str) -> pd.DataFrame:
        # decompose the key to extract the parameters
        _, stock_id, start_date, end_date = key.split(':')
        return self.data_io_butler.get_data(
            prefix='stock_data',
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date
        )


class GroupStockDataGetStrategy(DataGetStrategy):
    def get_data_from_db(self, key: str) -> dict:
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
    _get_data_strategies = {
        "stock_data:": SingleStockDataGetStrategy(RedisAdapter()),
        "group_stock_data:": GroupStockDataGetStrategy(RedisAdapter()),
    }

    def __new__(cls, *args, **kwargs):
        with cls._app_lock:
            if cls._app is None:
                cls._app = super().__new__(cls)
            return cls._app

    def export_data(self, key: str, export_type: str, *args, **kwargs):
        """
        get data from internal database based on the key prefix and export or send it using the specified type.

        :param key: Key to identify the data or data group in Redis.
        :param export_type: Type of export ('csv' or 'http').
        :param args: Additional arguments for the export type.
        :param kwargs: Additional keyword arguments for the export type.
        """
        strategy = None
        for prefix, get_data_strategy in self._get_data_strategies.items():
            if key.startswith(prefix):
                strategy = get_data_strategy
                break
        if strategy is None:
            raise ValueError("Invalid key format or unsupported key type.")

        data = strategy.get_data_from_db(key)

        if export_type == 'csv':
            CSVExporter().export_data(data, *args, **kwargs)
            return {"message": "Data exported to CSV successfully."}
        elif export_type == 'http':
            # Return the response object directly from the HTTPDataSender
            return HTTPDataSender().export_data(data, *args, **kwargs)
        else:
            raise ValueError(f"Unsupported export type: {export_type}")


def get_app():
    return DataExporterApp()
