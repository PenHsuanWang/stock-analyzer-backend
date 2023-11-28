from src.webapp.serving_app.stock_analysis_serving_app import StockAnalysisServingApp

import pandas as pd
import pytest


def test_singleton_instance():
    app1 = StockAnalysisServingApp()
    app2 = StockAnalysisServingApp()
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
    app = StockAnalysisServingApp()
    result = app._apply_candlestick_pattern_analyzer(valid_stock_data)
    assert 'Pattern' in result.columns


def test_apply_candlestick_pattern_analyzer_invalid_data(invalid_stock_data):
    app = StockAnalysisServingApp()
    with pytest.raises(ValueError):
        app._apply_candlestick_pattern_analyzer(invalid_stock_data)

