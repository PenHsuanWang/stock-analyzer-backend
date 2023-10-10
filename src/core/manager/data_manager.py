"""
the data manager is responsible for interact stored data in the redis db
include the operation like check data, get data, and delete data...
"""

import redis
import pandas as pd


class DataIOButler:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """
        Initialize the data manager with a connection to the Redis server.

        :param host: Redis server hostname.
        :param port: Redis server port.
        :param db: Redis database number.
        """
        self._redis_client = redis.StrictRedis(host=host, port=port, db=db)

    def _generate_key(self, stock_id: str, start_date: str, end_date: str) -> str:
        """
        Generate a consistent Redis key based on stock information.

        :param stock_id: ID of the stock.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :return: Generated key string.
        """
        return f"stock_data:{stock_id}:{start_date}:{end_date}"

    def check_data_exists(self, stock_id: str, start_date: str, end_date: str) -> bool:
        """
        Check if data for the given stock parameters exists in Redis.

        :param stock_id: ID of the stock.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :return: True if data exists, else False.
        """
        key = self._generate_key(stock_id, start_date, end_date)
        return self._redis_client.exists(key)

    def get_data(self, stock_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Retrieve stored stock data from Redis as a DataFrame.

        :param stock_id: ID of the stock.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :return: Stock data as a DataFrame.
        """
        key = self._generate_key(stock_id, start_date, end_date)
        data_json = self._redis_client.get(key)

        if data_json is None:
            return None

        return pd.read_json(data_json, orient="records")

    def update_data(self, stock_id: str, start_date: str, end_date: str, updated_dataframe: pd.DataFrame) -> None:
        """
        Update the stored stock data in Redis.

        :param stock_id: Stock ID from yfinance.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :param updated_dataframe: The updated dataframe.
        :return: None
        """
        key = self._generate_key(stock_id, start_date, end_date)
        # Convert DataFrame to JSON and store it in Redis
        self._redis_client.set(key, updated_dataframe.to_json(orient="records"))

    def delete_data(self, stock_id: str, start_date: str, end_date: str) -> bool:
        """
        Delete stored stock data for the given parameters from Redis.

        :param stock_id: ID of the stock.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :return: True if deletion was successful, else False.
        """
        key = self._generate_key(stock_id, start_date, end_date)
        return self._redis_client.delete(key)

    # Add any additional data management methods as needed.
