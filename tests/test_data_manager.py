import pytest
from unittest.mock import patch, MagicMock

import pandas as pd
import numpy as np

from src.core.manager.data_manager import DataIOButler, DataNotFoundError
from src.utils.database_adapters.base import AbstractDatabaseAdapter


class MockDatabaseAdapter(AbstractDatabaseAdapter):
    def __init__(self):
        self.data_store = {}

    def set_data(self, key: str, value: str):
        self.data_store[key] = value

    def get_data(self, key: str) -> str:
        return self.data_store.get(key, None)

    def delete_data(self, key: str) -> bool:
        return self.data_store.pop(key, None) is not None

    def exists(self, key: str) -> bool:
        return key in self.data_store

    def keys(self, pattern: str = None) -> list:
        if pattern:
            return [key for key in self.data_store if key.startswith(pattern.strip('*'))]
        return list(self.data_store.keys())


# Test the key generation
def test_generate_key():
    expected_key = 'prefix:stock_id:2023-01-01:2023-12-31'
    generated_key = DataIOButler._generate_major_stock_key('prefix', 'stock_id', '2023-01-01', '2023-12-31')
    assert generated_key == expected_key


# Test saving data
def test_save_data():
    mock_adapter = MockDatabaseAdapter()
    data_io_butler = DataIOButler(adapter=mock_adapter)
    df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    data_io_butler.save_data('prefix', 'stock_id', 'start_date', 'end_date', df)

    generated_key = 'prefix:stock_id:start_date:end_date'
    assert mock_adapter.get_data(generated_key) == df.to_json(orient="records")


# Test checking if data exists
def test_check_data_exists():
    mock_adapter = MockDatabaseAdapter()
    mock_adapter.set_data('prefix:stock_id:start_date:end_date', 'some data')
    data_io_butler = DataIOButler(adapter=mock_adapter)

    exists = data_io_butler.check_data_exists('prefix', 'stock_id', 'start_date', 'end_date')
    assert exists is True


# Test retrieving data
def test_get_data():
    mock_adapter = MockDatabaseAdapter()
    df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    mock_adapter.set_data('prefix:stock_id:start_date:end_date', df.to_json(orient="records"))
    data_io_butler = DataIOButler(adapter=mock_adapter)

    returned_df = data_io_butler.get_data('prefix', 'stock_id', 'start_date', 'end_date')
    pd.testing.assert_frame_equal(returned_df, df)


# Test data not found exception
def test_get_data_not_found():
    mock_adapter = MockDatabaseAdapter()
    data_io_butler = DataIOButler(adapter=mock_adapter)
    with pytest.raises(DataNotFoundError):
        data_io_butler.get_data('prefix', 'stock_id', 'start_date', 'end_date')


# Test updating data
def test_update_data():
    mock_adapter = MockDatabaseAdapter()
    data_io_butler = DataIOButler(adapter=mock_adapter)
    original_df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    key = 'prefix:stock_id:start_date:end_date'

    mock_adapter.set_data(key, original_df.to_json(orient="records"))

    updated_df = pd.DataFrame({'col1': [5, 6], 'col2': [7, 8]})
    data_io_butler.update_data('prefix', 'stock_id', 'start_date', 'end_date', updated_df)

    returned_data = mock_adapter.get_data(key)
    assert returned_data == updated_df.to_json(orient="records")



# Test deleting data
def test_delete_data():
    mock_adapter = MockDatabaseAdapter()
    data_io_butler = DataIOButler(adapter=mock_adapter)
    key = 'prefix:stock_id:start_date:end_date'

    mock_adapter.set_data(key, 'some data')

    result = data_io_butler.delete_data('prefix', 'stock_id', 'start_date', 'end_date')

    assert result is True
    assert mock_adapter.get_data(key) is None



# Test listing all data keys
def test_get_all_exist_data_key():
    mock_adapter = MockDatabaseAdapter()
    mock_adapter.set_data('prefix:stock_id:2023-01-01:2023-12-31', 'some data')
    data_io_butler = DataIOButler(adapter=mock_adapter)

    keys = data_io_butler.get_all_exist_data_key('prefix')
    assert 'prefix:stock_id:2023-01-01:2023-12-31' in keys

