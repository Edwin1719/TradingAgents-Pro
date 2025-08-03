import ccxt
import pandas as pd
from datetime import datetime
import time
import logging
import os
import threading

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BinanceLargeOrdersTracker:
    def __init__(self, symbol, min_amount=100000):
        """
        初始化币安大额订单追踪器
        
        Args:
            symbol (str): 交易对, e.g., 'BTC/USDT'
            min_amount (float): 最小订单金额阈值
        """
        self.symbol = symbol
        self.min_amount = min_amount
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'adjustForTimeDifference': True
            }
        })
        self.large_orders = []
        # 为每个tracker实例创建独立的CSV文件名
        self.filename = f"{self.symbol.replace('/', '_')}_large_orders.csv"
        
    def get_order_book(self):
        """获取订单簿数据"""
        try:
            orderbook = self.exchange.fetch_order_book(self.symbol)
            return orderbook
        except Exception as e:
            logger.error(f"[{self.symbol}] 获取订单簿失败: {e}")
            return None
    
    def get_ticker(self):
        """获取当前价格"""
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"[{self.symbol}] 获取价格失败: {e}")
            return None
    
    def filter_large_orders(self, orderbook, current_price):
        """筛选大额订单"""
        large_orders = []
        current_time = datetime.now()
        
        # 处理买单 (bids)
        for price, amount in orderbook['bids']:
            order_value = price * amount
            if order_value >= self.min_amount:
                large_orders.append({
                    'timestamp': current_time,
                    'type': 'buy',
                    'price': price,
                    'amount': amount,
                    'value_usdt': order_value,
                    'current_price': current_price
                })
        
        # 处理卖单 (asks)
        for price, amount in orderbook['asks']:
            order_value = price * amount
            if order_value >= self.min_amount:
                large_orders.append({
                    'timestamp': current_time,
                    'type': 'sell',
                    'price': price,
                    'amount': amount,
                    'value_usdt': order_value,
                    'current_price': current_price
                })
        
        return large_orders
    
    def save_to_csv(self):
        """保存数据到CSV文件"""
        if self.large_orders:
            df = pd.DataFrame(self.large_orders)
            try:
                # 确保数据目录存在
                data_dir = 'large_orders_data'
                if not os.path.exists(data_dir):
                    os.makedirs(data_dir)
                
                filepath = os.path.join(data_dir, self.filename)
                
                # 如果文件存在，追加数据；否则创建新文件
                file_exists = os.path.exists(filepath)
                df.to_csv(filepath, mode='a', header=not file_exists, index=False)
                
                logger.info(f"[{self.symbol}] 保存了 {len(self.large_orders)} 条大额订单到 {filepath}")
            except Exception as e:
                logger.error(f"[{self.symbol}] 保存CSV文件失败: {e}")
        else:
            logger.info(f"[{self.symbol}] 没有大额订单需要保存")
    
    def track_orders(self, interval=60):
        """持续追踪大额订单"""
        logger.info(f"[{self.symbol}] 开始追踪大额订单 (>= {self.min_amount} USDT)")
        logger.info(f"[{self.symbol}] 检查间隔: {interval} 秒")
        
        try:
            while True:
                orderbook = self.get_order_book()
                current_price = self.get_ticker()
                
                if orderbook and current_price:
                    large_orders = self.filter_large_orders(orderbook, current_price)
                    
                    if large_orders:
                        logger.info(f"[{self.symbol}] 发现 {len(large_orders)} 个大额订单")
                        for order in large_orders:
                            logger.info(f"[{self.symbol}] {order['type'].upper()} 订单: "
                                      f"价格 {order['price']:.2f}, "
                                      f"数量 {order['amount']:.6f}, "
                                      f"价值 {order['value_usdt']:.2f} USDT")
                        
                        self.large_orders.extend(large_orders)
                        self.save_to_csv()
                        self.large_orders = []
                    else:
                        logger.info(f"[{self.symbol}] 未发现大额订单")
                
                logger.info(f"[{self.symbol}] 等待 {interval} 秒后进行下次检查...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info(f"[{self.symbol}] 程序被用户中断")
        except Exception as e:
            logger.error(f"[{self.symbol}] 程序运行出错: {e}")
        finally:
            if self.large_orders:
                self.save_to_csv()
                logger.info(f"[{self.symbol}] 程序结束，数据已保存")

def start_tracker_thread(symbol, min_amount, interval):
    """为单个资产启动追踪器线程
    
    Args:
        symbol (str): 交易对符号，例如 'BTC/USDT'
        min_amount (float): 最小订单金额阈值
        interval (int): 检查间隔（秒），默认为60秒
    """
    tracker = BinanceLargeOrdersTracker(symbol=symbol, min_amount=min_amount)
    # 使用daemon=True可让主线程退出时子线程也退出
    thread = threading.Thread(target=tracker.track_orders, args=(interval,), daemon=True)
    thread.start()
    logger.info(f"启动 {symbol} 的后台追踪线程。")
    return thread
