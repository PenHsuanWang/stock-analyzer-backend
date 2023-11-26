"""
The stock data transformation serving application is going to implement the logic that perform analyzed data operation, slicing, convert, etc.
Integrated with data analysis and pass forward to more advance analysis
"""

import threading
import logging
import pandas as pd

from core.processor.data_segment_extractor import DataSegmentExtractor
from core.manager.data_manager import DataIOButler, DataNotFoundError

logger = logging.getLogger(__name__)


class StockDataTransformationServingApp:
    _app_instance = None
    _app_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._app_lock:
            if cls._app_instance is None:
                cls._app_instance = super().__new__(cls)
                cls._app_instance._data_io_butler = DataIOButler()
                cls._app_instance._data_segmentation_extractor = DataSegmentExtractor()
            return cls._app_instance

    def extract_segment_data_based_on_candlestick_pattern(
            self, stock_id: str, start_date: str, end_date: str,
            days_before_pattern: int, days_after_pattern: int) -> dict[str, list[pd.DataFrame]]:
        """
        Perform data segmentation based on candlestick patterns identified in the stock data.
        For each pattern detected, this method extracts a segment of data centered around the pattern occurrence,
        considering the specified number of days before and after the pattern.

        The method returns a dictionary where each key is a pattern type, and the value is a list of DataFrames.
        Each DataFrame in the list represents a segment of data corresponding to an occurrence of the pattern.

        :param stock_id: ID of the stock.
        :param start_date: Start date for the data.
        :param end_date: End date for the data.
        :param days_before_pattern: Number of days before the pattern occurrence to include in the segment.
        :param days_after_pattern: Number of days after the pattern occurrence to include in the segment.
        :return: A dictionary with pattern types as keys and lists of DataFrame segments as values.
                 Each list contains segments of data where the corresponding pattern was identified.
        """
        try:
            analyzed_df = self._data_io_butler.get_data("analyzed_stock_data", stock_id, start_date, end_date)
            segments_based_on_candlestick_pattern = self._data_segmentation_extractor.segment_based_on_pattern(
                analyzed_df, days_before_pattern, days_after_pattern)

            return segments_based_on_candlestick_pattern

        except DataNotFoundError as e:
            logger.error(f"No analyzed data found for stock ID {stock_id} from {start_date} to {end_date}: {e}")
            raise

        except Exception as e:
            logger.exception(f"An unexpected error occurred while extracting segments: {e}")
            raise


if __name__ == "__main__":
    app = StockDataTransformationServingApp()
    try:
        segments = app.extract_segment_data_based_on_candlestick_pattern("AAPL", "2020-01-01", "2023-10-31", 7, 3)
        for pattern, list_of_df in segments.items():
            print(f"Pattern: {pattern}, num of segment: {len(list_of_df)}" )
            # print(f"Pattern: {pattern}, num of segment: {len(list_of_df)}. Data Segment:\n{list_of_df}")
    except Exception as e:
        logger.error(f"Error in segment extraction: {e}")
