import pytest
import pandas as pd
import numpy as np
from src.core.processor.data_convertor.time_series_preprocessor import TimeSeriesPreprocessor


@pytest.fixture
def sample_dataframe():
    data = {
        'Open': np.random.rand(10),
        'High': np.random.rand(10),
        'Low': np.random.rand(10),
        'Close': np.random.rand(10)
    }
    return pd.DataFrame(data)

def test_window_size(sample_dataframe):
    window_size = 3
    transformed_data = TimeSeriesPreprocessor.transform(sample_dataframe, window_size, ['Open', 'Close'])

    for key, series in transformed_data.items():
        assert all([len(window) == window_size for window in series])

def test_selected_columns(sample_dataframe):
    selected_columns = ['Open', 'Close']
    window_size = 3
    transformed_data = TimeSeriesPreprocessor.transform(sample_dataframe, window_size, selected_columns)

    assert set(transformed_data.keys()) == set(selected_columns)

def test_window_content(sample_dataframe):
    window_size = 3
    transformed_data = TimeSeriesPreprocessor.transform(sample_dataframe, window_size, ['Open'])

    for window in transformed_data['Open']:
        assert len(window) == window_size
        assert type(window) == np.ndarray