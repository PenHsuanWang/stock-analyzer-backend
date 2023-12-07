import logging
import pandas as pd
import numpy as np

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AdvancedFinancialAnalyzer:
    """
    Class to combine multiple financial analysis strategies: Moving Average,
    Volume Analysis, Bollinger Bands, MACD, and RSI and Fibonacci Retracement.
    """

    @staticmethod
    def validate_data(stock_data: pd.DataFrame, required_columns: list) -> bool:
        """
        Validate if the required columns are present in the DataFrame.

        :param stock_data: DataFrame to be validated.
        :param required_columns: List of column names that are required.
        :return: True if all required columns are present, False otherwise.
        """
        missing_columns = [col for col in required_columns if col not in stock_data.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        return True

    @staticmethod
    def compute_ema(stock_data: pd.DataFrame, window: int, column: str = 'Close') -> pd.Series:
        """
        Compute Exponential Moving Average (EMA) for a given column.

        EMA is a type of moving average that places a greater weight and significance
        on the most recent data points. It's commonly used to identify the direction
        of a trend or to determine its strength.

        :param stock_data: DataFrame containing stock data.
        :param window: Integer representing the period of the EMA.
        :param column: The column on which EMA is to be computed.
        :return: Series containing the computed EMA values.
        """
        return stock_data[column].ewm(span=window, adjust=False).mean()

    @staticmethod
    def compute_macd(stock_data: pd.DataFrame, short_window: int = 12, long_window: int = 26,
                     signal_window: int = 9) -> pd.DataFrame:
        """
        Compute Moving Average Convergence Divergence (MACD) and Signal Line.

        MACD is a trend-following momentum indicator that shows the relationship between
        two moving averages of a security's price. The MACD is calculated by subtracting
        the 26-period EMA from the 12-period EMA. The result of that calculation is the
        MACD line. A nine-day EMA of the MACD called the "signal line," is then plotted
        on top of the MACD line, which can function as a trigger for buy and sell signals.

        :param stock_data: DataFrame containing stock data.
        :param short_window: Integer representing the short period EMA.
        :param long_window: Integer representing the long period EMA.
        :param signal_window: Integer representing the signal line EMA.
        :return: DataFrame with the MACD and Signal Line added.
        """
        if not AdvancedFinancialAnalyzer.validate_data(stock_data, ['Close']):
            return stock_data

        stock_data['MACD'] = AdvancedFinancialAnalyzer.compute_ema(stock_data,
                                                                   short_window) - AdvancedFinancialAnalyzer.compute_ema(
            stock_data, long_window)
        stock_data['Signal_Line'] = stock_data['MACD'].ewm(span=signal_window, adjust=False).mean()
        return stock_data

    @staticmethod
    def compute_bollinger_bands(stock_data: pd.DataFrame, window: int = 20, num_std: int = 2,
                                column: str = 'Close') -> pd.DataFrame:
        """
        Compute Bollinger Bands.

        Bollinger Bands are a type of statistical chart characterizing the prices and
        volatility over time of a financial instrument or commodity, using a formulaic
        method propounded by John Bollinger in the 1980s. They consist of a middle band
        being an N-period simple moving average (SMA), an upper band at K times an N-period
        standard deviation above the middle band, and a lower band at K times an N-period
        standard deviation below the middle band.

        :param stock_data: DataFrame containing stock data.
        :param window: Integer representing the moving average window size.
        :param num_std: Integer representing the number of standard deviations from the moving average.
        :param column: The column on which Bollinger Bands are to be computed.
        :return: DataFrame with Bollinger Bands (Mid, Upper, Lower) added.
        """
        if not AdvancedFinancialAnalyzer.validate_data(stock_data, [column]):
            return stock_data

        rolling_mean = stock_data[column].rolling(window=window).mean()
        rolling_std = stock_data[column].rolling(window=window).std()
        stock_data['Bollinger_Mid'] = rolling_mean
        stock_data['Bollinger_Upper'] = rolling_mean + (rolling_std * num_std)
        stock_data['Bollinger_Lower'] = rolling_mean - (rolling_std * num_std)
        return stock_data

    @staticmethod
    def compute_rsi(stock_data: pd.DataFrame, window: int = 14, column: str = 'Close') -> pd.DataFrame:
        """
        Compute Relative Strength Index (RSI).

        RSI is a momentum indicator that measures the magnitude of recent price changes
        to evaluate overbought or oversold conditions in the price of a stock or other asset.
        It is displayed as an oscillator (a line graph that moves between two extremes) and
        can have a reading from 0 to 100. The indicator was originally developed by J. Welles
        Wilder Jr. and introduced in his seminal 1978 book, "New Concepts in Technical Trading Systems."

        :param stock_data: DataFrame containing stock data.
        :param window: Integer representing the RSI calculation period.
        :param column: The column on which RSI is to be computed.
        :return: DataFrame with the RSI values added.
        """
        if not AdvancedFinancialAnalyzer.validate_data(stock_data, [column]):
            return stock_data

        delta = stock_data[column].diff()
        gain = (delta.clip(lower=0)).rolling(window=window).mean()
        loss = (-delta.clip(upper=0)).rolling(window=window).mean()
        rs = gain / loss
        stock_data['RSI'] = 100 - (100 / (1 + rs))
        return stock_data

    @staticmethod
    def compute_fibonacci_retracement(stock_data: pd.DataFrame, start_date: str, end_date: str) -> dict:
        """
        Compute Fibonacci Retracement Levels based on maximum high and minimum low in a date range.

        :param stock_data: DataFrame containing stock data.
        :param start_date: String representing the start date of the period.
        :param end_date: String representing the end date of the period.
        :return: Dictionary containing Fibonacci Retracement levels.
        """
        if 'Date' not in stock_data.columns:
            raise ValueError("DataFrame must contain a 'Date' column.")
        if stock_data.index.name != 'Date':
            stock_data = stock_data.set_index('Date')

        relevant_data = stock_data.loc[start_date:end_date]
        if relevant_data.empty:
            raise ValueError("No data found for the given date range.")

        high = relevant_data['High'].max()
        low = relevant_data['Low'].min()
        diff = high - low
        levels = {
            'Level_0': high,
            'Level_23.6%': high - diff * 0.236,
            'Level_38.2%': high - diff * 0.382,
            'Level_50%': high - diff * 0.5,
            'Level_61.8%': high - diff * 0.618,
            'Level_76.4%': high - diff * 0.764,
            'Level_100': low,
        }
        return levels

    @staticmethod
    def apply_strategy(stock_data: pd.DataFrame, short_window: int, long_window: int, volume_window: int,
                       column: str = 'Close') -> pd.DataFrame:
        """
        Apply a combined strategy on stock data incorporating MACD, Bollinger Bands, RSI, and Fibonacci Retracement.

        :param stock_data: DataFrame with stock data.
        :param short_window: Window size for the short-term EMA.
        :param long_window: Window size for the long-term EMA.
        :param volume_window: Window size for volume averaging.
        :param column: The column on which to perform the analyses.
        :return: DataFrame with combined strategy signals.
        """
        if not AdvancedFinancialAnalyzer.validate_data(stock_data, [column, 'Volume']):
            return stock_data

        # Calculate indicators
        stock_data = AdvancedFinancialAnalyzer.compute_macd(stock_data, short_window, long_window)
        stock_data = AdvancedFinancialAnalyzer.compute_bollinger_bands(stock_data, volume_window, column=column)
        stock_data = AdvancedFinancialAnalyzer.compute_rsi(stock_data, column=column)

        # Define signals based on combined indicators
        stock_data['Buy_Signal'] = ((stock_data['MACD'] > stock_data['Signal_Line']) &
                                    (stock_data['Close'] > stock_data['Bollinger_Lower']) &
                                    (stock_data['RSI'] < 70) &
                                    (stock_data['Volume'] > stock_data['Volume'].rolling(window=volume_window).mean()))

        stock_data['Sell_Signal'] = ((stock_data['MACD'] < stock_data['Signal_Line']) &
                                     (stock_data['Close'] < stock_data['Bollinger_Upper']) &
                                     (stock_data['RSI'] > 30))

        return stock_data

# Example usage:
# aapl_data = pd.read_csv('path_to_your_data.csv')
# analyzer = AdvancedFinancialAnalyzer()
# analyzed_data = analyzer.apply_strategy(aapl_data, short_window=12, long_window=26, volume_window=20)
# print(analyzed_data.tail())
