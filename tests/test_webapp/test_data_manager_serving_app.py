from unittest import mock
import pytest
from src.webapp.serving_app.data_manager_serving_app import DataManagerApp, get_app
from src.core.manager.data_manager import DataIOButler
from src.utils.database_adapters.redis_adapter import RedisAdapter
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal


test_data = pd.DataFrame({
    "date": pd.date_range(start="2023-01-01", end="2023-01-10"),
    "value": [1.0] * 10
})
test_prefix = "test"
test_stock_id = "AAPL"
test_start_date = "2023-01-01"
test_end_date = "2023-01-10"


# Mock Redis Adapter
@pytest.fixture(scope="module")
def mock_redis_adapter():
    with mock.patch('src.utils.database_adapters.redis_adapter.RedisAdapter', autospec=True) as mock_adapter:
        mock_adapter_instance = mock_adapter.return_value
        mock_adapter_instance.get_data.return_value = test_data.to_json(orient="records")
        mock_adapter_instance.save_data.return_value = None

        # Initially, let's assume the data exists
        mock_adapter_instance.exists.return_value = True

        # After delete_stock_data is called, data should not exist
        def reset_exists(*args, **kwargs):
            mock_adapter_instance.exists.return_value = False
            return True
        mock_adapter_instance.delete_data.side_effect = reset_exists

        # Mock for batch data operations
        mock_data_store = {}

        def mock_save_batch_data(key, value, data_type, additional_params=None):
            if data_type == 'hash':
                serialized_value = {}
                for k, v in value.items():
                    # Ensure v is a DataFrame before calling to_json
                    if isinstance(v, pd.DataFrame):
                        serialized_value[k] = v.to_json(orient='split')
                    else:
                        serialized_value[k] = v  # Assuming v is already a serialized string
                mock_data_store[key] = serialized_value
            return True

        def mock_get_batch_data(key, data_type, additional_params=None):
            if data_type == 'hash_keys' and key in mock_data_store:
                # Deserialize each stored DataFrame
                stored_data = mock_data_store[key]
                return {k: pd.read_json(v, orient='split') for k, v in stored_data.items() if v}
            return {}

        mock_adapter_instance.save_batch_data.side_effect = mock_save_batch_data
        mock_adapter_instance.get_batch_data.side_effect = mock_get_batch_data

        yield mock_adapter_instance



@pytest.fixture(scope="module")
def data_manager_app(mock_redis_adapter):
    data_io_butler = DataIOButler(adapter=mock_redis_adapter)
    return get_app(data_io_butler=data_io_butler)

def test_get_stock_data(data_manager_app):
    fetched_data = data_manager_app.get_stock_data(test_prefix, test_stock_id, test_start_date, test_end_date)

    assert isinstance(fetched_data, pd.DataFrame), "The fetched data should be a DataFrame"

    fetched_data["value"] = fetched_data["value"].astype(float)

    assert_frame_equal(fetched_data, test_data)


def test_save_and_get_stock_data(data_manager_app):
    data_manager_app.update_stock_data(test_prefix, test_stock_id, test_start_date, test_end_date, test_data)
    fetched_data = data_manager_app.get_stock_data(test_prefix, test_stock_id, test_start_date, test_end_date)
    assert not fetched_data.empty
    assert_frame_equal(fetched_data, test_data, check_dtype=False)

def test_check_data_exists(data_manager_app):
    exists = data_manager_app.check_data(test_prefix, test_stock_id, test_start_date, test_end_date)
    assert exists

def test_delete_stock_data(data_manager_app):
    data_manager_app.delete_stock_data(test_prefix, test_stock_id, test_start_date, test_end_date)
    exists_after_delete = data_manager_app.check_data(test_prefix, test_stock_id, test_start_date, test_end_date)
    assert not exists_after_delete


# Parametrized Test for Group DataFrame Operations
@pytest.mark.parametrize("group_id, start_date, end_date, num_stocks", [
    ("test_group", "2023-01-01", "2023-01-05", 3),
    ("empty_group", "2023-01-01", "2023-01-05", 0)  # Edge case: empty group
])
def test_group_dataframe_operations(data_manager_app, group_id, start_date, end_date, num_stocks):
    date_range = pd.date_range(start=start_date, end=end_date)
    group_df_list = [pd.DataFrame(np.random.rand(len(date_range), 4), columns=list('ABCD'), index=date_range) for _ in range(num_stocks)]

    save_success = data_manager_app.save_dataframes_group(group_id, start_date, end_date, group_df_list)
    assert save_success, f"Failed to save dataframes group for group_id={group_id}, num_stocks={num_stocks}"

    fetched_group = data_manager_app.get_dataframes_group(group_id, start_date, end_date)
    assert len(fetched_group) == num_stocks, f"Expected {num_stocks} dataframes for group_id={group_id}, got {len(fetched_group)}"

    for i, df in enumerate(group_df_list):
        assert_frame_equal(fetched_group[f'stock:{i+1}'], df, check_dtype=False), f"Mismatch in DataFrame for group_id={group_id}, stock:{i+1}"

    delete_success = data_manager_app.delete_dataframes_group(group_id, start_date, end_date)
    assert delete_success, f"Failed to delete dataframes group for group_id={group_id}"
    assert len(data_manager_app.get_dataframes_group(group_id, start_date, end_date)) == 0, f"Group should be empty after deletion for group_id={group_id}"


def test_boundary_dates(data_manager_app):
    early_date = "1970-01-01"
    late_date = "2100-01-01"
    sample_data = pd.DataFrame({
        "date": pd.date_range(start=early_date, end=early_date),
        "value": [1]
    })

    data_manager_app.update_stock_data(test_prefix, test_stock_id, early_date, early_date, sample_data)
    early_data = data_manager_app.get_stock_data(test_prefix, test_stock_id, early_date, early_date)
    early_data['date'] = pd.to_datetime(early_data['date'])
    assert early_data['date'].dt.date.equals(sample_data['date'].dt.date)

    data_manager_app.update_stock_data(test_prefix, test_stock_id, late_date, late_date, sample_data)
    late_data = data_manager_app.get_stock_data(test_prefix, test_stock_id, late_date, late_date)
    late_data['date'] = pd.to_datetime(late_data['date'])
    assert late_data['date'].dt.date.equals(sample_data['date'].dt.date)



def test_empty_and_invalid_parameters(data_manager_app):
    assert not data_manager_app.update_stock_data("", "", "", "", pd.DataFrame())
    assert data_manager_app.get_stock_data("", "", "", "").empty
    assert not data_manager_app.delete_stock_data("", "", "", "")


def test_data_integrity(data_manager_app):
    sample_data = pd.DataFrame({
        "date": pd.date_range(start="2023-01-01", end="2023-01-05"),
        "value": np.random.rand(5)
    })

    data_manager_app.update_stock_data(test_prefix, test_stock_id, "2023-01-01", "2023-01-05", sample_data)
    fetched_data = data_manager_app.get_stock_data(test_prefix, test_stock_id, "2023-01-01", "2023-01-05")
    assert not fetched_data.empty
    assert_frame_equal(fetched_data, sample_data, check_like=True)


def test_data_types(data_manager_app):
    sample_data = pd.DataFrame({
        "date": pd.date_range(start="2023-01-01", end="2023-01-05"),
        "value": np.random.rand(5)
    })

    data_manager_app.update_stock_data(test_prefix, test_stock_id, "2023-01-01", "2023-01-05", sample_data)
    fetched_data = data_manager_app.get_stock_data(test_prefix, test_stock_id, "2023-01-01", "2023-01-05")

    assert fetched_data["date"].dtype == sample_data["date"].dtype
    assert fetched_data["value"].dtype == sample_data["value"].dtype

