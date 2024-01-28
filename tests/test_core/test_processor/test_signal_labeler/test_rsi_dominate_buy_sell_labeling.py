# test_rsi_dominate_labeler.py

import pandas as pd
import pytest
from src.core.processor.signal_labeler.strategies.rsi_dominate_buy_sell_labeler import RsiDominateLabeler

class TestRsiDominateLabeler:
    def setup_method(self):
        self.labeler = RsiDominateLabeler()

    @pytest.mark.parametrize("macd, signal_line, rsi, expected_buy, expected_sell", [
        (1.5, 1.0, 25, True, False),  # Buy signal case
        (-0.5, -0.4, 55, False, False),  # No signal case
        (0.1, 0.2, 75, False, True),  # Corrected Sell signal case
        (-1.0, -0.8, 20, False, False)  # No signal case
    ])
    def test_signal_logic(self, macd, signal_line, rsi, expected_buy, expected_sell):
        data = pd.DataFrame({
            'MACD': [macd],
            'Signal_Line': [signal_line],
            'RSI': [rsi]
        })

        labeled_data = self.labeler.apply(data)
        assert labeled_data['Buy_Signal'].iloc[0] == expected_buy
        assert labeled_data['Sell_Signal'].iloc[0] == expected_sell

    def test_invalid_input(self):
        data = pd.DataFrame({
            'MACD': [1.5],
            'Signal_Line': [1.0]
            # Missing RSI column
        })

        with pytest.raises(ValueError):
            self.labeler.apply(data)

    def test_empty_dataframe(self):
        data = pd.DataFrame()

        with pytest.raises(ValueError):
            self.labeler.apply(data)

# Additional tests can be added for different scenarios and edge cases.
