from unittest import TestCase, mock
import pandas as pd
from core.analyzer.moving_average_analyzer import MovingAverageAnalyzer
from core.analyzer.daily_return_analyzer import DailyReturnAnalyzer
from core.analyzer.cross_asset_analyzer import CrossAssetAnalyzer
from core.manager.data_manager import DataNotFoundError

# Mocked stock data
fake_stock_data = pd.DataFrame({
    'Close': [100, 102, 101, 103, 102],
})


# Testing MovingAverageAnalyzer
class TestMovingAverageAnalyzer(TestCase):

    def setUp(self):
        self.analyzer = MovingAverageAnalyzer()
        self.fake_stock_data = pd.DataFrame({
            'Close': [100, 102, 101, 103, 102],
        })
        self.window_sizes = [3]

    def test_calculate_moving_average_success(self):
        # Perform the calculation
        result_df = self.analyzer.calculate_moving_average(
            self.fake_stock_data, self.window_sizes
        )
        # Validate the moving average calculation
        self.assertIn('MA_3_days', result_df.columns, "MA_3_days column not in DataFrame")

        # Check if the calculation is correct
        # Add the expected moving average values manually or calculate them as you would expect them to be
        expected_ma = [None, None, 101.0, 102.0, 102.0]  # Example expected values
        pd.testing.assert_series_equal(result_df['MA_3_days'], pd.Series(expected_ma, name='MA_3_days'), check_names=False)

    def test_calculate_moving_average_empty_window_sizes(self):
        # Test the situation where the window_sizes list is empty
        result_df = self.analyzer.calculate_moving_average(
            self.fake_stock_data, []
        )
        # Assert that the DataFrame is unchanged
        pd.testing.assert_frame_equal(result_df, self.fake_stock_data)


# Testing DailyReturnAnalyzer
class TestDailyReturnAnalyzer(TestCase):
    def setUp(self):
        self.analyzer = DailyReturnAnalyzer()
        self.fake_stock_data = pd.DataFrame({
            'Close': [100, 102, 101, 103, 102],
        })

    def test_calculate_daily_return_success(self):
        # Perform the calculation
        result_df = self.analyzer.calculate_daily_return(self.fake_stock_data)

        # Validate the daily return calculation
        self.assertIn('Daily_Return', result_df.columns, "Daily_Return column not in DataFrame")

        # Check if the calculation is correct
        # The first value should be 0.0 because this is the current behavior of the calculate_daily_return function
        expected_daily_return = [0.0, 0.02, -0.009803921568627416, 0.01980198019801982, -0.009708737864077666]
        # Ensure that the expected series is of dtype float64
        expected_series = pd.Series(expected_daily_return, name='Daily_Return', dtype='float64')
        pd.testing.assert_series_equal(result_df['Daily_Return'], expected_series, check_names=False)

    def test_calculate_daily_return_empty_data(self):
        # Test the situation where the data is empty
        empty_data = pd.DataFrame({'Close': []})
        result_df = self.analyzer.calculate_daily_return(empty_data)

        # Assert that the DataFrame is still empty and has a new 'Daily_Return' column
        self.assertTrue(result_df.empty)
        self.assertIn('Daily_Return', result_df.columns, "Daily_Return column should be present even in empty DataFrame")


# Mocked stock data
fake_stock_data = pd.DataFrame({
    'Close': [100, 102, 101, 103, 102],
    'Daily_Return': [0.01, -0.01, 0.02, -0.02, 0.01]
})

# Testing CrossAssetAnalyzer
class TestCrossAssetAnalyzer(TestCase):
    def setUp(self):
        self.analyzer = CrossAssetAnalyzer()
        self.stock_ids = ['AAPL', 'GOOGL']
        self.start_date = '2021-01-01'
        self.end_date = '2021-01-05'
        self.metric = 'Close'

    @mock.patch('core.manager.data_manager.DataIOButler.get_data')
    def test_calculate_correlation_success(self, mock_get_data):
        # Mock returning fake stock data for both stocks
        mock_get_data.side_effect = [fake_stock_data for _ in self.stock_ids]

        correlation_df = self.analyzer.calculate_correlation(
            self.stock_ids, self.start_date, self.end_date, self.metric
        )

        # Verify that the Redis get method has been called for each stock ID
        calls = [mock.call(stock_id, self.start_date, self.end_date) for stock_id in self.stock_ids]
        mock_get_data.assert_has_calls(calls, any_order=True)

        # Validate the correlation calculation
        # Here you should check the contents of the correlation DataFrame to ensure the correlations have been calculated correctly.

    @mock.patch('core.manager.data_manager.DataIOButler.get_data', side_effect=DataNotFoundError)
    def test_calculate_correlation_data_not_found(self, mock_get_data):
        # Test the situation where no data is found for any stock IDs

        correlation_df = self.analyzer.calculate_correlation(
            self.stock_ids, self.start_date, self.end_date, self.metric
        )

        # Instead, we can assert that the returned DataFrame is empty
        self.assertTrue(correlation_df.empty)

        # Verify that the Redis get method was called for both stock IDs
        mock_get_data.assert_any_call(self.stock_ids[0], self.start_date, self.end_date)
        mock_get_data.assert_any_call(self.stock_ids[1], self.start_date, self.end_date)

