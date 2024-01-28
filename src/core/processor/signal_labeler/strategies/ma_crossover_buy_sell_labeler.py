# moving_average_crossover_labeler.py

import pandas as pd
from src.core.processor.signal_labeler.base_strategy_labeler import BaseStrategyLabeler

class MovingAverageCrossoverLabeler(BaseStrategyLabeler):
    """
    Concrete implementation of BaseStrategyLabeler for labeling buy and sell signals
    based on moving average crossovers.
    """

    def __init__(self, short_window: int = 12, long_window: int = 26):
        """
        Initialize the MovingAverageCrossoverLabeler with configurable parameters.

        Parameters:
        short_window (int): The window size for the short-term moving average.
        long_window (int): The window size for the long-term moving average.
        """
        self.short_window = short_window
        self.long_window = long_window

    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply moving average crossovers for buy and sell signal labeling.

        Parameters:
        data (pd.DataFrame): The input DataFrame containing 'Close' price column.

        Returns:
        pd.DataFrame: The original DataFrame augmented with 'Buy_Signal' and 'Sell_Signal' columns.
        """
        if 'Close' not in data.columns:
            raise ValueError("Input DataFrame must contain 'Close' column for moving average calculation.")

        data['Short_MA'] = data['Close'].rolling(window=self.short_window).mean()
        data['Long_MA'] = data['Close'].rolling(window=self.long_window).mean()

        data['Buy_Signal'] = data['Short_MA'] > data['Long_MA']
        data['Sell_Signal'] = data['Short_MA'] < data['Long_MA']

        return data

