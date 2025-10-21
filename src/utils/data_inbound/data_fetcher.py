from typing import Tuple

import yfinance as yf
import pandas as pd

from datetime import datetime
from requests.exceptions import HTTPError

from utils.data_inbound.base import BaseDataFetcher


class YFinanceFetcher(BaseDataFetcher):

    def __init__(self):
        super().__init__()

    @staticmethod
    def _extract_fetch_stock_and_time_range_params(*args, **kwargs) -> Tuple[str, str, str]:
        """
        Check the input parameters are valid.
        check the necessary input parameters are provided.
        check the time range is valid.
        :param args:
        :param kwargs:
        :return:
        """
        # check the input parameters are valid or raise error
        if not all(key in kwargs for key in ("stock_id", "start_date", "end_date")):
            raise ValueError("Missing input parameters")

        stock_id = kwargs["stock_id"]
        start_date = kwargs["start_date"]
        end_date = kwargs["end_date"]

        # # check the stock id is valid or not
        # try:
        #     if not yf.Ticker(stock_id).info:
        #         raise ValueError(f"Invalid stock id: {stock_id}")
        # except HTTPError:
        #     raise ValueError(f"Invalid stock id: {stock_id}")

        # check the date format match to yfinance or not
        if not isinstance(start_date, str) or not isinstance(end_date, str):
            raise ValueError("Invalid date format")
        else:
            # check the date pattern match to yfinance or not
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Invalid date format")

        # check the date range is valid or not
        if start_date > end_date:
            raise ValueError("Invalid date range")

        return stock_id, start_date, end_date

    def fetch_from_source(self, *args, **kwargs) -> None:
        """
        Fetch data from YahooFinanceFetcher.
        provided the desired stock id and date range.
        Store the fetched data in self._fetched_data temperately.
        The fetched data is in pandas dataframe format.
        :return:
        """

        stock_id, start_date, end_date = self._extract_fetch_stock_and_time_range_params(*args, **kwargs)

        # check the self._fetched_data's shape is (0, 0) or not
        # if not, raise warning

        if self._fetched_data.shape != (0, 0):
            print("Warning: self._fetched_data is not empty, "
                  "please `get_as_dataframe` to get the temporary data first, ")
        else:
            self._fetched_data = yf.download(stock_id, start_date, end_date, auto_adjust=True)
            
            # Flatten MultiIndex columns if present (when downloading single stock)
            if isinstance(self._fetched_data.columns, pd.MultiIndex):
                self._fetched_data.columns = self._fetched_data.columns.get_level_values(0)
            
            # Reset index to make Date a column
            self._fetched_data = self._fetched_data.reset_index()

    def get_as_dataframe(self, *args, **kwargs) -> pd.DataFrame:
        """
        return the fetched data in self._fetched_data
        provided desired data format.
        :param args:
        :param kwargs:
        :return:
        """
        # check the type of self._fetched_data is pandas dataframe or not
        if not self._check_fetched_data_is_valid():
            # raise error if fetched data is not valid
            # let user to handling the error from outer fetcher
            raise ValueError("Invalid fetched data format")

        # tuple unpacking to flush the data
        self._fetched_data, flush_data = pd.DataFrame(), self._fetched_data

        return flush_data


if __name__ == "__main__":

    data_fetcher = YFinanceFetcher()

    data_fetcher.fetch_from_source(stock_id="AAPL", start_date="2020-01-01", end_date="2020-12-31")
    df = data_fetcher.get_as_dataframe()

    print(df.head(10))
