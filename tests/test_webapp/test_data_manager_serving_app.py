import pytest
from src.webapp.serving_app.data_manager_serving_app import DataManagerApp
import pandas as pd
import numpy as np
from datetime import datetime

test_data = pd.DataFrame({
    "date": pd.date_range(start="2023-01-01", end="2023-01-10"),
    "value": np.random.rand(10)
})
test_prefix = "test"
test_stock_id = "AAPL"
test_start_date = "2023-01-01"
test_end_date = "2023-01-10"


@pytest.fixture(scope="module")
def data_manager_app():
    return DataManagerApp()


def test_save_and_get_stock_data(data_manager_app):
    data_manager_app.update_stock_data(test_prefix, test_stock_id, test_start_date, test_end_date, test_data)

    fetched_data = data_manager_app.get_stock_data(test_prefix, test_stock_id, test_start_date, test_end_date)

    print("Original Data Index:", test_data.index)
    print("Fetched Data Index:", fetched_data.index)
    print("Original Data Type:", test_data["value"].dtype)
    print("Fetched Data Type:", fetched_data["value"].dtype)

    assert not fetched_data.empty
    pd.testing.assert_frame_equal(fetched_data.reset_index(drop=True), test_data.reset_index(drop=True),
                                  check_dtype=False)


def test_check_data_exists(data_manager_app):
    exists = data_manager_app.check_data(test_prefix, test_stock_id, test_start_date, test_end_date)
    assert exists == True


def test_delete_stock_data(data_manager_app):
    data_manager_app.delete_stock_data(test_prefix, test_stock_id, test_start_date, test_end_date)
    exists_after_delete = data_manager_app.check_data(test_prefix, test_stock_id, test_start_date, test_end_date)
    assert exists_after_delete == False


def test_save_and_get_dataframes_group(data_manager_app):
    group_id = "test_group"
    start_date = "2023-01-01"
    end_date = "2023-01-05"
    num_stocks = 3
    date_range = pd.date_range(start=start_date, end=end_date)
    group_df_list = [pd.DataFrame(np.random.rand(len(date_range), 4), columns=list('ABCD'), index=date_range) for _ in range(num_stocks)]

    # test save
    save_success = data_manager_app.save_dataframes_group(group_id, start_date, end_date, group_df_list)
    assert save_success == True

    # test fetch
    fetched_group = data_manager_app.get_dataframes_group(group_id, start_date, end_date)
    assert len(fetched_group) == num_stocks
    for i in range(num_stocks):
        pd.testing.assert_frame_equal(fetched_group[i], group_df_list[i], check_dtype=False)

    # test delete
    delete_success = data_manager_app.delete_dataframes_group(group_id, start_date, end_date)
    assert delete_success == True
    fetched_group_after_delete = data_manager_app.get_dataframes_group(group_id, start_date, end_date)
    assert len(fetched_group_after_delete) == 0

def test_exception_handling(data_manager_app):
    # test invalid parameters
    with pytest.raises(Exception):
        data_manager_app.get_stock_data("", "", "", "")
    with pytest.raises(Exception):
        data_manager_app.update_stock_data("", "", "", "", pd.DataFrame())

def test_empty_data_handling(data_manager_app):
    # test empty data
    empty_data = pd.DataFrame()
    update_success = data_manager_app.update_stock_data(test_prefix, test_stock_id, test_start_date, test_end_date, empty_data)
    assert update_success == True

    fetched_empty_data = data_manager_app.get_stock_data(test_prefix, test_stock_id, test_start_date, test_end_date)
    assert fetched_empty_data.empty

    # test to delete not exist data
    delete_non_exist = data_manager_app.delete_stock_data(test_prefix, "non_exist_stock", test_start_date, test_end_date)
    assert delete_non_exist == True


def test_boundary_dates(data_manager_app):
    early_date = "1970-01-01"
    late_date = "2100-01-01"
    sample_data = pd.DataFrame({
        "date": pd.date_range(start=early_date, end=early_date),
        "value": [1]
    })

    # Test the earliest date
    data_manager_app.update_stock_data(test_prefix, test_stock_id, early_date, early_date, sample_data)
    early_data = data_manager_app.get_stock_data(test_prefix, test_stock_id, early_date, early_date)

    # Debugging output
    print("Sample Data:", sample_data)
    print("Early Data Before Conversion:", early_data)

    early_data['date'] = pd.to_datetime(early_data['date'])

    # Debugging output
    print("Early Data After Conversion:", early_data)

    assert early_data['date'].dt.date.equals(sample_data['date'].dt.date)

    # Test the latest date
    data_manager_app.update_stock_data(test_prefix, test_stock_id, late_date, late_date, sample_data)
    late_data = data_manager_app.get_stock_data(test_prefix, test_stock_id, late_date, late_date)

    # Debugging output
    print("Late Data Before Conversion:", late_data)

    late_data['date'] = pd.to_datetime(late_data['date'])

    # Debugging output
    print("Late Data After Conversion:", late_data)

    assert late_data['date'].dt.date.equals(sample_data['date'].dt.date)


def test_empty_and_invalid_parameters(data_manager_app):
    # 测试空字符串
    assert data_manager_app.update_stock_data("", "", "", "", pd.DataFrame()) == False
    assert data_manager_app.get_stock_data("", "", "", "").empty
    assert data_manager_app.delete_stock_data("", "", "", "") == False

    # 测试None作为参数
    # with pytest.raises(TypeError):
    #     data_manager_app.update_stock_data(None, None, None, None, None)
    # with pytest.raises(TypeError):
    #     data_manager_app.get_stock_data(None, None, None, None)
    # with pytest.raises(TypeError):
    #     data_manager_app.delete_stock_data(None, None, None, None)


def test_data_integrity(data_manager_app):
    sample_data = pd.DataFrame({
        "date": pd.date_range(start="2023-01-01", end="2023-01-05"),
        "value": np.random.rand(5)
    })

    data_manager_app.update_stock_data(test_prefix, test_stock_id, "2023-01-01", "2023-01-05", sample_data)
    fetched_data = data_manager_app.get_stock_data(test_prefix, test_stock_id, "2023-01-01", "2023-01-05")

    assert not fetched_data.empty
    pd.testing.assert_frame_equal(fetched_data, sample_data, check_like=True)


def test_data_types(data_manager_app):
    sample_data = pd.DataFrame({
        "date": pd.date_range(start="2023-01-01", end="2023-01-05"),
        "value": np.random.rand(5)
    })

    data_manager_app.update_stock_data(test_prefix, test_stock_id, "2023-01-01", "2023-01-05", sample_data)
    fetched_data = data_manager_app.get_stock_data(test_prefix, test_stock_id, "2023-01-01", "2023-01-05")

    assert fetched_data["date"].dtype == sample_data["date"].dtype
    assert fetched_data["value"].dtype == sample_data["value"].dtype

