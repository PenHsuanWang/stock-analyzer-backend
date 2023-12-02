from fastapi.testclient import TestClient
from unittest.mock import patch
from src.webapp.router.data_manager_serving_app_router import router
from src.core.manager.data_manager import DataIOButler
import pandas as pd
import numpy as np

client = TestClient(router)


# Test get_all_data_keys endpoint
@patch.object(DataIOButler, 'get_all_exist_data_key', return_value=[b'my_key'])
def test_get_all_data_keys(mock_get_keys):
    response = client.post("/stock_data/get_all_keys", json={"prefix": "my_prefix"})
    assert response.status_code == 200
    assert response.json() == {"keys": ["my_key"]}


# Test get_stock_data endpoint
@patch.object(DataIOButler, 'get_data')
def test_get_stock_data(mock_get_data):
    df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    mock_get_data.return_value = df
    response = client.post("/stock_data/get_data", json={
        "prefix": "my_prefix",
        "stock_id": "stock_id",
        "start_date": "start_date",
        "end_date": "end_date"
    })
    assert response.status_code == 200
    assert response.json() == {"data": df.to_dict(orient="records")}


def test_check_data_exists():
    response = client.post("/stock_data/check_data_exists", json={
        "prefix": "test_prefix",
        "stock_id": "test_stock_id",
        "start_date": "2023-01-01",
        "end_date": "2023-01-30"
    })
    assert response.status_code == 200


def test_save_and_get_delete_dataframes_group():
    date_range = pd.date_range(start="2023-01-01", end="2023-01-30")
    group_df_list = [pd.DataFrame(np.random.randn(len(date_range), 4), columns=list('ABCD'), index=date_range).to_dict(orient='records') for _ in range(5)]

    save_response = client.post("/group_data/save", json={
        "group_id": "test_group_id",
        "start_date": "2023-01-01",
        "end_date": "2023-01-30",
        "group_df_list": group_df_list
    })
    assert save_response.status_code == 200

    get_response = client.get("/group_data/get", params={
        "group_id": "test_group_id",
        "start_date": "2023-01-01",
        "end_date": "2023-01-30"
    })
    assert get_response.status_code == 200

    delete_response = client.delete("/group_data/delete", params={
        "group_id": "test_group_id",
        "start_date": "2023-01-01",
        "end_date": "2023-01-30"
    })
    assert delete_response.status_code == 200

# Add more tests for each endpoint in data_manager_serving_app_router.py
