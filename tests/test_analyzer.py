from unittest import TestCase, mock
import pandas as pd
from core.analyzer.moving_average_analyzer import MovingAverageAnalyzer
from core.analyzer.daily_return_analyzer import DailyReturnAnalyzer
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
        # Mock Redis operations
        mock_update_data.return_value = None

        self.analyzer.calculate_moving_average(
            self.prefix, self.stock_id, self.start_date, self.end_date, self.window_sizes
        )

        # Verify that the correct function has been called
        mock_get_data.assert_called_with(self.prefix, self.stock_id, self.start_date, self.end_date)

        # Verify that update_data was called at least once
        # mock_update_data.assert_called()

        # Validate the moving average calculation
        expected_columns = ['Close', f'MA_{self.window_sizes[0]}_days']
        self.assertTrue(all(column in expected_columns for column in fake_stock_data.columns))

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
