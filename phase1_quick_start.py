#!/usr/bin/env python3
"""
Polymarket Maker Bot - Phase 1: Quick Start
基于2026年新规则的快速启动方案

核心功能：
1. WebSocket实时连接
2. 手续费感知订单签名
3. 基础撤单/重下循环
4. 5分钟市场策略原型
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib
import hmac
from decimal import Decimal
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PolymarketMakerBot:
    """Polymarket Maker机器人核心类"""
    
    def __init__(self, private_key: str, wallet_address: str):
        """
        初始化机器人
        
        Args:
            private_key: 私钥（用于签名）
            wallet_address: 钱包地址
        """
        self.private_key = private_key
        self.wallet_address = wallet_address
        self.session: Optional[aiohttp.ClientSession] = None
        
        # WebSocket连接
        self.binance_ws = None
        self.polymarket_ws = None
        
        # 状态跟踪
        self.active_orders: Dict[str, Dict] = {}  # order_id -> order_info
        self.current_prices: Dict[str, float] = {}  # market_id -> price
        self.fee_rates: Dict[str, int] = {}  # token_id -> fee_rate_bps
        
        # 性能监控
        self.latency_stats = {
            'cancel_replace_cycles': [],
            'ws_messages': 0,
            'errors': 0
        }
        
        logger.info(f"Polymarket Maker Bot初始化完成 - 钱包: {wallet_address[:10]}...")
    
    async def initialize(self):
        """初始化连接和会话"""
        self.session = aiohttp.ClientSession()
        logger.info("HTTP会话初始化完成")
    
    async def get_fee_rate(self, token_id: str) -> int:
        """
        查询手续费率
        
        Args:
            token_id: 代币ID
            
        Returns:
            fee_rate_bps: 手续费率（基点）
            
        注意：永远不要硬编码手续费率！
        """
        try:
            url = f"https://clob.polymarket.com/fee-rate?tokenID={token_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    fee_rate = data.get('feeRateBps', 150)  # 默认150bps (1.5%)
                    self.fee_rates[token_id] = fee_rate
                    logger.info(f"获取手续费率成功 - Token: {token_id}, 费率: {fee_rate}bps")
                    return fee_rate
                else:
                    logger.warning(f"获取手续费率失败: {response.status}")
                    return 150  # 默认值
        except Exception as e:
            logger.error(f"获取手续费率异常: {e}")
            return 150  # 默认值
    
    def sign_order(self, order_data: Dict) -> Dict:
        """
        订单签名（必须包含feeRateBps字段）
        
        Args:
            order_data: 订单数据
            
        Returns:
            签名后的订单
            
        注意：这是简化版本，实际需要完整的签名逻辑
        """
        # 确保包含feeRateBps字段
        if 'feeRateBps' not in order_data:
            token_id = order_data.get('tokenId', '')
            fee_rate = self.fee_rates.get(token_id, 150)
            order_data['feeRateBps'] = str(fee_rate)
        
        # 添加其他必要字段
        order_data.update({
            'salt': str(int(time.time() * 1000)),
            'maker': self.wallet_address,
            'signer': self.wallet_address,
            'expiration': str(int((time.time() + 3600) * 1000)),  # 1小时过期
        })
        
        # 这里应该使用私钥进行实际签名
        # 简化版本：返回带签名字段的订单
        order_data['signature'] = '0x' + '0' * 130  # 占位符
        
        logger.info(f"订单签名完成 - Token: {order_data.get('tokenId', 'unknown')}")
        return order_data
    
    async def place_maker_order(self, market_id: str, side: str, price: float, amount: int) -> Optional[str]:
        """
        挂maker单
        
        Args:
            market_id: 市场ID
            side: 方向 (YES/NO)
            price: 价格 (0-1)
            amount: 数量
            
        Returns:
            order_id: 订单ID
        """
        try:
            # 1. 获取市场信息
            market_info = await self.get_market_info(market_id)
            if not market_info:
                logger.error(f"无法获取市场信息: {market_id}")
                return None
            
            token_id = market_info.get('tokenId')
            
            # 2. 查询手续费率
            fee_rate = await self.get_fee_rate(token_id)
            
            # 3. 构建订单数据
            order_data = {
                'tokenId': token_id,
                'makerAmount': str(int(amount * price * 1e6)),  # 转换为USDC单位
                'takerAmount': str(int(amount * 1e6)),  # 转换为USDC单位
                'side': 'BUY' if side == 'YES' else 'SELL',
                'feeRateBps': str(fee_rate),
            }
            
            # 4. 签名订单
            signed_order = self.sign_order(order_data)
            
            # 5. 提交订单
            order_id = await self.submit_order(signed_order)
            
            if order_id:
                self.active_orders[order_id] = {
                    'market_id': market_id,
                    'side': side,
                    'price': price,
                    'amount': amount,
                    'timestamp': time.time(),
                    'fee_rate': fee_rate,
                }
                logger.info(f"挂单成功 - 市场: {market_id}, 方向: {side}, 价格: {price}, 数量: {amount}")
            
            return order_id
            
        except Exception as e:
            logger.error(f"挂单失败: {e}")
            return None
    
    async def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        try:
            # 调用Polymarket取消API
            url = f"https://clob.polymarket.com/orders/{order_id}/cancel"
            async with self.session.post(url) as response:
                if response.status == 200:
                    if order_id in self.active_orders:
                        del self.active_orders[order_id]
                    logger.info(f"取消订单成功: {order_id}")
                    return True
                else:
                    logger.warning(f"取消订单失败: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"取消订单异常: {e}")
            return False
    
    async def cancel_replace_cycle(self, market_id: str, new_price: float) -> float:
        """
        撤单/重下循环
        
        Args:
            market_id: 市场ID
            new_price: 新价格
            
        Returns:
            cycle_time: 循环耗时（毫秒）
        """
        start_time = time.time()
        
        try:
            # 1. 取消该市场的所有活跃订单
            orders_to_cancel = []
            for order_id, order_info in self.active_orders.items():
                if order_info['market_id'] == market_id:
                    orders_to_cancel.append(order_id)
            
            # 批量取消
            cancel_tasks = [self.cancel_order(order_id) for order_id in orders_to_cancel]
            cancel_results = await asyncio.gather(*cancel_tasks, return_exceptions=True)
            
            # 2. 查询最新手续费
            market_info = await self.get_market_info(market_id)
            if market_info:
                token_id = market_info.get('tokenId')
                fee_rate = await self.get_fee_rate(token_id)
                
                # 3. 重新挂单（示例：在YES和NO两侧都挂单）
                # 这里应该根据策略决定挂单方向和价格
                amount = 100  # 默认数量
                
                # 挂YES单
                await self.place_maker_order(
                    market_id=market_id,
                    side='YES',
                    price=new_price,
                    amount=amount
                )
                
                # 挂NO单
                await self.place_maker_order(
                    market_id=market_id,
                    side='NO',
                    price=1 - new_price,  # NO价格 = 1 - YES价格
                    amount=amount
                )
            
            cycle_time = (time.time() - start_time) * 1000  # 转换为毫秒
            self.latency_stats['cancel_replace_cycles'].append(cycle_time)
            
            if cycle_time > 200:
                logger.warning(f"撤单/重下循环较慢: {cycle_time:.1f}ms")
            else:
                logger.info(f"撤单/重下循环完成: {cycle_time:.1f}ms")
            
            return cycle_time
            
        except Exception as e:
            logger.error(f"撤单/重下循环异常: {e}")
            return -1
    
    async def get_market_info(self, market_id: str) -> Optional[Dict]:
        """获取市场信息"""
        try:
            url = f"https://gamma-api.polymarket.com/condition/{market_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"获取市场信息异常: {e}")
            return None
    
    async def submit_order(self, signed_order: Dict) -> Optional[str]:
        """提交订单到Polymarket"""
        try:
            url = "https://clob.polymarket.com/orders"
            async with self.session.post(url, json=signed_order) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('id')
                else:
                    logger.warning(f"提交订单失败: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"提交订单异常: {e}")
            return None
    
    async def monitor_5min_markets(self):
        """监控5分钟市场"""
        logger.info("开始监控5分钟市场...")
        
        while True:
            try:
                current_time = datetime.now()
                
                # 计算下一个5分钟市场的时间
                minute = current_time.minute
                remainder = minute % 5
                minutes_to_next = 5 - remainder if remainder > 0 else 0
                
                if minutes_to_next == 0:
                    # 当前就是5分钟边界
                    market_time = current_time.replace(second=0, microsecond=0)
                else:
                    # 计算下一个5分钟边界
                    market_time = current_time.replace(
                        minute=minute + minutes_to_next,
                        second=0,
                        microsecond=0
                    )
                
                # 市场ID格式: btc-5min-HHMM
                market_id = f"btc-5min-{market_time.hour:02d}{market_time.minute:02d}"
                
                # 计算窗口结束时间
                window_end = market_time + timedelta(minutes=5)
                time_to_end = (window_end - current_time).total_seconds()
                
                logger.info(f"当前市场: {market_id}, 窗口结束: {window_end}, 剩余: {time_to_end:.0f}秒")
                
                # 在T-10秒时执行策略
                if 10 < time_to_end <= 15:  # 提前一点开始准备
                    logger.info(f"市场 {market_id} 即将结束 (T-{time_to_end:.0f}秒)")
                    await self.execute_t_minus_10_strategy(market_id, window_end)
                
                # 等待1秒后继续检查
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"监控5分钟市场异常: {e}")
                await asyncio.sleep(5)
    
    async def execute_t_minus_10_strategy(self, market_id: str, window_end: datetime):
        """
        执行T-10秒策略
        
        根据文章：在窗口结束前10秒，BTC方向已有85%确定性
        但Polymarket赔率尚未完全反映
        """
        try:
            # 1. 获取当前BTC价格趋势（简化：随机模拟）
            # 实际应该连接Binance WebSocket分析
            import random
            btc_direction = "UP" if random.random() > 0.15 else "DOWN"  # 85%确定性
            
            # 2. 确定挂单价格
            if btc_direction == "UP":
                price = 0.92  # 0.90-0.95美元范围
                side = "YES"
            else:
                price = 0.92
                side = "NO"
            
            # 3. 挂maker单
            amount = 100  # 合约数量
            order_id = await self.place_maker_order(market_id, side, price, amount)
            
            if order_id:
                logger.info(f"T-10秒策略执行成功 - 市场: {market_id}, 方向: {side}, 价格: {price}")
                
                # 计算预期利润
                expected_profit = (1 - price) * amount  # 结算时每份合约获得(1-price)美元
                logger.info(f"预期利润: ${expected_profit:.2f} + 返佣")
            else:
                logger.warning(f"T-10秒策略执行失败 - 市场: {market_id}")
                
        except Exception as e:
            logger.error(f"执行T-10秒策略异常: {e}")
    
    async def connect_binance_websocket(self):
        """连接Binance WebSocket获取BTC价格"""
        try:
            # Binance BTCUSDT价格流
            ws_url = "wss://stream.binance.com:9443/ws/btcusdt@trade"
            
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(ws_url) as ws:
                    logger.info("Binance WebSocket连接成功")
                    
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            try:
                                data = json.loads(msg.data)
                                price = float(data['p'])
                                self.current_prices['BTCUSDT'] = price
                                
                                # 更新性能统计
                                self.latency_stats['ws_messages'] += 1
                                
                                # 每100条消息记录一次
                                if self.latency_stats['ws_messages'] % 100 == 0:
                                    logger.info(f"Binance价格更新: ${price:.2f}, 消息数: {self.latency_stats['ws_messages']}")
                                    
                            except Exception as e:
                                logger.error(f"解析Binance消息异常: {e}")
                        
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logger.error("Binance WebSocket错误")
                            break
                            
        except Exception as e:
            logger.error(f"连接Binance WebSocket异常: {e}")
    
    async def connect_polymarket_websocket(self):
        """连接Polymarket WebSocket获取订单簿"""
        try:
            # Polymarket订单簿流（简化示例）
            ws_url = "wss://clob.polymarket.com/ws"
            
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(ws_url) as ws:
                    logger.info("Polymarket WebSocket连接成功")
                    
                    # 订阅消息
                    subscribe_msg = {
                        "type": "subscribe",
                        "channel": "orderbook",
                        "id": "btc-5min-markets"
                    }
                    await ws.send_json(subscribe_msg)
                    
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            try:
                                data = json.loads(msg.data)
                                # 处理订单簿更新
                                # 这里应该更新本地订单簿状态
                                
                                # 更新性能统计
                                self.latency_stats['ws_messages'] += 1
                                
                            except Exception as e:
                                logger.error(f"解析Polymarket消息异常: {e}")
                        
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logger.error("Polymarket WebSocket错误")
                            break
                            
        except Exception as e:
            logger.error(f"连接Polymarket WebSocket异常: {e}")
    
    async def run_performance_monitor(self):
        """运行性能监控"""
        while True:
            try:
                await asyncio.sleep(60)  # 每分钟报告一次
                
                # 计算平均循环时间
                cycles = self.latency_stats['cancel_replace_cycles']
                if cycles:
                    avg_cycle = sum(cycles) / len(cycles)
                    max_cycle = max(cycles)
                    min_cycle = min(cycles)
                else:
                    avg_cycle = max_cycle = min_cycle = 0
                
                # 性能报告
                report = f"""
                ⚡ 性能报告 ⚡
                时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                ----------------------------
                WebSocket消息: {self.latency_stats['ws_messages']}
                活跃订单: {len(self.active_orders)}
                撤单/重下循环:
                  • 平均: {avg_cycle:.1f}ms
                  • 最快: {min_cycle:.1f}ms
                  • 最慢: {max_cycle:.1f}ms
                  • 次数: {len(cycles)}
                ----------------------------
                """
                logger.info(report