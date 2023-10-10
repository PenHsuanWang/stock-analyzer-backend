from stockana.analyzer.stock_analyzer import StockPriceAnalyzer
from core.manager.data_manager import DataIOButler


class MovingAverageAnalyzer:
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

        # Extract stock data from Redis
        stock_data = self.data_io_butler.get_data(stock_id, start_date, end_date)

        # If there's no stock data for the given ID, exit the function
        if stock_data is None:
            return

        # Initialize StockPriceAnalyzer with the fetched stock data
        analyzer = StockPriceAnalyzer(stock_data)

        # Calculate moving averages for all window sizes
        for window_size in window_sizes:
            analyzer.calculating_moving_average(window_size)

        # Get the updated dataframe
        updated_stock_data = analyzer.get_analysis_data()

        # Update the Redis data with the new dataframe
        self.data_io_butler.update_data(stock_id, start_date, end_date, updated_stock_data)

    # Add any additional analysis methods as needed.
