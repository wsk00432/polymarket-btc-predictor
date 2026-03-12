#!/usr/bin/env python3
"""
测试T-10秒策略触发
快速验证策略执行时机
"""

import asyncio
import time
from datetime import datetime, timedelta
import random
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_t10_strategy():
    """测试T-10秒策略"""
    print("🎯 开始测试T-10秒策略触发...")
    print(f"开始时间: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    test_duration = 600  # 测试10分钟
    start_time = time.time()
    
    while time.time() - start_time < test_duration:
        current_time = datetime.now()
        
        # 计算当前5分钟市场
        minute = current_time.minute
        remainder = minute % 5
        minutes_to_next = 5 - remainder if remainder > 0 else 0
        
        if minutes_to_next == 0:
            market_time = current_time.replace(second=0, microsecond=0)
        else:
            market_time = current_time.replace(
                minute=minute + minutes_to_next,
                second=0,
                microsecond=0
            )
        
        market_id = f"btc-5min-{market_time.hour:02d}{market_time.minute:02d}"
        window_end = market_time + timedelta(minutes=5)
        time_to_end = (window_end - current_time).total_seconds()
        
        # 检查T-10秒
        if 10 < time_to_end <= 15:
            logger.info(f"🎯 T-10秒策略触发! 市场: {market_id}")
            logger.info(f"   当前时间: {current_time.strftime('%H:%M:%S')}")
            logger.info(f"   窗口结束: {window_end.strftime('%H:%M:%S')}")
            logger.info(f"   剩余时间: {time_to_end:.1f}秒")
            
            # 模拟策略执行
            await execute_t10_strategy(market_id)
            
        # 每30秒显示一次状态
        elapsed = time.time() - start_time
        if int(elapsed) % 30 == 0:
            print(f"⏰ 已运行: {int(elapsed)}秒, 市场: {market_id}, 剩余: {time_to_end:.0f}秒")
        
        await asyncio.sleep(1)  # 1秒检查一次
    
    print()
    print("✅ 测试完成!")
    print(f"结束时间: {datetime.now().strftime('%H:%M:%S')}")

async def execute_t10_strategy(market_id: str):
    """执行T-10秒策略"""
    try:
        # 模拟BTC方向判断 (85%确定性)
        btc_direction = "UP" if random.random() > 0.15 else "DOWN"
        
        # 确定挂单价格
        if btc_direction == "UP":
            price = 0.92
            side = "YES"
        else:
            price = 0.92
            side = "NO"
        
        amount = 100
        
        # 计算预期利润
        expected_profit = (1 - price) * amount
        rebate = price * amount * 0.005  # 0.5%返佣
        total_profit = expected_profit + rebate
        
        logger.info(f"  策略执行:")
        logger.info(f"    BTC方向: {btc_direction} (85%确定性)")
        logger.info(f"    挂单方向: {side}")
        logger.info(f"    价格: ${price:.2f}")
        logger.info(f"    数量: {amount}")
        logger.info(f"    预期利润: ${expected_profit:.2f}")
        logger.info(f"    返佣: ${rebate:.2f}")
        logger.info(f"    总利润: ${total_profit:.2f}")
        
        # 模拟订单处理
        await simulate_order_processing(market_id, side, price, amount)
        
    except Exception as e:
        logger.error(f"策略执行异常: {e}")

async def simulate_order_processing(market_id: str, side: str, price: float, amount: int):
    """模拟订单处理"""
    # 模拟API调用延迟
    await asyncio.sleep(0.5)
    
    order_id = f"sim_order_{int(time.time())}"
    logger.info(f"  订单处理:")
    logger.info(f"    订单ID: {order_id}")
    logger.info(f"    状态: 已提交")
    logger.info(f"    模拟: 不会实际下单到Polymarket")
    
    # 模拟订单确认
    await asyncio.sleep(0.3)
    logger.info(f"    状态: 已确认 (模拟)")
    
    return order_id

def calculate_next_t10_time():
    """计算下一个T-10秒时间"""
    now = datetime.now()
    minute = now.minute
    remainder = minute % 5
    minutes_to_next = 5 - remainder if remainder > 0 else 0
    
    if minutes_to_next == 0:
        market_time = now.replace(second=0, microsecond=0)
    else:
        market_time = now.replace(
            minute=minute + minutes_to_next,
            second=0,
            microsecond=0
        )
    
    window_end = market_time + timedelta(minutes=5)
    t10_time = window_end - timedelta(seconds=10)
    
    return t10_time, window_end, market_time

async def main():
    """主函数"""
    print("=" * 60)
    print("🐝 T-10秒策略触发测试")
    print("=" * 60)
    
    # 计算下一个T-10秒时间
    t10_time, window_end, market_time = calculate_next_t10_time()
    market_id = f"btc-5min-{market_time.hour:02d}{market_time.minute:02d}"
    
    print(f"当前时间: {datetime.now().strftime('%H:%M:%S')}")
    print(f"下一个5分钟市场: {market_id}")
    print(f"市场开始: {market_time.strftime('%H:%M')}")
    print(f"窗口结束: {window_end.strftime('%H:%M:%S')}")
    print(f"T-10秒时间: {t10_time.strftime('%H:%M:%S')}")
    
    time_to_t10 = (t10_time - datetime.now()).total_seconds()
    if time_to_t10 > 0:
        print(f"距离T-10秒: {time_to_t10:.0f}秒")
        print()
        print(f"⏳ 等待T-10秒策略触发...")
        print(f"测试将运行10分钟，监控T-10秒策略执行")
        print("按 Ctrl+C 停止测试")
        print()
        
        # 运行测试
        await test_t10_strategy()
    else:
        print("⚠️  T-10秒时间已过，等待下一个市场")
        # 仍然运行测试，监控下一个市场
        await test_t10_strategy()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
        print("✅ T-10秒策略逻辑验证完成")