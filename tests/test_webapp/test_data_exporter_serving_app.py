import pytest
from unittest.mock import patch, Mock
from src.webapp.serving_app.data_exporter_serving_app import DataExporterApp, SingleStockDataGetStrategy, GroupStockDataGetStrategy
from src.utils.database_adapters.redis_adapter import RedisAdapter
from src.utils.data_outbound.csv_exporter import CSVExporter
from src.utils.data_outbound.http_data_sender import HTTPDataSender
import pandas as pd
from io import StringIO
import json

# Prepare the mock data as a JSON string, as it would be stored in Redis
mock_single_stock_data = pd.DataFrame({'test': [1, 2, 3]})
mock_single_stock_data_json = mock_single_stock_data.to_json(orient="records")

@pytest.fixture
def mock_redis_adapter():
    # Mock RedisAdapter methods
    mock_adapter = Mock(spec=RedisAdapter)
    # Mock get_data to return a JSON string
    mock_adapter.get_data.return_value = mock_single_stock_data_json

    # Mock get_batch_data to return a dictionary of JSON strings
    mock_adapter.get_batch_data.return_value = {
        'group1': mock_single_stock_data.to_json(orient="records")
    }

    return mock_adapter

@pytest.fixture
def app(mock_redis_adapter):
    # Inject the mock RedisAdapter into the application's data strategies
    app_instance = DataExporterApp()
    app_instance._get_data_strategies = {
        "stock_data:": SingleStockDataGetStrategy(mock_redis_adapter),
        "group_stock_data:": GroupStockDataGetStrategy(mock_redis_adapter),
    }
    return app_instance


def test_export_data_to_csv_success(app):
    # Mock CSVExporter.export_data method within the test case
    with patch('src.utils.data_outbound.csv_exporter.CSVExporter.export_data', return_value=None) as mock_export_method:
        response = app.export_data('stock_data:stock_id:2021-01-01:2021-12-31', 'csv', filepath='test.csv')
        assert response == {"message": "Data exported to CSV successfully."}
        mock_export_method.assert_called_once()


def test_export_data_to_http_success(app):
    # Mock HTTPDataSender.export_data method within the test case
    with patch('src.utils.data_outbound.http_data_sender.HTTPDataSender.export_data', return_value=Mock(status_code=200)) as mock_http_export_method:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Data sent successfully."}
        mock_http_export_method.return_value = mock_response

        response = app.export_data('stock_data:stock_id:2021-01-01:2021-12-31', 'http', url='http://test.com')
        assert mock_http_export_method.called
        assert response == mock_response

def test_single_stock_data_get_strategy(app):
    strategy = app._get_data_strategies["stock_data:"]
    data = strategy.get_data_from_db('stock_data:stock_id:2021-01-01:2021-12-31')
    assert not data.empty

def test_group_stock_data_get_strategy(app):
    strategy = app._get_data_strategies["group_stock_data:"]
    data = strategy.get_data_from_db('group_stock_data:group_id:2021-01-01:2021-12-31')
    assert 'group1' in data and not data['group1'].empty

def test_export_data_to_http_success(app):
    # Mock HTTPDataSender's export_data method within the test case
    with patch('src.utils.data_outbound.http_data_sender.HTTPDataSender.export_data', return_value=Mock(status_code=200)) as mock_http_export_method:
        response = app.export_data('stock_data:stock_id:2021-01-01:2021-12-31', 'http', url='http://test.com')
        assert mock_http_export_method.called
        mock_response = mock_http_export_method.return_value
        assert response == mock_response

def test_export_data_invalid_key(app):
    with pytest.raises(ValueError):
        app.export_data('invalid_key', 'csv', filepath='test.csv')

def test_export_data_invalid_type(app):
    with pytest.raises(ValueError):
        app.export_data('stock_data:stock_id:2021-01-01:2021-12-31', 'invalid_type', filepath='test.csv')