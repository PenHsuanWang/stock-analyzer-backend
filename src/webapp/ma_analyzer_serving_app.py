import threading
from core.manager.data_manager import DataIOButler, DataNotFoundError
from core.analyzer.moving_average_analyzer import MovingAverageAnalyzer


class MovingAverageAnalyzerApp:
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
    def compute_and_store_moving_average(stock_id: str, start_date: str, end_date: str,
                                         window_sizes: list[int]) -> None:
        """
        Computes the moving averages and updates the Redis store.

        :param stock_id: ID of the stock.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :param window_sizes: List of window sizes for moving average calculation.
        :return: None
        """

        ma_analyzer = MovingAverageAnalyzer()
        ma_analyzer.calculate_moving_average(
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date,
            window_sizes=window_sizes
        )


def get_app():
    app = MovingAverageAnalyzerApp()
    return app
