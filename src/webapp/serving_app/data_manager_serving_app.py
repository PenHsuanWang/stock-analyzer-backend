# webapp.data_manager_serving_app.py

import threading

import pandas as pd

from src.core.manager.data_manager import DataIOButler
from src.utils.database_adapters.redis_adapter import RedisAdapter


class DataManagerApp:
    _app = None
    _app_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._app_lock:
            if cls._app is None:
                cls._app = super().__new__(cls)
                cls._app._data_io_butler = DataIOButler(adapter=RedisAdapter())  # Initialize the DataIOButler here
            return cls._app

    @staticmethod
    def get_all_data_keys(prefix: str) -> list:
        return [key for key in DataManagerApp()._data_io_butler.get_all_exist_data_key(prefix=prefix)]

    @staticmethod
    def get_stock_data(prefix: str, stock_id: str, start_date: str, end_date: str) -> pd.DataFrame:
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
        return DataManagerApp()._data_io_butler.delete_data(
            prefix=prefix,
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date
        )


def get_app():
    app = DataManagerApp()
    return app
