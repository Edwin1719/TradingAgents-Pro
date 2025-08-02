
import pandas as pd
from tradingagents.dataflows.whale_order_utils import load_large_orders_data

class WhaleOrderAnalyst:
    """
    Analyzes large whale orders to provide insights into market sentiment and potential price movements.
    """

    def analyze(self, state: dict) -> dict:
        """
        Performs the analysis of large orders for a given symbol and returns a dictionary to update the state.

        Args:
            state (dict): The current agent state, containing 'company_of_interest'.

        Returns:
            dict: A dictionary with the key "whale_report" and the analysis string as the value.
        """
        symbol = state.get("company_of_interest")
        if not symbol:
            return {"whale_report": "**Whale Order Analysis Error**: Missing symbol in agent state."}

        # Load the data using the new utility function
        large_orders_df = load_large_orders_data(symbol, time_window_hours=24)

        if large_orders_df.empty:
            return {"whale_report": f"**Whale Order Analysis ({symbol}) - Last 24 Hours**\n\n*No recent large order data found.*"}

        # Separate buys and sells
        buys = large_orders_df[large_orders_df['type'] == 'buy']
        sells = large_orders_df[large_orders_df['type'] == 'sell']

        # Calculate total values
        total_buy_value = buys['value_usdt'].sum()
        total_sell_value = sells['value_usdt'].sum()
        net_flow = total_buy_value - total_sell_value

        # Determine net flow color and sign
        if net_flow > 0:
            net_flow_color = 'green'
            net_flow_sign = '+'
        else:
            net_flow_color = 'red'
            net_flow_sign = ''

        # Find the largest buy and sell orders
        largest_buy_order = buys.loc[buys['value_usdt'].idxmax()] if not buys.empty else None
        largest_sell_order = sells.loc[sells['value_usdt'].idxmax()] if not sells.empty else None

        # Format the report
        report_lines = [
            f"**Whale Order Analysis ({symbol}) - Last 24 Hours**",
            "---",
            f"*   **Net Flow**: <font color='{net_flow_color}'>{net_flow_sign}${net_flow:,.2f} USDT</font>",
            f"*   **Total Buy Volume**: ${total_buy_value:,.2f} USDT",
            f"*   **Total Sell Volume**: ${total_sell_value:,.2f} USDT"
        ]

        if largest_buy_order is not None:
            report_lines.append(
                f"*   **Largest Buy Order**: {largest_buy_order['amount']:.4f} at ${largest_buy_order['price']:,.2f} USDT"
            )
        else:
            report_lines.append("*   **Largest Buy Order**: N/A")

        if largest_sell_order is not None:
            report_lines.append(
                f"*   **Largest Sell Order**: {largest_sell_order['amount']:.4f} at ${largest_sell_order['price']:,.2f} USDT"
            )
        else:
            report_lines.append("*   **Largest Sell Order**: N/A")
            
        report = "\n".join(report_lines)
        
        return {"whale_report": report}
