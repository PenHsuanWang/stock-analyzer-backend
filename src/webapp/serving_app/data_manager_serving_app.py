# webapp.data_manager_serving_app.py
import os
import threading

import pandas as pd

from src.core.manager.data_manager import DataIOButler
from src.utils.database_adapters.redis_adapter import RedisAdapter


class AdapterFactory:
    @staticmethod
    def create_adapter(adapter_type, **kwargs):
        if adapter_type == "RedisAdapter":
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', 6379)
            db = kwargs.get('db', 0)
            return RedisAdapter(
                host=host,
                port=port,
                db=db
            )
        else:
            raise ValueError(f"Unsupported adapter type: {adapter_type}")


class DataManagerApp:
    _app = None
    _app_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        try:
            data_io_butler = kwargs["data_io_butler"]
            if data_io_butler is None:
                data_io_butler = DataIOButler(adapter=RedisAdapter())
        except KeyError:
            data_io_butler = DataIOButler(adapter=RedisAdapter())
        with cls._app_lock:
            if cls._app is None:
                cls._app = super().__new__(cls)
                # cls._app._data_io_butler = DataIOButler(adapter=RedisAdapter())  # Initialize the DataIOButler here
                cls._app._data_io_butler = data_io_butler
            return cls._app

    @staticmethod
    def get_all_data_keys(prefix: str) -> list:
        return [key for key in DataManagerApp()._data_io_butler.get_all_exist_data_key(prefix=prefix)]

    @staticmethod
    def get_stock_data(prefix: str, stock_id: str, start_date: str, end_date: str) -> pd.DataFrame:

        # Check for invalid or empty input
        if not all([prefix, stock_id, start_date, end_date]):
            return pd.DataFrame()

        return DataManagerApp()._data_io_butler.get_data(
            prefix=prefix,
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date
        )

    @staticmethod
    def check_data(prefix: str, stock_id: str, start_date: str, end_date: str) -> bool:
        return DataManagerApp()._data_io_butler.check_data_exists(
            prefix=prefix,
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date
        )

    @staticmethod
    def update_stock_data(prefix: str, stock_id: str, start_date: str, end_date: str, updated_dataframe: pd.DataFrame) -> bool:

        # Check for invalid or empty input
        if not all([prefix, stock_id, start_date, end_date]) or updated_dataframe.empty:
            return False

        try:
            DataManagerApp()._data_io_butler.update_data(
                prefix=prefix,
                stock_id=stock_id,
                start_date=start_date, end_date=end_date,
                updated_dataframe=updated_dataframe
            )
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def delete_stock_data(prefix: str, stock_id: str, start_date: str, end_date: str) -> bool:

        # Check for invalid or empty input
        if not all([prefix, stock_id, start_date, end_date]):
            return False

        return DataManagerApp()._data_io_butler.delete_data(
            prefix=prefix,
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date
        )

    @staticmethod
    def save_dataframes_group(group_id: str, start_date: str, end_date: str, group_df_list: list) -> bool:
        try:
            DataManagerApp()._data_io_butler.save_dataframes_group(
                group_id=group_id,
                start_date=start_date,
                end_date=end_date,
                group_df_list=group_df_list
            )
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def get_dataframes_group(group_id: str, start_date: str, end_date: str) -> dict:
        try:
            return DataManagerApp()._data_io_butler.get_dataframes_group(
                group_id=group_id,
                start_date=start_date,
                end_date=end_date
            )
        except Exception as e:
            print(e)
            return {}

    @staticmethod
    def delete_dataframes_group(group_id: str, start_date: str, end_date: str) -> bool:
        try:
            return DataManagerApp()._data_io_butler.delete_dataframes_group(
                group_id=group_id,
                start_date=start_date,
                end_date=end_date
            )
        except Exception as e:
            print(e)
            return False


def get_app(data_io_butler=None):
    if data_io_butler is None:
        adapter_type = os.getenv('ADAPTER_TYPE', 'RedisAdapter')
        adapter_kwargs = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '6379')),
            'db': int(os.getenv('DB_DB', '0')),
        }
        data_io_butler = DataIOButler(adapter=AdapterFactory.create_adapter(adapter_type, **adapter_kwargs))
    app = DataManagerApp(data_io_butler=data_io_butler)
    return app
