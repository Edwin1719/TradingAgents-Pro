
from tradingagents.dataflows.arkham_utils import get_arkham_transactions, format_arkham_transactions

class ArkhamAnalyst:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def analyze(self, asset):
        """
        Analyzes whale activity for a given asset using Arkham Intelligence.
        """
        if not self.api_key or not self.api_secret:
            return "Arkham API Key or Secret not provided."
        
        # The asset symbol (e.g., "BTC") is passed to the analysis function.
        transactions = get_arkham_transactions(self.api_key, self.api_secret, asset)
        report = format_arkham_transactions(transactions)
        return report
