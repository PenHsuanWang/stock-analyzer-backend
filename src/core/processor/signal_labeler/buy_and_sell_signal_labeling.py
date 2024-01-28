# buy_and_sell_signal_labeling.py

import pandas as pd
from src.core.processor.signal_labeler.base_strategy_labeler import BaseStrategyLabeler


class BuySellSignalLabeler(BaseStrategyLabeler):
    """
    Concrete implementation of BaseStrategyLabeler for labeling buy and sell signals.

    This class applies a specific strategy to label buy and sell signals in a stock dataset.
    The strategy uses Moving Average Convergence Divergence (MACD) and Relative Strength Index (RSI)
    to determine potential buying and selling points. A buy signal is generated when the MACD line
    crosses above the Signal Line and the RSI is below 30, indicating an oversold condition.
    Conversely, a sell signal is generated when the MACD line crosses below the Signal Line and
    the RSI is above 70, indicating an overbought condition.

    Attributes:
        None

    Methods:
        apply(data: pd.DataFrame) -> pd.DataFrame:
            Applies the buy and sell signal labeling strategy to the provided DataFrame.
        _validate_input(data: pd.DataFrame):
            Validates if the input DataFrame contains the necessary columns for the analysis.
    """

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
            if data['MACD'][i] > data['Signal_Line'][i] and data['RSI'][i] < 30:
                buy_signals.append(True)
                sell_signals.append(False)
            elif data['MACD'][i] < data['Signal_Line'][i] and data['RSI'][i] > 70:
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

