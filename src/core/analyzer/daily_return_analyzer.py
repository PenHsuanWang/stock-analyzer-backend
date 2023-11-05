import logging
import threading
import pandas as pd

from stockana import calc_time_based

# Initialize logging
logger = logging.getLogger(__name__)


class DailyReturnAnalyzer:
    def __init__(self):
        self.redis_lock = threading.Lock()  # Lock for Redis operations

    @staticmethod
    def calculate_daily_return(stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the daily return and add as a new column to the DataFrame.

        :param stock_data: DataFrame with stock data.
        :return: DataFrame with a new 'Daily_Return' column.
        """
        if stock_data.empty:
            stock_data['Daily_Return'] = pd.Series()  # or pd.NA or 0 based on the logic you want
        else:
            stock_data['Daily_Return'] = calc_time_based.calculate_daily_return(stock_data['Close'])
        return stock_data
