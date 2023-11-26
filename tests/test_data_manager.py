import pytest
from unittest.mock import patch, MagicMock
from core.manager.data_manager import DataIOButler, DataNotFoundError
import pandas as pd
import numpy as np


# Test the key generation
def test_generate_key():
    expected_key = 'prefix:stock_id:2023-01-01:2023-12-31'
    generated_key = DataIOButler._generate_major_stock_key('prefix', 'stock_id', '2023-01-01', '2023-12-31')
    assert generated_key == expected_key


# Test saving data
@patch('redis.StrictRedis.set')
def test_save_data(mock_set):
    data_io_butler = DataIOButler()
    df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    data_io_butler.save_data('prefix', 'stock_id', 'start_date', 'end_date', df)
    mock_set.assert_called_once()


# Test checking if data exists
@patch('redis.StrictRedis.exists', return_value=True)
def test_check_data_exists(mock_exists):
    data_io_butler = DataIOButler()
    exists = data_io_butler.check_data_exists('prefix', 'stock_id', 'start_date', 'end_date')
    assert exists is True


# Test retrieving data
@patch('redis.StrictRedis.get')
def test_get_data(mock_get):
    data_io_butler = DataIOButler()
    df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    mock_get.return_value = df.to_json(orient="records").encode('utf-8')
    returned_df = data_io_butler.get_data('prefix', 'stock_id', 'start_date', 'end_date')
    pd.testing.assert_frame_equal(returned_df, df)


# Test data not found exception
@patch('redis.StrictRedis.get', return_value=None)
def test_get_data_not_found(mock_get):
    data_io_butler = DataIOButler()
    with pytest.raises(DataNotFoundError):
        data_io_butler.get_data('prefix', 'stock_id', 'start_date', 'end_date')


# Test updating data
@patch('redis.StrictRedis.pipeline')
def test_update_data(mock_pipeline):
    pipeline = MagicMock()
    pipeline.set.return_value = pipeline
    pipeline.execute.return_value = None
    mock_pipeline.return_value.__enter__.return_value = pipeline

    data_io_butler = DataIOButler()
    df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    data_io_butler.update_data('prefix', 'stock_id', 'start_date', 'end_date', df)
    pipeline.set.assert_called_once()
    pipeline.execute.assert_called_once()


# Test deleting data
@patch('redis.StrictRedis.delete', return_value=1)
def test_delete_data(mock_delete):
    data_io_butler = DataIOButler()
    result = data_io_butler.delete_data('prefix', 'stock_id', 'start_date', 'end_date')
    assert result is True


# Test listing all data keys
@patch('redis.StrictRedis.keys', return_value=[b'prefix:stock_id:2023-01-01:2023-12-31'])
def test_get_all_exist_data_key(mock_keys):
    data_io_butler = DataIOButler()
    keys = data_io_butler.get_all_exist_data_key('prefix')
    assert keys == [b'prefix:stock_id:2023-01-01:2023-12-31']
