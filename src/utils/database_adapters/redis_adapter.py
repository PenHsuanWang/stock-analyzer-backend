# utils/database_adapters/redis_adapter.py

import redis
from src.utils.database_adapters.base import AbstractDatabaseAdapter

class RedisAdapter(AbstractDatabaseAdapter):
    """
    Adapter for Redis database.

    This adapter provides an interface to interact with a Redis database,
    allowing data to be stored, retrieved, deleted, and checked for existence.
    """

    def __init__(self, host='localhost', port=6379, db=0):
        """
        Initialize the Redis client.

        :param host: Hostname of the Redis server.
        :param port: Port number of the Redis server.
        :param db: Database number to connect to.
        """
        self._redis_client = redis.StrictRedis(
            connection_pool=redis.ConnectionPool(host=host, port=port, db=db)
        )

    def set_data(self, key: str, value: str):
        """
        Store data in Redis.

        :param key: The key under which the data should be stored.
        :param value: The string data to store in Redis.
        """
        self._redis_client.set(key, value)

    def get_data(self, key: str) -> str:
        """
        Retrieve data from Redis.

        :param key: The key of the data to retrieve.
        :return: The data stored under the given key as a string. Returns None if key does not exist.
        """
        data = self._redis_client.get(key)
        return data.decode('utf-8') if data else None

    def delete_data(self, key: str) -> bool:
        """
        Delete data from Redis.

        :param key: The key of the data to delete.
        :return: True if the deletion was successful, False otherwise.
        """
        return bool(self._redis_client.delete(key))

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.

        :param key: The key to check in the database.
        :return: True if the key exists, False otherwise.
        """
        return bool(self._redis_client.exists(key))

    def keys(self, pattern: str = None) -> list:
        """
        Retrieve a list of keys from Redis matching a pattern.

        :param pattern: The pattern to match against the keys. If None, all keys will be returned.
        :return: A list of keys that match the given pattern.
        """
        return [key.decode('utf-8') for key in self._redis_client.keys(pattern=pattern or "*")]
