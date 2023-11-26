# utils/database_adaptors/base.py

from abc import ABC, abstractmethod


class AbstractDatabaseAdapter(ABC):
    """
    Abstract base class for all database adapters.
    """

    @abstractmethod
    def set_data(self, key: str, value: str):
        """
        Store data in the database.

        :param key: The key under which the data should be stored.
        :param value: The data to store.
        """
        raise NotImplementedError

    @abstractmethod
    def get_data(self, key: str) -> str:
        """
        Retrieve data from the database.

        :param key: The key of the data to retrieve.
        :return: The data as a string.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_data(self, key: str) -> bool:
        """
        Delete data from the database.

        :param key: The key of the data to delete.
        :return: True if deletion was successful, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the database.

        :param key: The key to check.
        :return: True if the key exists, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def keys(self, pattern: str = None) -> list:
        """
        Retrieve a list of keys from the database matching a pattern.

        :param pattern: The pattern to match.
        :return: A list of keys.
        """
        raise NotImplementedError
