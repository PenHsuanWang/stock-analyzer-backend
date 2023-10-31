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
        self.prefix = 'test'
        self.stock_id = 'AAPL'
        self.start_date = '2021-01-01'
        self.end_date = '2021-01-05'
        self.window_sizes = [3]

    @mock.patch('core.manager.data_manager.DataIOButler.get_data')
    @mock.patch('core.manager.data_manager.DataIOButler.update_data')
    def test_calculate_moving_average_success(self, mock_update_data, mock_get_data):
        # Mock returning fake stock data
        mock_get_data.return_value = fake_stock_data
        # Perform the calculation
        self.analyzer.calculate_moving_average(
            self.prefix, self.stock_id, self.start_date, self.end_date, self.window_sizes
        )
        # Verify that the Redis get and update methods have been called
        mock_get_data.assert_called_with(self.prefix, self.stock_id, self.start_date, self.end_date)
        # mock_update_data.assert_called()

        # Validate the moving average calculation
        # Here you should also check the contents of the DataFrame to ensure the moving average has been calculated correctly.

    @mock.patch('core.manager.data_manager.DataIOButler.get_data', side_effect=DataNotFoundError)
    def test_calculate_moving_average_data_not_found(self, mock_get_data):
        # Call the method, which is expected to handle DataNotFoundError internally
        self.analyzer.calculate_moving_average(
            self.prefix, self.stock_id, self.start_date, self.end_date, self.window_sizes
        )

        # Instead of checking for an exception, verify the behavior, such as a log message
        # For example, if you're logging an error when this happens, check that the logger was called
        # mock_logger.error.assert_called_once_with(expected_message)

        # Verify that the Redis get method was called
        mock_get_data.assert_called_with(self.prefix, self.stock_id, self.start_date, self.end_date)

    @mock.patch('core.manager.data_manager.DataIOButler.get_data')
    def test_calculate_moving_average_empty_window_sizes(self, mock_get_data):
        # Test the situation where the window_sizes list is empty
        mock_get_data.return_value = fake_stock_data
        with mock.patch('core.analyzer.moving_average_analyzer.logger') as mock_logger:
            self.analyzer.calculate_moving_average(
                self.prefix, self.stock_id, self.start_date, self.end_date, []
            )
            # Assert that a warning was logged
            mock_logger.warning.assert_called_with("No window sizes provided for moving average calculation.")
            # Assert that Redis update_data was not called since there's nothing to calculate and update
            # mock_update_data.assert_not_called()


# Testing DailyReturnAnalyzer
class TestDailyReturnAnalyzer(TestCase):
    def setUp(self):
        self.analyzer = DailyReturnAnalyzer()
        self.prefix = 'test'
        self.stock_id = 'AAPL'
        self.start_date = '2021-01-01'
        self.end_date = '2021-01-05'

    @mock.patch('core.manager.data_manager.DataIOButler.get_data')
    @mock.patch('core.manager.data_manager.DataIOButler.save_data')
    def test_calculate_daily_return_success(self, mock_save_data, mock_get_data):
        # Mock returning fake stock data
        mock_get_data.return_value = fake_stock_data
        # Mock Redis operation
        mock_save_data.return_value = None

        self.analyzer.calculate_daily_return(
            self.prefix, self.stock_id, self.start_date, self.end_date
        )

        # Verify that the correct function has been called
        mock_get_data.assert_called_with(self.prefix, self.stock_id, self.start_date, self.end_date)
        mock_save_data.assert_called()

        # Validate the daily return calculation
        self.assertTrue('Daily_Return' in fake_stock_data.columns)

    @mock.patch('core.manager.data_manager.DataIOButler.get_data', side_effect=DataNotFoundError)
    def test_calculate_daily_return_data_not_found(self, mock_get_data):
        # Test the situation where no data is found in Redis
        with self.assertRaises(DataNotFoundError):
            self.analyzer.calculate_daily_return(
                self.prefix, self.stock_id, self.start_date, self.end_date
            )


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

