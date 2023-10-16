"""
The data manager is responsible for interacting with stored data in the Redis db.
This includes operations like checking data, getting data, and deleting data.
"""

import redis
import pandas as pd
import asyncio  # import asyncio


class DataNotFoundError(Exception):
    """Custom exception for when data is not found in Redis."""
    pass


class DataIOButler:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """
        Initialize the data manager with a connection to the Redis server.

        :param host: Redis server hostname.
        :param port: Redis server port.
        :param db: Redis database number.
        """
        self._redis_client = redis.StrictRedis(
            connection_pool=redis.ConnectionPool(host=host, port=port, db=db)
        )

    @staticmethod
    def _generate_key(stock_id: str, start_date: str, end_date: str) -> str:
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
        return bool(self._redis_client.exists(key))

    def get_data(self, stock_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Retrieve stored stock data from Redis as a DataFrame.

        :param stock_id: ID of the stock.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :return: Stock data as a DataFrame.
        """
        key = self._generate_key(stock_id, start_date, end_date)
        data_json_bytes = self._redis_client.get(key)

        if data_json_bytes is None:
            raise DataNotFoundError("No data found for the given stock parameters in Redis.")

        data_json_str = data_json_bytes.decode('utf-8')  # decode bytes to string
        return pd.read_json(data_json_str, orient="records")

    def update_data(self, stock_id: str, start_date: str, end_date: str, updated_dataframe: pd.DataFrame) -> None:
        """
        Update the stored stock data in Redis.

        :param stock_id: Stock ID from yfinance.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :param updated_dataframe: The updated dataframe.
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
        return bool(self._redis_client.delete(key))

    # Add any additional data management methods as needed.

    def get_all_exist_data_key(self) -> list:
        """
        return keys of the exist dataset
        :return: list(keys)
        """
        return self._redis_client.keys(pattern="stock_data:*")


if __name__ == "__main__":
    data_io_butler = DataIOButler()

    # List all keys in Redis matching the pattern 'stock_data:*'
    keys = data_io_butler.get_all_exist_data_key()
    if not keys:
        print("No stock data keys found in Redis.")
        exit()

    for key in keys:
        print(key.decode('utf-8'))

    # Just fetching data for the first key as an example
    key = keys[0].decode('utf-8')  # Convert bytes to string
    print(f"Fetching data for key: {key}")

    # Extract stock_id, start_date, and end_date from the key
    _, stock_id, start_date, end_date = key.split(":")  # Assumes the key format is consistent


    def fetch_and_print():
        try:
            # Remove await since get_data is not asynchronous
            data_frame = data_io_butler.get_data(stock_id, start_date, end_date)
            print(data_frame.head())
        except DataNotFoundError as e:
            print(str(e))


    fetch_and_print()

    keys = data_io_butler.get_all_exist_data_key()
    print(keys)

    data_io_butler.delete_data(
        stock_id="AAPL",
        start_date="2023-01-01",
        end_date="2023-10-10"
    )

    keys = data_io_butler.get_all_exist_data_key()
    print(keys)
