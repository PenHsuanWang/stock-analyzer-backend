from abc import ABC, abstractmethod


class PreprocessorBase(ABC):
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
