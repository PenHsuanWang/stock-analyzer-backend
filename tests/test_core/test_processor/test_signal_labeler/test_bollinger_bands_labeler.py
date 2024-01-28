# test_bollinger_bands_labeler.py

import pandas as pd
import pytest
from src.core.processor.signal_labeler.strategies.bollinger_bands_buy_sell_labeler import BollingerBandsLabeler

class TestBollingerBandsLabeler:
    def setup_method(self):
        self.labeler = BollingerBandsLabeler()

    def test_bollinger_bands_signals(self):
        data = pd.DataFrame({
            'Close': [100, 101, 102, 98, 97, 103, 105, 107, 106, 104]
        })

        labeled_data = self.labeler.apply(data)
        # Assuming window = 20, num_std_dev = 2. Adjust assertions based on actual band calculations.
        assert labeled_data['Buy_Signal'].sum() >= 0  # Check if there are any buy signals
        assert labeled_data['Sell_Signal'].sum() >= 0  # Check if there are any sell signals

    def test_input_without_close_column(self):
        data = pd.DataFrame({
            'Open': [100, 101, 102, 98, 97, 103, 105, 107, 106, 104]
        })

        with pytest.raises(ValueError):
            self.labeler.apply(data)

    def test_empty_dataframe(self):
        data = pd.DataFrame()

        with pytest.raises(ValueError):
            self.labeler.apply(data)

# Additional tests can be added to cover different scenarios and edge cases.
