import pandas as pd
from abc import ABC, abstractmethod


class PreprocessorBase(ABC):
    def __init__(self, df: pd.DataFrame):
        """
        The case class PreprocessorBase design for all different required data convert for advance analysis

        :param df: input dataframe
        """
        self.df = df

    @abstractmethod
    def transform(self, *args, **kwargs):
        """
        implement in concrete class
        """
        raise NotImplementedError
