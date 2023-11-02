import logging
import threading
import redis.exceptions
from stockana import calc_time_based
from core.manager.data_manager import DataIOButler, DataNotFoundError

# Initialize logging
logger = logging.getLogger(__name__)


class DailyReturnAnalyzer:
    def __init__(self):
        self.data_io_butler = DataIOButler()
        self.redis_lock = threading.Lock()  # Lock for Redis operations

    def calculate_daily_return(self, prefix: str, stock_id: str, start_date: str, end_date: str) -> None:
        """
        Extract the data from Redis with the specified prefix and calculate the daily return.
        The daily return data will be added as a new column and the updated data will be saved back to Redis.

        :param prefix: Prefix for the Redis key where the stock data is stored.
        :param stock_id: Stock ID from yfinance.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :return: None
        """

        # Use a consistent key prefix for both fetching and updating data
        fetch_prefix = prefix if prefix != "analyzed_stock_data" else "raw_stock_data"

        try:
            # Extract stock data from Redis
            stock_data = self.data_io_butler.get_data(fetch_prefix, stock_id, start_date, end_date)

            # Perform the daily return calculation
            stock_data['Daily_Return'] = calc_time_based.calculate_daily_return(stock_data['Close'])

            # Update the Redis data with the new dataframe
            with self.redis_lock:  # Ensure thread safety for Redis operations
                self.data_io_butler.save_data(
                    "analyzed_stock_data",
                    stock_id,
                    start_date,
                    end_date,
                    data=stock_data
                )

        except DataNotFoundError as de:
            logger.error(f"No data found for stock ID {stock_id} from {start_date} to {end_date} in Redis: {de}")
            raise
        except redis.exceptions.RedisError as re:
            logger.error(f"Redis error occurred: {re}")
            raise
        except Exception as e:
            logger.exception(f"An unexpected error occurred while calculating daily returns: {e}")
            raise
