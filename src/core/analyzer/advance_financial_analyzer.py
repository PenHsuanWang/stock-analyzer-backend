import logging
import pandas as pd
from stockana.calc_advance_indicator import AdvancedFinancialIndicator

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedFinancialAnalyzer:
    def __init__(self):
        pass

    @staticmethod
    def apply_advanced_analysis(stock_data: pd.DataFrame, short_window: int, long_window: int, volume_window: int) -> pd.DataFrame:
        """
        Apply advanced financial analysis on the stock data.

        :param stock_data: DataFrame with stock data.
        :param short_window: The short window period for certain indicators.
        :param long_window: The long window period for certain indicators.
        :param volume_window: The volume window period for volume-related indicators.
        :return: DataFrame with new analysis columns.
        """
        indicator = AdvancedFinancialIndicator()
        try:
            return indicator.apply_strategy(stock_data, short_window, long_window, volume_window)
        except Exception as e:
            logger.error(f"Failed to apply advanced financial analysis: {e}")
            raise
