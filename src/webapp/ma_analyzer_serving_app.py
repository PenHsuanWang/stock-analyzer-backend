import threading
from core.manager.data_manager import DataIOButler, DataNotFoundError
from stockana.analyzer.moving_average_analyzer import MovingAverageAnalyzer


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

    def compute_and_store_moving_average(self, stock_id: str, start_date: str, end_date: str,
                                         window_sizes: list[int]) -> None:
        """
        Computes the moving averages and updates the Redis store.

        :param stock_id: ID of the stock.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :param window_sizes: List of window sizes for moving average calculation.
        :return: None
        """
        # Fetch stock data from Redis
        try:
            stock_data = self._data_io_butler.get_data(stock_id, start_date, end_date)
        except DataNotFoundError:
            print(f"No data found for stock: {stock_id} between {start_date} and {end_date}")
            return

        # Create a MovingAverageAnalyzer with the fetched data
        ma_analyzer = MovingAverageAnalyzer(stock_data)

        # Calculate moving averages for the data
        for window_size in window_sizes:
            ma_analyzer.calculating_moving_average(window_size)

        # Get the updated DataFrame after calculation
        updated_stock_data = ma_analyzer.get_analysis_data()

        # Store the updated data back to Redis
        self._data_io_butler.update_data(stock_id, start_date, end_date, updated_stock_data)


def get_app():
    app = MovingAverageAnalyzerApp()
    return app
