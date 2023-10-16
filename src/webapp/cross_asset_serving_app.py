import threading
import pandas as pd
from core.manager.data_manager import DataIOButler
from core.analyzer.cross_asset_analyzer import CrossAssetAnalyzer


class CrossAssetApp:
    _app = None
    _app_lock = threading.Lock()
    _is_initialized = None

    def __new__(cls, *args, **kwargs):
        with cls._app_lock:
            if cls._app is None:
                cls._app = super().__new__(cls)
                cls._app._is_initialized = False
            return cls._app

    def __init__(self):
        if not self._is_initialized:
            self._data_io_butler = DataIOButler()

    @staticmethod
    def compute_assets_correlation(stock_ids: list[str], start_date: str, end_date: str, metric: str) -> pd.DataFrame:
        """
        Computes the correlation among different assets based on the provided metric and returns the result.

        :param stock_ids: List of stock IDs.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :param metric: The column based on which the correlation should be calculated.
        :return: DataFrame of correlations
        """

        cross_asset_analyzer = CrossAssetAnalyzer()
        correlation_df = cross_asset_analyzer.calculate_correlation(stock_ids, start_date, end_date, metric)
        return correlation_df


def get_app():
    app = CrossAssetApp()
    return app
