from abc import ABC, abstractmethod


class PreprocessorBase(ABC):
    """
    The base class for all data preprocessing modules in the project.

    This abstract class defines the basic structure and required method `transform`
    that all derived preprocessing classes should implement. The purpose of this class
    is to provide a consistent interface for different data transformation tasks
    across the project.
    """

    def __init__(self):
        """
        The base class PreprocessorBase design for all different required data convert for advance analysis
        """
        pass

    @abstractmethod
    def transform(self, *args, **kwargs):
        """
        Implement in concrete class. This method should be defined to handle the transformation.
        """
        raise NotImplementedError
