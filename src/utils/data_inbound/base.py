import pandas as pd
from abc import ABC, abstractmethod


class BaseDataFetcher(ABC):
    """
    Abstract base class for all fetchers.
    To fetch data from the designated source.
    Implement concrete class for different data source.
    The Data Fetcher is designed as Adapter Pattern.
    For filling the gap between different data source.
    converting the data to pandas dataframe at `fetch_data` function.
    """
    def __init__(self):
        self._fetched_data = pd.DataFrame()

    @abstractmethod
    def fetch_from_source(self, *args, **kwargs) -> None:
        """
        Fetch data from the designated source.
        Organize the data to pandas dataframe.
        Store the fetched data in self._fetched_data temperately.
        In this function, provide the function to convert the data to pandas dataframe.
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def get_as_dataframe(self, *args, **kwargs) -> pd.DataFrame:
        """
        return the fetched data in self._fetched_data
        provided desired data format.
        Once the data been returned, the self._fetched_data should be empty.
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    def _check_fetched_data_is_valid(self) -> bool:
        """
        Check the fetched data is valid.
        :return:
        """
        # check the self._fetched_data's type is pandas dataframe
        # check the self._fetched_data's shape is not (0, 0)

        if isinstance(self._fetched_data, pd.DataFrame):
            if self._fetched_data.shape != (0, 0):
                return True
        return False

    def check_data_head(self) -> None:
        """
        Check the head of the fetched data.
        :return:
        """
        if not self._check_fetched_data_is_valid():
            # TODO: Use Logger to print the error message.
            print("fetch data is not valid, please check the data source.")
            return

        print(self._fetched_data.head())

    def check_data_size(self) -> None:
        """
        Check the size of the fetched data.
        :return:
        """
        if not self._check_fetched_data_is_valid():
            # TODO: Use Logger to print the error message.
            print("fetch data is not valid, please check the data source.")
            return

        print(self._fetched_data.shape)

    def check_data_columns(self) -> None:
        """
        Check the columns of the fetched data.
        :return:
        """
        if not self._check_fetched_data_is_valid():
            # TODO: Use Logger to print the error message.
            print("fetch data is not valid, please check the data source.")
            return

        print(self._fetched_data.columns)
