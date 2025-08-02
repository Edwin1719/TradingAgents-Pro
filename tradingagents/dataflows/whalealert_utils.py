
import requests
from datetime import datetime, timedelta

def get_whale_transactions(api_key, asset):
    """
    Fetches large cryptocurrency transactions from the Whale Alert API.
    """
    # Whale Alert API uses the full name for some assets
    asset_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "USDT": "tether",
        # Add other mappings as needed
    }
    
    # Default to the provided asset symbol if no mapping is found
    blockchain = asset_map.get(asset.upper(), asset.lower())
    
    # API endpoint for transactions
    url = "https://api.whale-alert.io/v1/transactions"
    
    # Set the time for the last 24 hours
    now = datetime.now()
    start_time = now - timedelta(days=1)
    start_timestamp = int(start_time.timestamp())

    params = {
        "api_key": api_key,
        "blockchain": blockchain,
        "min_value": 500000,  # Minimum value of $500,000 USD
        "start": start_timestamp,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data.get("transactions", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching whale transactions: {e}")
        return []

def format_whale_transactions(transactions):
    """
    Formats the whale transaction data into a readable report.
    """
    if not transactions:
        return "No significant whale activity detected in the last 24 hours."

    report = "Whale Transaction Report (Last 24 Hours):\n\n"
    for tx in transactions:
        timestamp = datetime.fromtimestamp(tx['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        amount_usd = tx['amount_usd']
        from_owner = tx['from']['owner']
        to_owner = tx['to']['owner']
        
        report += f"- **Time:** {timestamp}\n"
        report += f"- **Amount (USD):** ${amount_usd:,.2f}\n"
        report += f"- **From:** {from_owner}\n"
        report += f"- **To:** {to_owner}\n"
        report += "---\n"
        
    return report
