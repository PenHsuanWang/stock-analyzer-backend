# utils/database_adapters/redis_adapter.py

import redis
import json

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

    def save_data(self, key: str, value: str):
        """
        Store data in Redis.

        :param key: The key under which the data should be stored.
        :param value: The string data to store in Redis.
        """
        self._redis_client.set(key, value)

    def save_batch_data(self, key: str, value: dict, data_type: str, additional_params: dict = None) -> bool:
        """
        Store multiple data items in Redis in a batch operation.

        :param key: The key under which the data should be stored.
        :param value: The data to store, expected to be a dictionary for hash data type.
        :param data_type: The type of data structure to use in Redis ('list' or 'hash').
        :param additional_params: Additional parameters required for specific operations.
        """

        with self._redis_client.pipeline() as pipe:
            try:
                if data_type == 'list':
                    pipe.lpush(key, *value)
                elif data_type == 'hash':
                    serialized_value = {field: json.dumps(val) for field, val in value.items()}
                    pipe.hmset(key, serialized_value)
                pipe.execute()
            except Exception:
                return False

        print("Store data successfully")
        return True

    def get_data(self, key: str) -> str:
        """
        Retrieve data from Redis.

        :param key: The key of the data to retrieve.
        :return: The data stored under the given key as a string. Returns None if key does not exist.
        """
        data = self._redis_client.get(key)
        return data.decode('utf-8') if data else None

    def get_batch_data(self, key: str, data_type: str, additional_params: dict = None) -> dict:
        """
        Retrieve multiple data items from Redis in a batch operation.

        :param key: The key of the data to retrieve.
        :param data_type: The type of data structure to retrieve from Redis ('hash_keys' or other).
        :param additional_params: Additional parameters required for specific operations.
        :return: A dictionary of data items.
        """
        data = {}
        if data_type == 'hash_keys':
            with self._redis_client.pipeline() as pipe:
                fields = self._redis_client.hkeys(key)
                for field in fields:
                    pipe.hget(key, field)
                values = pipe.execute()

            data = {field.decode('utf-8'): json.loads(value.decode('utf-8')) for field, value in zip(fields, values)}
        return data

    def delete_data(self, key: str) -> bool:
        """
        Delete data from Redis.

        :param key: The key of the data to delete.
        :return: True if the deletion was successful, False otherwise.
        """
        return bool(self._redis_client.delete(key))

    def delete_batch_data(self, key: str, data_type: str, additional_params: dict = None) -> bool:
        """
        Delete multiple data items from Redis in a batch operation.

        :param key: The key under which the data items are stored.
        :param data_type: The type of data structure to delete from Redis ('hash_keys' or other).
        :param additional_params: Additional parameters required for specific operations.
        :return: True if deletion was successful, False otherwise.
        """
        try:
            if data_type == 'hash_keys':
                fields = self._redis_client.hkeys(key)
                with self._redis_client.pipeline() as pipe:
                    for field in fields:
                        pipe.hdel(key, field)
                    pipe.execute()
            else:
                # Handle other data types (if applicable)
                # Example: if data_type == 'some_other_type': ...
                pass
            return True
        except Exception as e:
            print(f"Error during batch delete: {e}")
            return False

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

    def lpush(self, key: str, *values):
        """
        Prepend one or multiple values to a list.

        :param key: The key of the list.
        :param values: Values to prepend.
        """
        self._redis_client.lpush(key, *values)

    def hset(self, key: str, field: str, value: str):
        """
        Set the string value of a hash field.

        :param key: The key of the hash.
        :param field: The field within the hash.
        :param value: The value to set.
        """
        self._redis_client.hset(key, field, value)

    def hkeys(self, key: str):
        """
        Get all the fields in a hash.

        :param key: The key of the hash.
        :return: List of fields within the hash.
        """
        return [field.decode('utf-8') for field in self._redis_client.hkeys(key)]

    def hget(self, key: str, field: str) -> str:
        """
        Get the value of a hash field.

        :param key: The key of the hash.
        :param field: The field within the hash.
        :return: The value of the field.
        """
        value = self._redis_client.hget(key, field)
        return value.decode('utf-8') if value else None