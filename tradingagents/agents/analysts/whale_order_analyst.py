
import pandas as pd
from tradingagents.dataflows.whale_order_utils import load_large_orders_data

# Translation templates
TRANSLATIONS = {
    "english": {
        "title": "**Whale Order Analysis ({symbol}) - Last 24 Hours**",
        "no_data": "*No recent large order data found.*",
        "net_flow": "*   **Net Flow**: <font color='{color}'>{sign}${value:,.2f} USDT</font>",
        "buy_volume": "*   **Total Buy Volume**: ${value:,.2f} USDT",
        "sell_volume": "*   **Total Sell Volume**: ${value:,.2f} USDT",
        "pressure_ratio": "*   **Buy/Sell Pressure Ratio**: {ratio:.2f}",
        "order_count": "*   **Order Count**: {buys} Buys / {sells} Sells",
        "largest_buy": "*   **Largest Buy Order**: {amount:.4f} at ${price:,.2f} USDT",
        "largest_sell": "*   **Largest Sell Order**: {amount:.4f} at ${price:,.2f} USDT",
        "no_buy_order": "*   **Largest Buy Order**: N/A",
        "no_sell_order": "*   **Largest Sell Order**: N/A",
        "conclusion_title": "\n**Analyst's Conclusion:**",
        "strong_bullish": "The data indicates a **strong bullish sentiment**. A significant net inflow is observed, with both the volume and number of buy orders substantially exceeding sell orders. This suggests aggressive accumulation by whales, potentially signaling a near-term price increase.",
        "mild_bullish": "The data suggests a **mildly bullish sentiment**. There is a positive net inflow, but the buying pressure is not overwhelmingly dominant. This could indicate steady accumulation, but caution is still warranted.",
        "strong_bearish": "The data reveals a **strong bearish sentiment**. A significant net outflow is recorded, with selling pressure far outweighing buying pressure. The higher number of sell orders indicates widespread distribution by whales, posing a risk of a near-term price decline.",
        "mild_bearish": "The data points to a **mildly bearish sentiment**. There is a net outflow of funds, suggesting more selling than buying. However, the pressure is not extreme, indicating cautious selling or profit-taking rather than panic selling.",
        "neutral": "The data shows a **neutral sentiment**. Buy and sell pressures are relatively balanced, with no clear dominance from either side. Whales seem to be in a holding pattern, waiting for a clearer market signal."
    },
    "chinese": {
        "title": "**巨鲸订单分析 ({symbol}) - 过去24小时**",
        "no_data": "*未找到近期大额订单数据。*",
        "net_flow": "*   **净资金流**: <font color='{color}'>{sign}${value:,.2f} USDT</font>",
        "buy_volume": "*   **总买入额**: ${value:,.2f} USDT",
        "sell_volume": "*   **总卖出额**: ${value:,.2f} USDT",
        "pressure_ratio": "*   **买卖压力比**: {ratio:.2f}",
        "order_count": "*   **订单数量**: {buys} 买单 / {sells} 卖单",
        "largest_buy": "*   **最大买单**: {amount:.4f} @ ${price:,.2f} USDT",
        "largest_sell": "*   **最大卖单**: {amount:.4f} @ ${price:,.2f} USDT",
        "no_buy_order": "*   **最大买单**: 无",
        "no_sell_order": "*   **最大卖单**: 无",
        "conclusion_title": "\n**分析师结论:**",
        "strong_bullish": "数据显示出**强烈的看涨情绪**。观察到显著的资金净流入，买入量和订单数量均远超卖单。这表明巨鲸正在积极吸筹，可能预示着近期价格上涨。",
        "mild_bullish": "数据显示出**温和的看涨情绪**。虽有资金净流入，但买入压力并未形成绝对主导。这可能意味着市场在稳定吸筹，但仍需保持谨慎。",
        "strong_bearish": "数据显示出**强烈的看跌情绪**。录得大量资金净流出，卖出压力远超买入压力。大额卖单数量较多，表明巨鲸在广泛派发，构成短期价格下跌风险。",
        "mild_bearish": "数据指向**温和的看跌情绪**。资金呈净流出状态，表明卖方力量稍强。然而，抛压并不极端，可能只是谨慎的获利了结，而非恐慌性抛售。",
        "neutral": "数据显示出**中性情绪**。买卖双方力量相对均衡，没有明确的主导方。巨鲸似乎处于观望状态，等待更清晰的市场信号。"
    }
}

class WhaleOrderAnalyst:
    def __init__(self, config=None):
        self.config = config or {}

    def analyze(self, state: dict) -> dict:
        symbol = state.get("company_of_interest")
        language = self.config.get("language", "english")
        T = TRANSLATIONS.get(language, TRANSLATIONS["english"])

        if not symbol:
            return {"whale_report": T["title"].format(symbol="N/A") + "\n\n" + T["no_data"]}

        large_orders_df = load_large_orders_data(symbol, time_window_hours=24)

        if large_orders_df.empty:
            return {"whale_report": T["title"].format(symbol=symbol) + "\n\n" + T["no_data"]}

        buys = large_orders_df[large_orders_df['type'] == 'buy']
        sells = large_orders_df[large_orders_df['type'] == 'sell']

        total_buy_value = buys['value_usdt'].sum()
        total_sell_value = sells['value_usdt'].sum()
        net_flow = total_buy_value - total_sell_value
        
        buy_order_count = len(buys)
        sell_order_count = len(sells)

        pressure_ratio = total_buy_value / total_sell_value if total_sell_value > 0 else float('inf')

        if net_flow > 0:
            net_flow_color = 'green'
            net_flow_sign = '+'
            if pressure_ratio > 1.5 and buy_order_count > sell_order_count * 1.2:
                conclusion = T["strong_bullish"]
            else:
                conclusion = T["mild_bullish"]
        elif net_flow < 0:
            net_flow_color = 'red'
            net_flow_sign = ''
            if pressure_ratio < 0.66 and sell_order_count > buy_order_count * 1.2:
                conclusion = T["strong_bearish"]
            else:
                conclusion = T["mild_bearish"]
        else:
            net_flow_color = 'gray'
            net_flow_sign = ''
            conclusion = T["neutral"]

        largest_buy_order = buys.loc[buys['value_usdt'].idxmax()] if not buys.empty else None
        largest_sell_order = sells.loc[sells['value_usdt'].idxmax()] if not sells.empty else None

        report_lines = [
            T["title"].format(symbol=symbol),
            "---",
            T["net_flow"].format(color=net_flow_color, sign=net_flow_sign, value=net_flow),
            T["buy_volume"].format(value=total_buy_value),
            T["sell_volume"].format(value=total_sell_value),
            T["pressure_ratio"].format(ratio=pressure_ratio),
            T["order_count"].format(buys=buy_order_count, sells=sell_order_count),
        ]

        if largest_buy_order is not None:
            report_lines.append(T["largest_buy"].format(amount=largest_buy_order['amount'], price=largest_buy_order['price']))
        else:
            report_lines.append(T["no_buy_order"])

        if largest_sell_order is not None:
            report_lines.append(T["largest_sell"].format(amount=largest_sell_order['amount'], price=largest_sell_order['price']))
        else:
            report_lines.append(T["no_sell_order"])
            
        report_lines.append(T["conclusion_title"])
        report_lines.append(conclusion)

        report = "\n".join(report_lines)
        
        return {"whale_report": report}
