from stockana import calc_time_based
from core.manager.data_manager import DataIOButler, DataNotFoundError


class MAAnalyzer:
    def __init__(self, data_io_butler=None):
        self.data_io_butler = data_io_butler or DataIOButler()

    def calculate_moving_average(self, stock_id: str, start_date: str, end_date: str, window_sizes: list[int]) -> None:
        """
        Extract the data from Redis and calculate the moving average.
        The moving average data will be added as a new column and the current data in Redis will be updated.
        e.g.
        Get the stock data from Redis with the key "AAPL".
        | date | Open | High | Low | Close | Volume |
        Perform the operation of calculating the moving average and append the column MA_{window_size}_days.
        Insert the new dataframe with the MA column back to Redis.
        | date | Open | High | Low | Close | Volume | MA_5_days | MA_10_days | ...

        :param stock_id: Stock ID from yfinance.
        :param window_sizes: A list of integers representing the desired MA days for calculation.
        :return: None
        """

        if not window_sizes:
            print("No window sizes provided for moving average calculation.")
            return

        try:
            # Extract stock data from Redis
            stock_data = self.data_io_butler.get_data(stock_id, start_date, end_date)

            for i in window_sizes:
                stock_data[f"MA_{i}_days"] = calc_time_based.calculate_moving_average(stock_data["Close"], i)

            # # Initialize StockPriceAnalyzer with the fetched stock data
            # analyzer = MovingAverageAnalyzer(stock_data)
            #
            # # Calculate moving averages for all window sizes
            # for window_size in window_sizes:
            #     analyzer.calculating_moving_average(window_size)
            #
            # # Get the updated dataframe
            # updated_stock_data = analyzer.get_analysis_data()

            # Update the Redis data with the new dataframe
            self.data_io_butler.update_data(stock_id, start_date, end_date, stock_data)

        except DataNotFoundError:
            print(f"No data found for stock ID {stock_id} from {start_date} to {end_date} in Redis.")
        except Exception as e:
            # You can provide more specific exceptions above this general one
            # to handle different types of errors differently.
            print(f"An error occurred: {e}")
    # Add any additional analysis methods as needed.


if __name__ == "__main__":
    # Initialize the data manager and moving average analyzer
    data_io_butler = DataIOButler()
    ma_analyzer = MAAnalyzer(data_io_butler)

    # Define some test parameters
    stock_id = "TSM"  # This should be a stock ID that you have stored in Redis
    start_date = "2023-01-01"  # Adjust these dates according to your data
    end_date = "2023-10-10"
    window_sizes = [5, 10, 20]  # Calculate 5-day, 10-day, and 20-day moving averages

    # Calculate moving averages and update Redis
    ma_analyzer.calculate_moving_average(stock_id, start_date, end_date, window_sizes)

    # Fetch the updated data from Redis to verify
    updated_data = data_io_butler.get_data(stock_id, start_date, end_date)
    print(updated_data.head(30))  # Display the first few rows of the updated data


