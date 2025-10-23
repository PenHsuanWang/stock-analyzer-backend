"""
The data manager is responsible for interacting with stored data in the Redis db.
This includes operations like checking data, getting data, and deleting data.
"""

import redis
import pandas as pd
import numpy as np
import json
from io import StringIO
from threading import Lock
from typing import Optional, Dict, Any

from utils.database_adapters.redis_adapter import RedisAdapter
from utils.database_adapters.base import AbstractDatabaseAdapter
from utils.storage_identifier import identifier_strategy
from core.services.metadata_service import MetadataService


class DataNotFoundError(Exception):
    """Custom exception for when data is not found in Redis."""
    pass


class DataIOButler:
    def __init__(self, adapter: AbstractDatabaseAdapter):
        """
        Initialize the data manager with a database adapter.

        :param adapter: Database adapter implementing AbstractDatabaseAdapter interface.
        """
        self.adapter = adapter
        self._lock = Lock()

    @staticmethod
    def _select_key_strategy(**kwargs):
        params_criteria_mapping = {
            frozenset(['prefix', 'stock_id', 'start_date', 'end_date']): identifier_strategy.DefaultStockDataIdentifierGenerator,
            frozenset(['prefix', 'stock_id', 'start_date', 'end_date', 'post_id']): identifier_strategy.SlicingStockDataIdentifierGenerator,
            frozenset(['group_id', 'start_date', 'end_date', 'group_df_list']): identifier_strategy.GroupDataFramesIdentifierGenerator,
            frozenset(['group_id', 'start_date', 'end_date']): identifier_strategy.GroupDataFramesIdentifierGenerator
            # add more criteria here
        }

        # make sure the order of tuple will not affect
        keys = frozenset(kwargs.keys())
        strategy_class = params_criteria_mapping.get(keys)

        if strategy_class:
            return strategy_class()  # dynamically initialization
        else:
            raise ValueError("No matching strategy found for the given criteria")

    @staticmethod
    def _with_retries(max_retries, function, *args, **kwargs):
        attempts = 0
        while attempts < max_retries:
            try:
                return function(*args, **kwargs)
            except redis.WatchError:
                attempts += 1
                if attempts == max_retries:
                    raise Exception("Max retries exceeded for operation in Redis")

    def save_data(self, data: pd.DataFrame, *args, **kwargs) -> None:
        """
        Stash the given stock data in Redis.

        :param prefix:
        :param stock_id: Stock ID from yfinance.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :param data: The dataframe containing the stock data.
        :param metadata: Optional metadata dictionary
        """
        # Extract metadata if provided
        metadata = kwargs.pop('metadata', None)
        
        storage_unit_identifier = self._select_key_strategy(**kwargs)
        key = storage_unit_identifier.generate_identifier(**kwargs)
        
        # Wrap data with metadata
        data_json = data.to_json(orient="records")
        if metadata is not None:
            # New format: wrap with metadata
            data_with_metadata = MetadataService.wrap_data_with_metadata(
                data=json.loads(data_json),
                metadata=metadata
            )
            self.adapter.save_data(key, json.dumps(data_with_metadata))
        else:
            # Legacy format: save raw data
            self.adapter.save_data(key, data_json)

    def save_dataframes_group(self, **kwargs) -> None:
        """
        Store a group of DataFrames in Redis using a dynamically selected key strategy.

        Accepts keyword arguments to define the parameters for generating the storage key and the data to store.
        """
        storage_unit_identifier = self._select_key_strategy(**kwargs)
        key = storage_unit_identifier.generate_identifier(
            group_id=kwargs['group_id'],
            start_date=kwargs['start_date'],
            end_date=kwargs['end_date']
        )

        group_df_list = kwargs['group_df_list']
        hash_data = {f'stock:{index}': df.to_json(orient='records') for index, df in enumerate(group_df_list, start=1)}

        self.adapter.save_batch_data(key, hash_data, 'hash')

    def get_dataframes_group(self, **kwargs) -> dict:
        """
        Retrieve a group of DataFrames from Redis using a dynamically selected key strategy.

        Accepts keyword arguments to define the parameters for generating the storage key.
        """
        storage_unit_identifier = self._select_key_strategy(**kwargs)
        key = storage_unit_identifier.generate_identifier(
            group_id=kwargs['group_id'],
            start_date=kwargs['start_date'],
            end_date=kwargs['end_date']
        )

        dataframes = {}
        stock_data = self.adapter.get_batch_data(key, 'hash_keys')

        for stock_id, df_json in stock_data.items():
            dataframes[stock_id] = pd.read_json(df_json, orient='records')

        return dataframes

    def check_data_exists(self, *args, **kwargs) -> bool:
        """
        Check if data for the given stock parameters exists in Redis.

        :param prefix:
        :param stock_id: ID of the stock.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :return: True if data exists, else False.
        """
        # key = self._generate_major_stock_key(**kwargs)
        storage_unit_identifier = self._select_key_strategy(**kwargs)
        key = storage_unit_identifier.generate_identifier(**kwargs)
        return self.adapter.exists(key)

    def get_data(self, *args, **kwargs) -> pd.DataFrame:
        """
        Retrieve stored stock data from Redis as a DataFrame.

        :param prefix:
        :param stock_id: ID of the stock.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :return: Stock data as a DataFrame.
        """
        # key = self._generate_major_stock_key(**kwargs)
        storage_unit_identifier = self._select_key_strategy(**kwargs)
        key = storage_unit_identifier.generate_identifier(**kwargs)
        data_json_str = self.adapter.get_data(key)

        if data_json_str is None:
            raise DataNotFoundError("No data found for the given parameters in the database.")
        
        # Extract data from potentially wrapped structure
        result = MetadataService.extract_data_and_metadata(data_json_str)
        data_array = result["data"]

        df = pd.DataFrame(data_array)
        if df.select_dtypes(include=[np.number]).map(np.isinf).any().any():
            df = df.replace([np.inf, -np.inf], np.nan)

        return df
    
    def get_data_with_metadata(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Retrieve stored stock data with metadata from Redis.

        :param prefix:
        :param stock_id: ID of the stock.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :return: Dictionary with 'data' (DataFrame) and 'metadata' keys.
        """
        storage_unit_identifier = self._select_key_strategy(**kwargs)
        key = storage_unit_identifier.generate_identifier(**kwargs)
        data_json_str = self.adapter.get_data(key)

        if data_json_str is None:
            raise DataNotFoundError("No data found for the given parameters in the database.")
        
        # Extract data and metadata
        result = MetadataService.extract_data_and_metadata(data_json_str)
        data_array = result["data"]
        
        df = pd.DataFrame(data_array)
        if df.select_dtypes(include=[np.number]).map(np.isinf).any().any():
            df = df.replace([np.inf, -np.inf], np.nan)

        return {
            "data": df,
            "metadata": result["metadata"]
        }

    def update_data(self, updated_dataframe: pd.DataFrame, *args, **kwargs) -> None:
        """
        Update the stored stock data in Redis.

        :param prefix:
        :param stock_id: Stock ID from yfinance.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :param updated_dataframe: The updated dataframe.
        """
        storage_unit_identifier = self._select_key_strategy(**kwargs)
        key = storage_unit_identifier.generate_identifier(**kwargs)
        data_json = updated_dataframe.to_json(orient="records")

        with self._lock:
            self.adapter.save_data(key, data_json)

    def delete_data(self, *args, **kwargs) -> bool:
        """
        Delete stored stock data for the given parameters from Redis.

        :param prefix:
        :param stock_id: ID of the stock.
        :param start_date: Start date for the stock data.
        :param end_date: End date for the stock data.
        :return: True if deletion was successful, else False.
        """
        # key = self._generate_major_stock_key(**kwargs)
        storage_unit_identifier = self._select_key_strategy(**kwargs)
        key = storage_unit_identifier.generate_identifier(**kwargs)
        return self.adapter.delete_data(key)

    def delete_dataframes_group(self, **kwargs) -> bool:
        """
        Delete a group of DataFrames from Redis using a dynamically selected key strategy.

        Accepts keyword arguments to define the parameters for generating the storage key.
        :return: True if deletion was successful, False otherwise.
        """
        storage_unit_identifier = self._select_key_strategy(**kwargs)
        key = storage_unit_identifier.generate_identifier(**kwargs)
        return self.adapter.delete_batch_data(key, 'hash_keys')

    # Add any additional data management methods as needed.

    def get_all_exist_data_key(self, prefix: str = None) -> list[str]:
        """
        Return keys of the exist dataset with the given prefix.
        If no prefix is provided, it returns keys without a prefix.

        :param prefix: The prefix to filter keys by.
        :return: list(keys)
        """
        if prefix is not None:
            if not prefix.strip():
                raise ValueError("Prefix cannot be empty or whitespace.")
            pattern = f"{prefix}:*"
        else:
            pattern = "*"

        return self.adapter.keys(pattern=pattern)
    
    def list_all_datasets(self, prefix_pattern: str = "stock_data:*") -> list:
        """
        List all datasets from Redis with their metadata.
        
        :param prefix_pattern: Pattern to match keys (e.g., "stock_data:*")
        :return: List of dataset summaries with metadata
        """
        datasets = []
        keys = self.adapter.keys(pattern=prefix_pattern)
        
        for key in keys:
            try:
                # Parse key: prefix:stock_id:start_date:end_date
                parts = key.split(':')
                if len(parts) != 4:
                    continue
                
                prefix, stock_id, start_date, end_date = parts
                
                # Get data
                raw_data = self.adapter.get_data(key)
                if not raw_data:
                    continue
                
                # Extract data and metadata
                result = MetadataService.extract_data_and_metadata(raw_data)
                data_array = result["data"]
                metadata = result["metadata"]
                
                datasets.append({
                    "key": key,
                    "stock_id": stock_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "record_count": len(data_array) if isinstance(data_array, list) else 0,
                    "metadata": metadata
                })
            except Exception as e:
                # Skip problematic keys
                continue
        
        return datasets


if __name__ == "__main__":
    redis_adapter = RedisAdapter()
    data_io_butler = DataIOButler(redis_adapter)

    # List all keys in Redis matching the pattern 'stock_data:*'
    keys = data_io_butler.get_all_exist_data_key()
    if not keys:
        print("No stock data keys found in Redis.")
        exit()

    for key in keys:
        print(key)

    # Just fetching data for the first key as an example
    key = keys[0]
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
