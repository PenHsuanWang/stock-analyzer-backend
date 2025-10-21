# bollinger_bands_labeler.py

import pandas as pd
import numpy as np
from core.processor.signal_labeler.base_strategy_labeler import BaseStrategyLabeler

class BollingerBandsLabeler(BaseStrategyLabeler):
    """
    Concrete implementation of BaseStrategyLabeler for labeling buy and sell signals
    based on Bollinger Bands.
    """

    def __init__(self, window: int = 20, num_std_dev: int = 2):
        """
        Initialize the BollingerBandsLabeler with configurable parameters.

        Parameters:
        window (int): The moving window size for the middle band (SMA).
        num_std_dev (int): The number of standard deviations for the upper and lower bands.
        """
        self.window = window
        self.num_std_dev = num_std_dev

    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply Bollinger Bands for buy and sell signal labeling.

        Parameters:
        data (pd.DataFrame): The input DataFrame containing 'Close' price column.

        Returns:
        pd.DataFrame: The original DataFrame augmented with 'Buy_Signal' and 'Sell_Signal' columns.
        """
        if 'Close' not in data.columns:
            raise ValueError("Input DataFrame must contain 'Close' column for Bollinger Bands calculation.")

        data['Middle_Band'] = data['Close'].rolling(window=self.window).mean()
        data['Std_Dev'] = data['Close'].rolling(window=self.window).std()
        data['Upper_Band'] = data['Middle_Band'] + (data['Std_Dev'] * self.num_std_dev)
        data['Lower_Band'] = data['Middle_Band'] - (data['Std_Dev'] * self.num_std_dev)

        data['Buy_Signal'] = (data['Close'] < data['Lower_Band'])
        data['Sell_Signal'] = (data['Close'] > data['Upper_Band'])

        return data.drop(['Std_Dev'], axis=1)

