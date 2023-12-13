# test_http_data_sender.py
import pandas as pd
from src.utils.data_outbound.http_data_sender import HTTPDataSender
from unittest.mock import patch


@patch('requests.request')
def test_http_data_sender(mock_request):
    test_data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    test_url = "http://example.com"
    test_method = "POST"

    sender = HTTPDataSender()
    sender.export_data(test_data, test_url, test_method)

    # check the request method invoked
    mock_request.assert_called_once_with(
        test_method, test_url, json={"data": test_data.to_json()}
    )
