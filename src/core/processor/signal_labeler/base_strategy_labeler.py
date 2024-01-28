from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategyLabeler(ABC):
    """
    Abstract base class for strategy labelers.

    This class defines a template for creating new strategy labelers.
    Concrete implementations must override the 'apply' method.
    """

    @abstractmethod
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply the strategy labeling to the given DataFrame.

        Parameters:
        data (pd.DataFrame): The input DataFrame.

        Returns:
        pd.DataFrame: DataFrame with labeled strategy signals.
        """
        pass
