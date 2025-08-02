import requests
import time
import hmac
import hashlib
import base64
import json

# Correct BASE_URL from the official documentation
BASE_URL = "https://arkm.com/api"

def _make_arkham_request(api_key: str, api_secret: str, method: str, path: str, body: str = ""):
    """
    Creates and sends a signed request to the Arkham API, following the official documentation.
    """
    # Expiry timestamp in microseconds (5 minutes from now)
    expires = str(int((time.time() + 300) * 1000000))
    
    # 1. Prepare the message to be signed
    message = f"{api_key}{expires}{method}{path}{body}"
    message_bytes = message.encode('utf-8')

    # 2. CRITICAL STEP: Decode the base64 API Secret before using it as the HMAC key
    try:
        secret_bytes = base64.b64decode(api_secret)
    except (TypeError, base64.binascii.Error) as e:
        print(f"Error decoding API Secret: {e}. Please ensure it is a valid base64 string.")
        return None

    # 3. Create the HMAC-SHA256 signature
    signature_digest = hmac.new(secret_bytes, message_bytes, hashlib.sha256).digest()
    
    # 4. Base64 encode the final signature for the header
    signature_b64 = base64.b64encode(signature_digest).decode('utf-8')
    
    # 5. Prepare headers as per the documentation
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Arkham-Api-Key": api_key,
        "Arkham-Expires": expires,
        "Arkham-Signature": signature_b64,
    }
    
    # 6. Make the request
    try:
        full_url = f"{BASE_URL}{path}"
        if method.upper() == "GET":
            response = requests.get(full_url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(full_url, headers=headers, data=body)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making Arkham request: {e}")
        if e.response is not None:
            print(f"Response content: {e.response.text}")
        return None

def get_arkham_public_trades(api_key: str, api_secret: str, pair: str):
    """
    Fetches recent public trades for a given pair from the Arkham Exchange API.
    This can be used as an indicator of large market activities.
    """
    # Use the /public/trades endpoint from the documentation
    request_path = f"/public/trades?pair={pair}"
    
    data = _make_arkham_request(api_key, api_secret, "GET", request_path)
    
    return data if data else []

def format_arkham_trades(transactions):
    """
    Formats the public trade data into a readable report.
    """
    if not transactions:
        return "No recent public trades found for the selected pair."

    report = "Arkham Public Trades Report:\n\n"
    # Filter for large trades, e.g., > $100,000
    large_trades = [t for t in transactions if float(t.get('size', 0)) * float(t.get('price', 0)) > 100000]

    if not large_trades:
        return "No significant public trades (> $100,000) detected recently."

    for tx in large_trades:
        trade_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(tx['time']) / 1000))
        side = tx.get('side', 'N/A').upper()
        size = float(tx.get('size', 0))
        price = float(tx.get('price', 0))
        value_usd = size * price

        color = "green" if side == "BUY" else "red"
        report += f"- **Time:** {trade_time}\n"
        report += f"- **Side:** :{color}[{side}]\n"
        report += f"- **Amount:** {size:.4f}\n"
        report += f"- **Price:** ${price:,.2f}\n"
        report += f"- **Total Value (USD):** ${value_usd:,.2f}\n"
        report += "---\n"
        
    return report