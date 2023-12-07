import pytest
import pandas as pd
from src.core.analyzer.advance_financial_analyzer import AdvancedFinancialAnalyzer

# Sample data for testing
data = {
    'Date': ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04', '2021-01-05'],
    'Close': [100, 102, 101, 105, 107],
    'Volume': [200, 220, 210, 240, 230],
    'High': [102, 103, 102, 106, 108],
    'Low': [98, 101, 100, 104, 106]
}
sample_df = pd.DataFrame(data)
sample_df['Date'] = pd.to_datetime(sample_df['Date'])
sample_df.set_index('Date', inplace=True)


@pytest.fixture
def stock_data():
    return sample_df.copy()


@pytest.fixture
def empty_data():
    return pd.DataFrame()


# Testing EMA Calculation
def test_compute_ema(stock_data):
    result = AdvancedFinancialAnalyzer.compute_ema(stock_data, window=2, column='Close')
    assert not result.empty
    assert result.iloc[-1] == pytest.approx(106.75, 0.01)  # Check last EMA value


# Testing EMA Calculation with empty data
def test_compute_ema_empty(empty_data):
    with pytest.raises(KeyError):
        AdvancedFinancialAnalyzer.compute_ema(empty_data, window=2, column='Close')


# Test EMA with invalid window size
def test_compute_ema_invalid_window(stock_data):
    with pytest.raises(ValueError):
        AdvancedFinancialAnalyzer.compute_ema(stock_data, window=-1, column='Close')


# Testing MACD Calculation
def test_compute_macd(stock_data):
    result = AdvancedFinancialAnalyzer.compute_macd(stock_data)
    assert all(key in result for key in ['MACD', 'Signal_Line'])


# Testing Bollinger Bands Calculation
def test_compute_bollinger_bands(stock_data):
    result = AdvancedFinancialAnalyzer.compute_bollinger_bands(stock_data)
    assert all(key in result for key in ['Bollinger_Mid', 'Bollinger_Upper', 'Bollinger_Lower'])


# Testing RSI Calculation
def test_compute_rsi(stock_data):
    result = AdvancedFinancialAnalyzer.compute_rsi(stock_data)
    assert 'RSI' in result


# Testing Fibonacci Retracement Calculation
def test_compute_fibonacci_retracement(stock_data):
    stock_data_reset = stock_data.reset_index()  # Reset index to make 'Date' a column
    levels = AdvancedFinancialAnalyzer.compute_fibonacci_retracement(stock_data_reset, '2021-01-01', '2021-01-05')
    assert isinstance(levels, dict)
    assert 'Level_0' in levels and 'Level_100' in levels


# Test Fibonacci Retracement with invalid date range
def test_compute_fibonacci_retracement_invalid_date(stock_data):
    with pytest.raises(ValueError):
        _ = AdvancedFinancialAnalyzer.compute_fibonacci_retracement(stock_data, '2021-01-10', '2021-01-15')


# Testing Combined Strategy Application
def test_apply_strategy(stock_data):
    result = AdvancedFinancialAnalyzer.apply_strategy(stock_data, 2, 5, 3)
    assert all(key in result for key in ['Buy_Signal', 'Sell_Signal'])


# Test MACD with valid data
def test_compute_macd_valid(stock_data):
    result = AdvancedFinancialAnalyzer.compute_macd(stock_data)
    assert 'MACD' in result and 'Signal_Line' in result


# Test MACD with empty data
def test_compute_macd_empty(empty_data):
    result = AdvancedFinancialAnalyzer.compute_macd(empty_data)
    assert result.empty


# Test Bollinger Bands with valid data
def test_compute_bollinger_bands_valid(stock_data):
    result = AdvancedFinancialAnalyzer.compute_bollinger_bands(stock_data)
    assert all(key in result for key in ['Bollinger_Mid', 'Bollinger_Upper', 'Bollinger_Lower'])


# Test Bollinger Bands with empty data
def test_compute_bollinger_bands_empty(empty_data):
    result = AdvancedFinancialAnalyzer.compute_bollinger_bands(empty_data)
    assert result.empty


# Test RSI with valid data
def test_compute_rsi_valid(stock_data):
    result = AdvancedFinancialAnalyzer.compute_rsi(stock_data)
    assert 'RSI' in result


# Test RSI with empty data
def test_compute_rsi_empty(empty_data):
    result = AdvancedFinancialAnalyzer.compute_rsi(empty_data)
    assert result.empty


# Test Combined Strategy with valid data
def test_apply_strategy_valid(stock_data):
    result = AdvancedFinancialAnalyzer.apply_strategy(stock_data, 2, 5, 3)
    assert 'Buy_Signal' in result and 'Sell_Signal' in result


# Test Combined Strategy with empty data
def test_apply_strategy_empty(empty_data):
    result = AdvancedFinancialAnalyzer.apply_strategy(empty_data, 2, 5, 3)
    assert result.empty