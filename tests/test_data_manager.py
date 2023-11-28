import pytest
from unittest.mock import patch, MagicMock

import pandas as pd
import numpy as np

from src.core.manager.data_manager import DataIOButler, DataNotFoundError
from src.utils.database_adapters.base import AbstractDatabaseAdapter


class MockDatabaseAdapter(AbstractDatabaseAdapter):
    def __init__(self):
        self.data_store = {}
        self.batch_data_store = {}

    def save_data(self, key: str, value: str):
        self.data_store[key] = value

    def get_data(self, key: str) -> str:
        return self.data_store.get(key, None)

    def save_batch_data(self, key: str, value: dict, data_type: str, additional_params: dict = None):
        self.batch_data_store[key] = value

    def get_batch_data(self, key: str, data_type: str, additional_params: dict = None) -> dict:
        return self.batch_data_store.get(key, {})

    def delete_data(self, key: str) -> bool:
        return self.data_store.pop(key, None) is not None

    def exists(self, key: str) -> bool:
        return key in self.data_store

    def keys(self, pattern: str = None) -> list:
        if pattern:
            return [key for key in self.data_store if key.startswith(pattern.strip('*'))]
        return list(self.data_store.keys())


# Test the key generation
# def test_generate_key():
#     expected_key = 'prefix:stock_id:2023-01-01:2023-12-31'
#     generated_key = DataIOButler._generate_major_stock_key(prefix='prefix', stock_id='stock_id', start_date='2023-01-01', end_date='2023-12-31')
#     assert generated_key == expected_key


# Test saving data
def test_save_data():
    mock_adapter = MockDatabaseAdapter()
    data_io_butler = DataIOButler(adapter=mock_adapter)
    df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    data_io_butler.save_data(prefix='prefix', stock_id='stock_id', start_date='start_date', end_date='end_date', data=df)

    generated_key = 'prefix:stock_id:start_date:end_date'
    assert mock_adapter.get_data(generated_key) == df.to_json(orient="records")


# Test checking if data exists
def test_check_data_exists():
    mock_adapter = MockDatabaseAdapter()
    mock_adapter.save_data('prefix:stock_id:start_date:end_date', 'some data')
    data_io_butler = DataIOButler(adapter=mock_adapter)

    exists = data_io_butler.check_data_exists(prefix='prefix', stock_id='stock_id', start_date='start_date', end_date='end_date')
    assert exists is True


# Test retrieving data
def test_get_data():
    mock_adapter = MockDatabaseAdapter()
    df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    mock_adapter.save_data('prefix:stock_id:start_date:end_date', df.to_json(orient="records"))
    data_io_butler = DataIOButler(adapter=mock_adapter)

    returned_df = data_io_butler.get_data(prefix='prefix', stock_id='stock_id', start_date='start_date', end_date='end_date')
    pd.testing.assert_frame_equal(returned_df, df)


# Test data not found exception
def test_get_data_not_found():
    mock_adapter = MockDatabaseAdapter()
    data_io_butler = DataIOButler(adapter=mock_adapter)
    with pytest.raises(DataNotFoundError):
        data_io_butler.get_data(prefix='prefix', stock_id='stock_id', start_date='start_date', end_date='end_date')


# Test updating data
def test_update_data():
    mock_adapter = MockDatabaseAdapter()
    data_io_butler = DataIOButler(adapter=mock_adapter)
    original_df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    key = 'prefix:stock_id:start_date:end_date'

    mock_adapter.save_data(key, original_df.to_json(orient="records"))

    updated_df = pd.DataFrame({'col1': [5, 6], 'col2': [7, 8]})
    data_io_butler.update_data(updated_dataframe=updated_df, prefix='prefix', stock_id='stock_id', start_date='start_date', end_date='end_date')

    returned_data = mock_adapter.get_data(key)
    assert returned_data == updated_df.to_json(orient="records")



# Test deleting data
def test_delete_data():
    mock_adapter = MockDatabaseAdapter()
    data_io_butler = DataIOButler(adapter=mock_adapter)
    key = 'prefix:stock_id:start_date:end_date'

    mock_adapter.save_data(key, 'some data')

    result = data_io_butler.delete_data(prefix='prefix', stock_id='stock_id', start_date='start_date', end_date='end_date')

    assert result is True
    assert mock_adapter.get_data(key) is None


# Test listing all data keys
def test_get_all_exist_data_key():
    mock_adapter = MockDatabaseAdapter()
    mock_adapter.save_data('prefix:stock_id:2023-01-01:2023-12-31', 'some data')
    data_io_butler = DataIOButler(adapter=mock_adapter)

    keys = data_io_butler.get_all_exist_data_key('prefix')
    assert 'prefix:stock_id:2023-01-01:2023-12-31' in keys


def test_save_empty_dataframes_group():
    mock_adapter = MockDatabaseAdapter()
    data_io_butler = DataIOButler(adapter=mock_adapter)

    df_list = []
    data_io_butler.save_dataframes_group(
        group_id='group1',
        start_date='2023-01-01',
        end_date='2023-01-31',
        group_df_list=df_list
    )

    # Check if an empty hash is saved
    saved_data = mock_adapter.batch_data_store.get('group1:2023-01-01:2023-01-31', {})
    assert saved_data == {}


# def test_get_empty_dataframes_group():
#     mock_adapter = MockDatabaseAdapter()
#     data_io_butler = DataIOButler(adapter=mock_adapter)
#
#     # Simulate an empty group data scenario
#     mock_adapter.batch_data_store['group1:2023-01-01:2023-01-31'] = {}
#
#     retrieved_data = data_io_butler.get_dataframes_group(
#         group_id='group1',
#         start_date='2023-01-01',
#         end_date='2023-01-31'
#     )
#
#     # Verify that an empty dictionary is retrieved
#     assert retrieved_data == {}


# def test_get_nonexistent_dataframes_group():
#     mock_adapter = MockDatabaseAdapter()
#     data_io_butler = DataIOButler(adapter=mock_adapter)
#
#     # Attempt to retrieve a group that does not exist
#     retrieved_data = data_io_butler.get_dataframes_group(group_id='nonexistent_group', date_range='2023-01-01:2023-01-31')
#
#     # Expect an empty dictionary
#     assert retrieved_data == {}

#
# def test_save_dataframe_with_nan():
#     mock_adapter = MockDatabaseAdapter()
#     data_io_butler = DataIOButler(adapter=mock_adapter)
#
#     df_with_nan = pd.DataFrame({'col1': [1, np.nan], 'col2': [3, 4]})
#     kwargs = {
#         'group_id': 'group1',
#         'start_date': '2023-01-01',
#         'end_date': '2023-01-31',
#         'group_df_list': [df_with_nan]
#     }
#     data_io_butler.save_dataframes_group(**kwargs)
#
#     # Check if data with NaN is saved correctly
#     saved_data = mock_adapter.batch_data_store['group1:2023-01-01:2023-01-31']
#     assert 'stock:0' in saved_data

#
# def test_get_dataframe_with_nan():
#     mock_adapter = MockDatabaseAdapter()
#     data_io_butler = DataIOButler(adapter=mock_adapter)
#
#     df_with_nan = pd.DataFrame({'col1': [1, np.nan], 'col2': [3, 4]})
#     mock_adapter.batch_data_store['group1:2023-01-01:2023-01-31'] = {
#         'stock:0': df_with_nan.to_json(orient='records', default_handler=str)
#     }
#
#     retrieved_data = data_io_butler.get_dataframes_group(group_id='group1', date_range='2023-01-01:2023-01-31')
#
#     # Verify the data with NaN is correctly retrieved
#     pd.testing.assert_frame_equal(retrieved_data['stock:0'], df_with_nan)


