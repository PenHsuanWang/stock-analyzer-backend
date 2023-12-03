import requests
import pandas as pd
import numpy as np

import json

# Define base URL for the FastAPI server
BASE_URL = "http://localhost:8000"

def save_dataframes_group(group_id, start_date, end_date, group_df_list):
    endpoint = f"{BASE_URL}/group_data/save"
    data = {
        "group_id": group_id,
        "start_date": start_date,
        "end_date": end_date,
        "group_df_list": [df.to_dict(orient='records') for df in group_df_list]
    }
    print("check request data:")
    print(data)
    response = requests.post(endpoint, json=data)
    print("check response json")
    print(response.json())

def get_dataframes_group(group_id, start_date, end_date):
    endpoint = f"{BASE_URL}/group_data/get"
    params = {
        "group_id": group_id,
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.get(endpoint, params=params)
    group_data = response.json()

    if 'dataframes_group' in group_data:
        return {k: pd.DataFrame(v) for k, v in group_data['dataframes_group'].items()}
    else:
        return {}

def delete_dataframes_group(group_id, start_date, end_date):
    endpoint = f"{BASE_URL}/group_data/delete"
    params = {
        "group_id": group_id,
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.delete(endpoint, params=params)
    return response.json()


# Example usage
if __name__ == "__main__":
    group_id = "my_group_001"
    start_date = "2023-01-01"
    end_date = "2023-01-30"
    date_range = pd.date_range(start=start_date, end=end_date)
    num_stocks = 5

    # Generate sample group data
    group_df_list = [pd.DataFrame(np.random.randn(len(date_range), 4), columns=list('ABCD'), index=date_range) for _ in range(num_stocks)]

    # Save group data
    save_dataframes_group(group_id, start_date, end_date, group_df_list)

    # Get group data
    retrieved_group = get_dataframes_group(group_id, start_date, end_date)
    if retrieved_group:
        print(f"Retrieved group data for {group_id}:")
        for key, df in retrieved_group.items():
            print(f"Data for {key}:")
            print(df.head())
    else:
        print(f"No group data found for {group_id}.")

    # Delete group data
    delete_response = delete_dataframes_group(group_id, start_date, end_date)
    print("Delete response:", delete_response)

    # Verify deletion
    try:
        retrieved_group = get_dataframes_group(group_id, start_date, end_date)
        if not retrieved_group:
            print(f"Group data for {group_id} has been successfully deleted.")
        else:
            print(f"Data for {group_id} after deletion:")
            print(retrieved_group)
    except Exception as e:
        print(f"Error during deletion verification: {e}")