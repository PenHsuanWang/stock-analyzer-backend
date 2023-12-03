import pytest
from datetime import datetime
import pandas as pd
from src.utils.data_inbound.data_fetcher import YFinanceFetcher


# Mock YahooFinanceFetcher, assuming it is being used in DataFetcher
@pytest.fixture
def mock_yfinance(mocker):
    mock = mocker.patch("src.utils.data_inbound.data_fetcher.yf")
    mock.Ticker.return_value.info = {"symbol": "AAPL"}
    mock.download.return_value = pd.DataFrame({'Open': [100, 101], 'Close': [102, 103]})
    return mock


def test_extract_fetch_stock_and_time_range_params():
    fetcher = YFinanceFetcher()
    stock_id, start_date, end_date = fetcher._extract_fetch_stock_and_time_range_params(
        stock_id="AAPL", start_date="2023-01-01", end_date="2023-01-31")
    assert stock_id == "AAPL"
    assert start_date == "2023-01-01"
    assert end_date == "2023-01-31"


def test_extract_fetch_stock_and_time_range_params_invalid():
    fetcher = YFinanceFetcher()
    with pytest.raises(ValueError):
        fetcher._extract_fetch_stock_and_time_range_params(stock_id="AAPL", start_date="invalid_date", end_date="2023-01-31")


def test_fetch_from_source_success(mock_yfinance):
    fetcher = YFinanceFetcher()
    fetcher.fetch_from_source(stock_id="AAPL", start_date="2023-01-01", end_date="2023-01-31")
    assert not fetcher._fetched_data.empty


def test_fetch_from_source_invalid(mock_yfinance):
    mock_yfinance.download.side_effect = Exception("Error fetching data")
    fetcher = YFinanceFetcher()
    with pytest.raises(Exception):
        fetcher.fetch_from_source(stock_id="AAPL", start_date="2023-01-01", end_date="2023-01-31")


def test_get_as_dataframe_success():
    fetcher = YFinanceFetcher()
    fetcher._fetched_data = pd.DataFrame({'Open': [100, 101], 'Close': [102, 103]})
    df = fetcher.get_as_dataframe()
    assert not df.empty


def test_get_as_dataframe_invalid():
    fetcher = YFinanceFetcher()
    fetcher._fetched_data = None
    with pytest.raises(ValueError):
        fetcher.get_as_dataframe()
