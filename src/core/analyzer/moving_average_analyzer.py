import logging
import threading
import redis.exceptions


from stockana import calc_time_based
from core.manager.data_manager import DataIOButler, DataNotFoundError


# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MovingAverageAnalyzer:

    def __init__(self):
        self.data_io_butler = DataIOButler()
        self.redis_lock = threading.Lock()  # Lock for Redis operations

    def calculate_moving_average(self, prefix: str, stock_id: str, start_date: str, end_date: str, window_sizes: list[int]) -> None:
        """
        Extract the data from Redis and calculate the moving average.
        The moving average data will be added as a new column and the current data in Redis will be updated.
        e.g.
        Get the stock data from Redis with the key "AAPL".
        | date | Open | High | Low | Close | Volume |
        Perform the operation of calculating the moving average and append the column MA_{window_size}_days.
        Insert the new dataframe with the MA column back to Redis.
        | date | Open | High | Low | Close | Volume | MA_5_days | MA_10_days | ...

        :param prefix:
        :param stock_id: Stock ID from yfinance.
        :param window_sizes: A list of integers representing the desired MA days for calculation.
        :return: None
        """

        if not window_sizes:
            logger.warning("No window sizes provided for moving average calculation.")
            return

        try:
            # Extract stock data from Redis
            stock_data = self.data_io_butler.get_data(prefix, stock_id, start_date, end_date)

            for i in window_sizes:
                stock_data[f"MA_{i}_days"] = calc_time_based.calculate_moving_average(stock_data["Close"], i)

            # if this stock dataset is not calculated before, save with new key
            self.data_io_butler.save_data(
                "analyzed_stock_data",
                stock_id,
                start_date,
                end_date,
                data=stock_data
            )

            # Update the Redis data with the new dataframe
            with self.redis_lock:  # Ensure thread safety for Redis operations
                self.data_io_butler.update_data(
                    "analyzed_stock_data",
                    stock_id,
                    start_date,
                    end_date,
                    stock_data
                )

        except DataNotFoundError as de:
            print(de)
            logger.error(f"No data found for stock ID {stock_id} from {start_date} to {end_date} in Redis.")
        except redis.exceptions.RedisError as re:
            logger.error(f"Redis error occurred: {re}")
        except (ValueError, TypeError) as e:
            logger.error(f"Data processing error: {e}")
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            raise



if __name__ == "__main__":
    # Initialize the data manager and moving average analyzer
    ma_analyzer = MovingAverageAnalyzer()

    # Define some test parameters
    stock_id = "TSM"  # This should be a stock ID that you have stored in Redis
    start_date = "2023-01-01"  # Adjust these dates according to your data
    end_date = "2023-10-10"
    window_sizes = [5, 10, 20]  # Calculate 5-day, 10-day, and 20-day moving averages

    # Calculate moving averages and update Redis
    ma_analyzer.calculate_moving_average(stock_id, start_date, end_date, window_sizes)

    # Fetch the updated data from Redis to verify
    data_io_butler = DataIOButler()
    updated_data = data_io_butler.get_data(stock_id, start_date, end_date)
    print(updated_data.head(30))  # Display the first few rows of the updated data


