# webapp.data_manager_serving_app.py

import threading
from core.manager.data_manager import DataIOButler


class DataManagerApp:
    _app = None
    _app_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._app_lock:
            if cls._app is None:
                cls._app = super().__new__(cls)
                cls._app._data_io_butler = DataIOButler()  # Initialize the DataIOButler here
            return cls._app

    @staticmethod
    def get_stock_data(stock_id: str, start_date: str, end_date: str):
        return DataManagerApp()._data_io_butler.get_data(stock_id, start_date, end_date)

    @staticmethod
    def check_data(stock_id: str, start_date: str, end_date: str) -> bool:
        return DataManagerApp()._data_io_butler.check_data_exists(stock_id, start_date, end_date)

    @staticmethod
    def update_stock_data(stock_id: str, start_date: str, end_date: str, updated_dataframe):
        DataManagerApp()._data_io_butler.update_data(stock_id, start_date, end_date, updated_dataframe)

    @staticmethod
    def delete_stock_data(stock_id: str, start_date: str, end_date: str) -> bool:
        return DataManagerApp()._data_io_butler.delete_data(stock_id, start_date, end_date)


def get_app():
    app = DataManagerApp()
    return app
