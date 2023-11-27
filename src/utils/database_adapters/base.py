# utils/database_adaptors/base.py

from abc import ABC, abstractmethod
from typing import Any, List, Optional

class AbstractDatabaseAdapter(ABC):
    """
    Abstract base class for all database adapters.
    """

    @abstractmethod
    def set_data(self, key: str, value: Any):
        """
        Store data in the database.

        :param key: The key under which the data should be stored.
        :param value: The data to store. The type of data can be any,
                      as it depends on the specific database adapter.
        """
        raise NotImplementedError

    @abstractmethod
    def get_data(self, key: str) -> Optional[Any]:
        """
        Retrieve data from the database.

        :param key: The key of the data to retrieve.
        :return: The data as a specific type, depending on the database adapter.
                 Returns None if no data is found.
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
    def keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Retrieve a list of keys from the database matching a pattern.

        :param pattern: The pattern to match. If None, all keys may be returned.
        :return: A list of keys as strings.
        """
        raise NotImplementedError
