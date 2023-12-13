from abc import ABC, abstractmethod


class DataExporter(ABC):
    """
    Abstract base class for data exporting functionalities.

    This class provides a standard interface for exporting data
    in different formats or sending it to different destinations.
    """

    @abstractmethod
    def export_data(self, *args, **kwargs) -> None:
        """
        Abstract method to export data. Implement this method in subclasses
        to handle specific data exporting logic.

        :param args: Variable length argument list.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass
