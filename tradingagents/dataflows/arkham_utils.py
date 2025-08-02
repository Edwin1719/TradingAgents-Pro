import requests
import time
import hmac
import hashlib
import base64
import json

BASE_URL = "https://api.arkhamintelligence.com"

def _make_arkham_request(api_key: str, api_secret: str, method: str, path: str, body: str = ""):
    """
    Creates and sends a signed request to the Arkham API.
    """
    expires = str(int((time.time() + 300) * 1000000)) # Expiry in 5 mins, in microseconds
    
    # 1. Prepare the message to be signed
    message = f"{api_key}{expires}{method}{path}{body}"
    
    # 2. Decode the base64 API Secret and create the HMAC-SHA256 signature
    # The documentation implies the secret itself might be base64 encoded, but typically libraries
    # work with the raw secret. We will assume the secret is a standard string and encode it to bytes.
    secret_bytes = api_secret.encode('utf-8')
    message_bytes = message.encode('utf-8')
    
    signature_digest = hmac.new(secret_bytes, message_bytes, hashlib.sha256).digest()
    
    # 3. Base64 encode the signature
    signature_b64 = base64.b64encode(signature_digest).decode('utf-8')
    
    # 4. Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Arkham-Api-Key": api_key,
        "Arkham-Expires": expires,
        "Arkham-Signature": signature_b64,
    }
    
    # 5. Make the request
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

def get_arkham_transactions(api_key: str, api_secret: str, asset_symbol: str):
    """
    Fetches transactions for a given asset from the Arkham API.
    NOTE: This requires finding the Arkham-specific ID for the asset.
    The path used here is a placeholder and needs to be adapted based on API capabilities.
    """
    # For this example, we'll use the /transfers endpoint, as it's more generic.
    # A real implementation would first need to resolve the asset_symbol (e.g., "BTC")
    # to an Arkham entity or address.
    # Let's assume we are tracking a known whale address for simplicity.
    whale_address = "0x220bda5c86366978d3e38de38c75a5b5873a7117" # Example: Vitalik Buterin's address
    
    request_path = f"/transfers?address={whale_address}&chain=ethereum" # Example path
    
    data = _make_arkham_request(api_key, api_secret, "GET", request_path)
    
    return data.get("transfers", []) if data else []

def format_arkham_transactions(transactions):
    """
    Formats the Arkham transaction data into a readable report.
    """
    if not transactions:
        return "No significant whale activity detected for the tracked address."

    report = "Arkham Whale Transaction Report:\n\n"
    for tx in transactions:
        from_entity = tx.get('fromEntity', {}).get('name', tx.get('fromAddress', 'N/A'))
        to_entity = tx.get('toEntity', {}).get('name', tx.get('toAddress', 'N/A'))
        token_symbol = tx.get('token', {}).get('symbol', 'N/A')
        value_usd = tx.get('valueUSD', 0)

        report += f"- **Token:** {token_symbol}\n"
        report += f"- **Value (USD):** ${value_usd:,.2f}\n"
        report += f"- **From:** {from_entity}\n"
        report += f"- **To:** {to_entity}\n"
        report += f"- **Transaction:** [{tx.get('hash', 'N/A')}]\n"
        report += "---"
        
    return report
