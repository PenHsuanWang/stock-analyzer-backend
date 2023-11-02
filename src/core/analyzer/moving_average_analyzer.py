import logging
import threading
import pandas as pd


from stockana import calc_time_based


# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MovingAverageAnalyzer:

    def __init__(self):
        self.redis_lock = threading.Lock()  # Lock for Redis operations

    @staticmethod
    def calculate_moving_average(stock_data: pd.DataFrame, window_sizes: list[int]) -> pd.DataFrame:
        """
        Calculate the moving average and add as new columns to the DataFrame.

        :param stock_data: DataFrame with stock data.
        :param window_sizes: List of integers representing window sizes for MA calculation.
        :return: DataFrame with new MA columns.
        """

        if not window_sizes:
            logger.error("No window sizes provided for moving average calculation.")
            return stock_data

        for window_size in window_sizes:
            ma_column_name = f"MA_{window_size}_days"
            stock_data[ma_column_name] = calc_time_based.calculate_moving_average(stock_data["Close"], window_size)
        return stock_data

