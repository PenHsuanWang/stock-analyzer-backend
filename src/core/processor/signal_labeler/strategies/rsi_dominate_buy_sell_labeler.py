# rsi_dominate_buy_sell_labeler.py

import pandas as pd
from src.core.processor.signal_labeler.base_strategy_labeler import BaseStrategyLabeler


class BuySellSignalLabeler(BaseStrategyLabeler):
    """
    Concrete implementation of BaseStrategyLabeler for labeling buy and sell signals.

    This class allows configuration of RSI thresholds and column names for MACD, Signal Line, and RSI,
    making it adaptable for different datasets or analysis strategies.
    """

    def __init__(self, rsi_buy_threshold: float = 30.0, rsi_sell_threshold: float = 70.0,
                 macd_column: str = 'MACD', signal_line_column: str = 'Signal_Line',
                 rsi_column: str = 'RSI'):
        """
        Initialize the BuySellSignalLabeler with configurable parameters.

        Parameters:
        rsi_buy_threshold (float): The RSI threshold for triggering a buy signal.
        rsi_sell_threshold (float): The RSI threshold for triggering a sell signal.
        macd_column (str): The column name for MACD values.
        signal_line_column (str): The column name for Signal Line values.
        rsi_column (str): The column name for RSI values.
        """
        self.rsi_buy_threshold = rsi_buy_threshold
        self.rsi_sell_threshold = rsi_sell_threshold
        self.macd_column = macd_column
        self.signal_line_column = signal_line_column
        self.rsi_column = rsi_column

    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply buy and sell signal labeling based on MACD and RSI.

        This method labels each row in the DataFrame with a buy or sell signal based on the
        MACD and RSI values. The input DataFrame is expected to contain 'MACD', 'Signal_Line',
        and 'RSI' columns. It appends two new boolean columns to the DataFrame - 'Buy_Signal'
        and 'Sell_Signal', indicating the presence of buy and sell signals respectively.

        Parameters:
        data (pd.DataFrame): The input DataFrame containing the MACD, Signal_Line, and RSI columns.

        Returns:
        pd.DataFrame: The original DataFrame augmented with 'Buy_Signal' and 'Sell_Signal' columns.

        Raises:
        ValueError: If required columns ('MACD', 'Signal_Line', 'RSI') are not present in the DataFrame.
        """
        self._validate_input(data)

        buy_signals, sell_signals = [], []

        for i in range(len(data)):
            if data[self.macd_column][i] > data[self.signal_line_column][i] and data[self.rsi_column][i] < self.rsi_buy_threshold:
                buy_signals.append(True)
                sell_signals.append(False)
            elif data[self.macd_column][i] < data[self.signal_line_column][i] and data[self.rsi_column][i] > self.rsi_sell_threshold:
                sell_signals.append(True)
                buy_signals.append(False)
            else:
                buy_signals.append(False)
                sell_signals.append(False)

        data['Buy_Signal'] = buy_signals
        data['Sell_Signal'] = sell_signals

        return data

    def _validate_input(self, data: pd.DataFrame):
        """
        Validate if the input DataFrame contains the necessary columns for analysis.

        This internal method checks if the DataFrame includes 'MACD', 'Signal_Line', and 'RSI' columns.
        It raises a ValueError if any of these columns are missing.

        Parameters:
        data (pd.DataFrame): The input DataFrame to validate.

        Raises:
        ValueError: If the DataFrame does not contain the required columns.
        """
        required_columns = {'MACD', 'Signal_Line', 'RSI'}
        if not required_columns.issubset(data.columns):
            raise ValueError(f"Input DataFrame must contain the following columns: {required_columns}")


if __name__ == "__main__":
    # Sample data for demonstration
    data = {
        'MACD': [1.5, -0.5, 0.2, -1.0, 1.1, -0.3],
        'Signal_Line': [1.0, -0.4, 0.1, -0.8, 0.9, -0.2],
        'RSI': [25, 55, 20, 75, 30, 80]
    }

    # Creating a DataFrame from the sample data
    df = pd.DataFrame(data)

    # Creating an instance of BuySellSignalLabeler
    labeler = BuySellSignalLabeler()

    # Applying the BuySellSignalLabeler
    labeled_data = labeler.apply(df)

    # Displaying the original data with buy and sell signals
    print("Original Data with Buy and Sell Signals:")
    print(labeled_data)

