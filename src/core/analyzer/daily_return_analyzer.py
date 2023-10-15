import logging
import threading
from stockana import calc_time_based
from core.manager.data_manager import DataIOButler, DataNotFoundError

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DailyReturnAnalyzer:
    def __init__(self):
        self.data_io_butler = DataIOButler()
        self.redis_lock = threading.Lock()  # Lock for Redis operations

    def calculate_daily_return(self, stock_id: str, start_date: str, end_date: str) -> None:
        """
        Extract the data from Redis and calculate the daily return.
        The daily return data will be added as a new column and the current data in Redis will be updated.
        e.g.
        Get the stock data from Redis with the key "AAPL".
        | date | Open | High | Low | Close | Volume |
        Perform the operation of calculating the daily return and append the column Daily_Return.
        Insert the new dataframe with the Daily_Return column back to Redis.
        | date | Open | High | Low | Close | Volume | Daily_Return |

        :param stock_id: Stock ID from yfinance.
        :return: None
        """

        try:
            # Extract stock data from Redis
            stock_data = self.data_io_butler.get_data(stock_id, start_date, end_date)

            stock_data['Daily_Return'] = calc_time_based.calculate_daily_return(stock_data['Close'])

            # Update the Redis data with the new dataframe
            with self.redis_lock:  # Ensure thread safety for Redis operations
                self.data_io_butler.update_data(stock_id, start_date, end_date, stock_data)

        except DataNotFoundError:
            logger.error(f"No data found for stock ID {stock_id} from {start_date} to {end_date} in Redis.")
            raise
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
