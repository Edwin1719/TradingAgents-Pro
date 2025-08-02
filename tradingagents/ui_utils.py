
import os

# Define popular assets by category
popular_assets = {
    "Cryptocurrencies": ["BTC-USD", "ETH-USD", "ADA-USD", "SOL-USD", "MATIC-USD", "DOT-USD", "AVAX-USD", "LINK-USD"],
    "Tech Stocks": ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "META", "AMZN", "NFLX"],
    "Blue Chip Stocks": ["JPM", "JNJ", "KO", "PG", "WMT", "V", "MA", "DIS"],
    "Indices": ["SPY", "QQQ", "IWM", "VTI", "GLD", "TLT", "VIX", "DXY"],
    "Custom": []
}

# From environment variables, get the default minimum order amount threshold, default is 100000
DEFAULT_MIN_AMOUNT = int(os.getenv('BINANCE_MIN_ORDER_AMOUNT', 100000))

def convert_crypto_symbol(symbol):
    """
    Converts a Yahoo Finance format cryptocurrency symbol to Binance format
    For example: BTC-USD -> BTC/USDT
    """
    if symbol.endswith('-USD'):
        base_currency = symbol[:-4]  # Remove the '-USD' suffix
        return f"{base_currency}/USDT"
    return symbol
