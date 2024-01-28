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

        if not all(column in stock_data.columns for column in ["Open", "High", "Low", "Close", "Volume"]):
            raise ValueError("Input Dataframe missing necessary column")

        indicator = AdvancedFinancialIndicator()

        try:
            stock_data['MACD'], stock_data["Signal_Line"], stock_data['MACD_Histogram'] = indicator.compute_macd(stock_data, short_window, long_window)
            stock_data['Bollinger_Upper'], stock_data['Bollinger_Mid'], stock_data['bollinger_Lower'] = indicator.compute_bollinger_bands(stock_data, volume_window, column='Close')
            stock_data['RSI'] = indicator.compute_rsi(stock_data, column='Close')

            return stock_data
        except Exception as e:
            logger.error(f"Failed to apply advanced financial analysis: {e}")
            raise


        # try:
        #     return indicator.apply_strategy(stock_data, short_window, long_window, volume_window)
        # except Exception as e:
        #     logger.error(f"Failed to apply advanced financial analysis: {e}")
        #     raise
