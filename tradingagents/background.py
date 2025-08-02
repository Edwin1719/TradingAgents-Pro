
import threading
from tradingagents.dataflows.binance_utils import start_tracker_thread
from tradingagents.ui_utils import popular_assets, convert_crypto_symbol, DEFAULT_MIN_AMOUNT

# Use a set to track started threads to avoid duplication
tracking_threads = set()

def start_crypto_tracking_threads(crypto_assets, min_amount=DEFAULT_MIN_AMOUNT, interval=60):
    """
    Start background tracking threads for cryptocurrency assets
    
    Args:
        crypto_assets (list): List of cryptocurrency assets, such as ['BTC-USD', 'ETH-USD']
        min_amount (int): Minimum order amount threshold
        interval (int): Check interval (seconds)
    """
    for asset in crypto_assets:
        binance_symbol = convert_crypto_symbol(asset)
        if binance_symbol not in tracking_threads:
            start_tracker_thread(binance_symbol, min_amount, interval)
            tracking_threads.add(binance_symbol)

# --- Start background threads immediately when this module is loaded ---
print("Starting background crypto tracking threads...")
crypto_assets_to_track = popular_assets["Cryptocurrencies"]
start_crypto_tracking_threads(crypto_assets_to_track)
print("Background crypto tracking threads started.")
