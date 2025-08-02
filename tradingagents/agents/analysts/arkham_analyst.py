from tradingagents.dataflows.arkham_utils import get_arkham_public_trades, format_arkham_trades

class ArkhamAnalyst:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def analyze(self, asset):
        """
        Analyzes whale activity for a given asset by fetching public trades from Arkham Exchange.
        The 'asset' parameter should be in a format like 'BTC_USDT'.
        """
        if not self.api_key or not self.api_secret:
            return "Arkham API Key or Secret not provided."
        
        # Convert asset ticker from "BTC-USD" to "BTC_USDT" format if needed
        # This is a simple assumption, a more robust mapping might be required
        pair = asset.replace("-", "_").replace("USD", "USDT")

        trades = get_arkham_public_trades(self.api_key, self.api_secret, pair)
        report = format_arkham_trades(trades)
        return report