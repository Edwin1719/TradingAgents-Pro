
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

        buy_order_count = len(buys)
        sell_order_count = len(sells)

        pressure_ratio = total_buy_value / total_sell_value if total_sell_value > 0 else float('inf')


        # Determine net flow color and sign
        if net_flow > 0:
            net_flow_color = 'green'
            net_flow_sign = '+'
            if pressure_ratio > 1.5 and buy_order_count > sell_order_count:
                conclusion = "The data indicates a **strong bullish sentiment**. A significant net inflow is observed, with both the volume and number of buy orders substantially exceeding sell orders. This suggests aggressive accumulation by whales, potentially signaling a near-term price increase."
            else:
                conclusion = "The data suggests a **mildly bullish sentiment**. There is a positive net inflow, but the buying pressure is not overwhelmingly dominant. This could indicate steady accumulation, but caution is still warranted."
        else:
            net_flow_color = 'red'
            net_flow_sign = ''
            if pressure_ratio < 0.66 and sell_order_count > buy_order_count:
                conclusion = "The data reveals a **strong bearish sentiment**. A significant net outflow is recorded, with selling pressure far outweighing buying pressure. The higher number of sell orders indicates widespread distribution by whales, posing a risk of a near-term price decline."
            else:
                conclusion = "The data points to a **mildly bearish sentiment**. There is a net outflow of funds, suggesting more selling than buying. However, the pressure is not extreme, indicating cautious selling or profit-taking rather than panic selling."

        # Find the largest buy and sell orders
        largest_buy_order = buys.loc[buys['value_usdt'].idxmax()] if not buys.empty else None
        largest_sell_order = sells.loc[sells['value_usdt'].idxmax()] if not sells.empty else None

        # Format the report
        report_lines = [
            f"**Whale Order Analysis ({symbol}) - Last 24 Hours**",
            "---",
            f"*   **Net Flow**: <font color='{net_flow_color}'>{net_flow_sign}${net_flow:,.2f} USDT</font>",
            f"*   **Total Buy Volume**: ${total_buy_value:,.2f} USDT",
            f"*   **Total Sell Volume**: ${total_sell_value:,.2f} USDT",
            f"*   **Buy/Sell Pressure Ratio**: {pressure_ratio:.2f}",
            f"*   **Order Count**: {buy_order_count} Buys / {sell_order_count} Sells",
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
            
        report_lines.append("\n**Analyst's Conclusion:**")
        report_lines.append(conclusion)

        report = "\n".join(report_lines)
        
        return {"whale_report": report}
