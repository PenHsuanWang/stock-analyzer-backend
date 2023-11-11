from fastapi.testclient import TestClient
from unittest.mock import patch
from webapp.router.data_manager_serving_app_router import router
from core.manager.data_manager import DataIOButler
import pandas as pd

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


# Add more tests for each endpoint in data_manager_serving_app_router.py
