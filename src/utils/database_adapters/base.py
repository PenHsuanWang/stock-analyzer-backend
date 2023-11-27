# utils/database_adaptors/base.py

from abc import ABC, abstractmethod


class AbstractDatabaseAdapter(ABC):
    """
    Abstract base class for all database adapters.
    """

    @abstractmethod
    def set_data(self, *args, **kwargs):
        """
        Store data in the database.
        Accepts any number of arguments and keyword arguments.
        """
        raise NotImplementedError

    @abstractmethod
    def get_data(self, *args, **kwargs):
        """
        Retrieve data from the database.
        Accepts any number of arguments and keyword arguments.
        :return: Data from the database, format and type may vary.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_data(self, *args, **kwargs) -> bool:
        """
        Delete data from the database.
        Accepts any number of arguments and keyword arguments.
        :return: True if deletion was successful, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def exists(self, *args, **kwargs) -> bool:
        """
        Check if a key exists in the database.
        Accepts any number of arguments and keyword arguments.
        :return: True if the key exists, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def keys(self, *args, **kwargs):
        """
        Retrieve a list of keys from the database matching a pattern.
        Accepts any number of arguments and keyword arguments.
        :return: A list of keys, format may vary.
        """
        raise NotImplementedError
