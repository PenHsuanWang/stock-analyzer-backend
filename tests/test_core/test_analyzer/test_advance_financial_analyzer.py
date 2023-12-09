# test_advanced_financial_analyzer.py
import pandas as pd
import pytest
from src.core.analyzer.advance_financial_analyzer import AdvancedFinancialAnalyzer


# Example stock data for testing
@pytest.fixture
def example_stock_data():
    data = {
        "Open": [100, 101, 102, 103],
        "High": [105, 106, 107, 108],
        "Low": [99, 98, 97, 96],
        "Close": [104, 105, 106, 107],
        "Volume": [300, 400, 500, 600]
    }
    return pd.DataFrame(data)


@pytest.fixture
def advanced_analyzer():
    return AdvancedFinancialAnalyzer()


def test_apply_advanced_analysis(advanced_analyzer, example_stock_data):
    short_window = 12
    long_window = 26
    volume_window = 9

    # Apply the advanced analysis
    analyzed_data = advanced_analyzer.apply_advanced_analysis(
        example_stock_data, short_window, long_window, volume_window
    )

    # Check if all expected columns are in the output DataFrame
    expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume',
                        'MACD', 'Signal_Line', 'Bollinger_Mid',
                        'Bollinger_Upper', 'Bollinger_Lower', 'RSI']
    for column in expected_columns:
        assert column in analyzed_data.columns, f"{column} is missing in the analyzed data"

    # Optionally, you can add more specific tests for the values,
    # e.g., to check if MACD is calculated correctly
    # This would require known input and output data for comparison


# To run the test
if __name__ == "__main__":
    pytest.main()
