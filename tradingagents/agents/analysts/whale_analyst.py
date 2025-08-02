
from tradingagents.dataflows.whalealert_utils import get_whale_transactions, format_whale_transactions

class WhaleAnalyst:
    def __init__(self, api_key):
        self.api_key = api_key

    def analyze(self, asset):
        """
        Analyzes whale activity for a given asset.
        """
        transactions = get_whale_transactions(self.api_key, asset)
        report = format_whale_transactions(transactions)
        return report
