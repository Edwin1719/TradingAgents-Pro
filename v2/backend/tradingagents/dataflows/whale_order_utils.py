
import pandas as pd
from datetime import datetime, timedelta
import os

def load_large_orders_data(symbol: str, time_window_hours: int = 24):
    """
    Loads and filters large orders for a given symbol from a CSV file within a specified time window.

    This function reads the data in chunks to efficiently handle large files.

    Args:
        symbol (str): The trading symbol, e.g., "BTC-USD".
        time_window_hours (int): The number of hours to look back for recent orders.

    Returns:
        pandas.DataFrame: A DataFrame containing the filtered large order data,
                          or an empty DataFrame if the file doesn't exist or no data is found.
    """
    # Convert symbol format "BTC-USD" to "BTC_USDT" for filename
    if symbol.endswith("-USD"):
        filename_symbol = symbol[:-4] + "_USDT"
    else:
        filename_symbol = symbol
    
    # Construct the absolute path to the data file
    # IMPORTANT: This assumes the script is run from the project root.
    # A more robust solution might involve environment variables or a config file for the base path.
    base_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "large_orders_data"))
    file_path = os.path.join(base_data_path, f"{filename_symbol}_large_orders.csv")

    if not os.path.exists(file_path):
        print(f"Warning: Data file not found at {file_path}")
        return pd.DataFrame()

    cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
    
    chunk_list = []
    
    try:
        # Read the CSV in chunks to save memory
        for chunk in pd.read_csv(file_path, chunksize=10000):
            # Convert timestamp column to datetime objects, coercing errors
            chunk['timestamp'] = pd.to_datetime(chunk['timestamp'], errors='coerce')
            
            # Drop rows where timestamp conversion failed
            chunk.dropna(subset=['timestamp'], inplace=True)
            
            # Filter the chunk for the desired time window
            filtered_chunk = chunk[chunk['timestamp'] >= cutoff_time]
            
            if not filtered_chunk.empty:
                chunk_list.append(filtered_chunk)

    except Exception as e:
        print(f"Error reading or processing file {file_path}: {e}")
        return pd.DataFrame()

    if not chunk_list:
        return pd.DataFrame()

    # Concatenate all filtered chunks into a single DataFrame
    return pd.concat(chunk_list, ignore_index=True)

