import pandas as pd
import numpy as np

from src.utils.database_adapters.redis_adapter import RedisAdapter
from src.core.manager.data_manager import DataIOButler

# Initialize RedisAdapter
redis_adapter = RedisAdapter(host='localhost', port=6379, db=0)

# Initialize DataIOButler with RedisAdapter
data_io_butler = DataIOButler(redis_adapter)

# Generate sample data
group_id = "my_etf_001"
stock_ids = [f"company_{i}" for i in range(1, 31)]
date_range = pd.date_range(start="2023-01-01", end="2023-01-30")
dataframes_group = [pd.DataFrame(np.random.randn(len(date_range), 4), columns=list('ABCD'), index=date_range) for _ in stock_ids]

# Use save_dataframes_group() to store stock group data in Redis
data_io_butler.save_dataframes_group(
    group_id=group_id,
    start_date="2023-01-01",
    end_date="2023-01-30",
    group_df_list=dataframes_group
)

# Use get_dataframes_group() to retrieve stock group data from Redis
try:
    retrieved_dataframes_group = data_io_butler.get_dataframes_group(
        group_id=group_id,
        start_date="2023-01-01",
        end_date="2023-01-30"
    )

    print("Check the fetched data group contains dictionary")
    print(retrieved_dataframes_group)

    # # Display some of the retrieved data
    # for stock_id, df in retrieved_dataframes_group.items():
    #     print(f"Data for {stock_id}:\n{df.head()}\n")

except Exception as e:
    print(f"Error retrieving group data: {e}")

# Use delete_dataframes_group() to delete stock group data from Redis
try:
    delete_success = data_io_butler.delete_dataframes_group(
        group_id=group_id,
        start_date="2023-01-01",
        end_date="2023-01-30"
    )

    if delete_success:
        print(f"Data for group {group_id} successfully deleted from Redis.")
    else:
        print(f"Failed to delete data for group {group_id}.")

except Exception as e:
    print(f"Error deleting group data: {e}")


# try to get data again to make sure the data has been deleted

try:
    retrieved_dataframes_group = data_io_butler.get_dataframes_group(
        group_id=group_id,
        start_date="2023-01-01",
        end_date="2023-01-30"
    )

    print("Check the fetched data group contains dictionary")
    print(retrieved_dataframes_group)

    # Display some of the retrieved data
    for stock_id, df in retrieved_dataframes_group.items():
        print(f"Data for {stock_id}:\n{df.head()}\n")

except Exception as e:
    print(f"Error retrieving group data: {e}")

