# utils/database_adaptors/redis_adaptor.py

import redis
from utils.database_adaptors.base import AbstractDatabaseAdapter


class RedisAdapter(AbstractDatabaseAdapter):
    def __init__(self, host='localhost', port=6379, db=0):
        self._redis_client = redis.StrictRedis(
            connection_pool=redis.ConnectionPool(host=host, port=port, db=db)
        )

    def set_data(self, key: str, value: str):
        self._redis_client.set(key, value)

    def get_data(self, key: str) -> str:
        data = self._redis_client.get(key)
        return data.decode('utf-8') if data else None

    def delete_data(self, key: str) -> bool:
        return bool(self._redis_client.delete(key))

    def exists(self, key: str) -> bool:
        return bool(self._redis_client.exists(key))

    def keys(self, pattern: str = None) -> list:
        return [key.decode('utf-8') for key in self._redis_client.keys(pattern=pattern or "*")]
