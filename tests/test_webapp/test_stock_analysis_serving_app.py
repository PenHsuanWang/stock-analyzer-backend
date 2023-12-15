from unittest.mock import patch
from fastapi import HTTPException

from src.webapp.serving_app.stock_analyzer_basic_serving_app import StockAnalyzerBasicServingApp

import pandas as pd
import pytest
from src.core.analyzer.moving_average_analyzer import MovingAverageAnalyzer
from src.core.analyzer.daily_return_analyzer import DailyReturnAnalyzer
from src.core.analyzer.candlestick_pattern_analyzer import CandlestickPatternAnalyzer
from src.core.analyzer.advance_financial_analyzer import AdvancedFinancialAnalyzer


def test_singleton_instance():
    app1 = StockAnalyzerBasicServingApp()
    app2 = StockAnalyzerBasicServingApp()
    assert app1 is app2


@pytest.fixture
def valid_stock_data():
    return pd.DataFrame({
        'Open': [100, 101],
        'High': [102, 103],
        'Low': [99, 98],
        'Close': [101, 102],
        'Volume': [1000, 2000]
    })


@pytest.fixture
def invalid_stock_data():
    return pd.DataFrame({
        'Open': [100, 101],
        'Low': [99, 98],
        'Close': [101, 102]
    })


def test_apply_candlestick_pattern_analyzer_valid_data(valid_stock_data):
    app = StockAnalyzerBasicServingApp()
    result = app._apply_candlestick_pattern_analyzer(valid_stock_data)
    assert 'Pattern' in result.columns


def test_apply_candlestick_pattern_analyzer_invalid_data(invalid_stock_data):
    app = StockAnalyzerBasicServingApp()
    with pytest.raises(ValueError):
        app._apply_candlestick_pattern_analyzer(invalid_stock_data)


def test_fetch_data_and_get_as_dataframe_success():
    app = StockAnalyzerBasicServingApp()
    # Mock the YFinanceFetcher's fetch_from_source and get_as_dataframe methods
    with patch.object(app._data_fetcher, 'fetch_from_source'), \
         patch.object(app._data_fetcher, 'get_as_dataframe', return_value=pd.DataFrame()):
        df = app._fetch_data_and_get_as_dataframe('AAPL', '2023-01-01', '2023-01-31')
        assert isinstance(df, pd.DataFrame)


def test_fetch_data_and_get_as_dataframe_exception():
    app = StockAnalyzerBasicServingApp()
    # Mock the YFinanceFetcher's fetch_from_source method to raise an exception
    with patch.object(app._data_fetcher, 'fetch_from_source', side_effect=Exception):
        with pytest.raises(RuntimeError):
            app._fetch_data_and_get_as_dataframe('AAPL', '2023-01-01', '2023-01-31')


# test fetch_and_do_full_ana_and_save success
def test_fetch_and_do_full_ana_and_save_success(valid_stock_data):
    app = StockAnalyzerBasicServingApp()
    # Mock _fetch_data_and_get_as_dataframe to return valid stock data
    with patch.object(app, '_fetch_data_and_get_as_dataframe', return_value=valid_stock_data), \
         patch.object(app._data_io_butler, 'save_data') as mock_save:
        app.fetch_and_do_full_ana_and_save('AAPL', '2023-01-01', '2023-01-31', [5, 10])
        mock_save.assert_called()


# test fetch_and_do_full_ana_and_save with exception
def test_fetch_and_do_full_ana_and_save_exception():
    app = StockAnalyzerBasicServingApp()
    # Mock _fetch_data_and_get_as_dataframe to raise an exception
    with patch.object(app, '_fetch_data_and_get_as_dataframe', side_effect=Exception):
        with pytest.raises(HTTPException):
            app.fetch_and_do_full_ana_and_save('AAPL', '2023-01-01', '2023-01-31', [5, 10])


# test calculating_full_ana_and_saved_as_analyzed_prefix success complete
def test_calculating_full_ana_and_saved_as_analyzed_prefix_success(valid_stock_data):
    app = StockAnalyzerBasicServingApp()
    # Mock get_data to return valid stock data and save_data for checking if it's called
    with patch.object(app._data_io_butler, 'get_data', return_value=valid_stock_data), \
         patch.object(app._data_io_butler, 'save_data') as mock_save:
        app.calculating_full_ana_and_saved_as_analyzed_prefix('raw_stock_data', 'AAPL', '2023-01-01', '2023-01-31', [5, 10])
        mock_save.assert_called()


# test calculate_correlation success case
def test_calculate_correlation_success(valid_stock_data):
    app = StockAnalyzerBasicServingApp()
    # Mock get_data to return valid stock data
    with patch.object(app._data_io_butler, 'get_data', return_value=valid_stock_data):
        correlation_df = app.calculate_correlation(['AAPL', 'MSFT'], '2023-01-01', '2023-01-31', 'Close')
        assert isinstance(correlation_df, pd.DataFrame)


# test analyze_candlestick_patterns success analysis
def test_analyze_candlestick_patterns_success(valid_stock_data):
    app = StockAnalyzerBasicServingApp()
    # Mock get_data to return valid stock data
    with patch.object(app._data_io_butler, 'get_data', return_value=valid_stock_data):
        patterns_df = app.analyze_candlestick_patterns('AAPL', '2023-01-01', '2023-01-31')
        assert 'Pattern' in patterns_df.columns


# Sample stock data for testing
sample_data = {
    "Open": [100, 101, 102],
    "High": [105, 106, 107],
    "Low": [95, 96, 97],
    "Close": [102, 103, 104],
    "Volume": [1000, 1100, 1200],
}
sample_df = pd.DataFrame(sample_data)


@pytest.fixture
def stock_analyzer():
    ma_analyzer = MovingAverageAnalyzer()
    daily_return_analyzer = DailyReturnAnalyzer()
    candlestick_analyzer = CandlestickPatternAnalyzer()
    advanced_analyzer = AdvancedFinancialAnalyzer()
    return {
        "ma_analyzer": ma_analyzer,
        "daily_return_analyzer": daily_return_analyzer,
        "candlestick_analyzer": candlestick_analyzer,
        "advanced_analyzer": advanced_analyzer
    }


def test_advanced_analysis_columns_unchanged(stock_analyzer):
    # Perform basic analysis
    analyzed_data = stock_analyzer["ma_analyzer"].calculate_moving_average(sample_df, [3])
    analyzed_data = stock_analyzer["daily_return_analyzer"].calculate_daily_return(analyzed_data)
    analyzed_data = stock_analyzer["candlestick_analyzer"].analyze_patterns(analyzed_data)

    # Capture the original columns before advanced analysis
    original_columns = set(analyzed_data.columns)

    # Perform advanced analysis
    analyzed_data = stock_analyzer["advanced_analyzer"].apply_advanced_analysis(
        analyzed_data, short_window=12, long_window=26, volume_window=20)

    # Capture the columns after advanced analysis
    advanced_columns = set(analyzed_data.columns)

    # Check if original columns are preserved after advanced analysis
    assert original_columns.issubset(advanced_columns), "Original columns have been altered after advanced analysis."



