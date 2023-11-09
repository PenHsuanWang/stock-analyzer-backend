# src/webapp/cross_asset_serving_app.py

import threading
import pandas as pd
from core.analyzer.cross_asset_analyzer import CrossAssetAnalyzer
from core.manager.data_manager import DataIOButler, DataNotFoundError


class CrossAssetApp:
    _app_instance = None
    _app_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._app_lock:
            if cls._app_instance is None:
                cls._app_instance = super().__new__(cls)
            return cls._app_instance

    @staticmethod
    def compute_assets_correlation(stock_ids: list[str], start_date: str, end_date: str, metric: str) -> pd.DataFrame:
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


def get_app():
    return CrossAssetApp()
