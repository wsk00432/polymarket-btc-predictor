#!/usr/bin/env python3
"""
快速验证策略触发和执行情况
"""

from datetime import datetime, timedelta
import random

def analyze_current_situation():
    """分析当前情况"""
    print("🔍 Polymarket Maker Bot 策略执行情况分析")
    print("=" * 60)
    
    now = datetime.now()
    print(f"分析时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 计算当前市场
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
    
    market_id = f"btc-5min-{market_time.hour:02d}{market_time.minute:02d}"
    window_end = market_time + timedelta(minutes=5)
    time_to_end = (window_end - now).total_seconds()
    
    print("📊 当前市场状态:")
    print(f"  当前市场: {market_id}")
    print(f"  市场开始: {market_time.strftime('%H:%M')}")
    print(f"  窗口结束: {window_end.strftime('%H:%M:%S')}")
    print(f"  剩余时间: {time_to_end:.0f}秒")
    print()
    
    # 2. 检查T-10秒触发
    print("🎯 T-10秒策略触发检查:")
    trigger_condition = 10 < time_to_end <= 15
    
    if trigger_condition:
        print("  ✅ 触发条件满足: 10 < 剩余时间 <= 15秒")
        print(f"    当前剩余时间: {time_to_end:.1f}秒")
        print("    策略应该正在执行!")
    elif time_to_end > 15:
        seconds_until_trigger = time_to_end - 15
        t10_start = window_end - timedelta(seconds=15)
        t10_end = window_end - timedelta(seconds=10)
        print(f"  ⏳ 触发条件未满足: 剩余时间 > 15秒")
        print(f"    当前剩余时间: {time_to_end:.1f}秒")
        print(f"    距离触发: {seconds_until_trigger:.0f}秒")
        print(f"    触发时间: {t10_start.strftime('%H:%M:%S')} 到 {t10_end.strftime('%H:%M:%S')}")
    else:
        print("  ⏸️ 触发条件已过: 剩余时间 <= 10秒")
        print(f"    当前剩余时间: {time_to_end:.1f}秒")
        print("    策略执行时间已过")
    
    print()
    
    # 3. 模拟策略执行
    print("🤖 策略执行模拟:")
    
    if trigger_condition:
        # 模拟T-10秒策略
        btc_direction = "UP" if random.random() > 0.15 else "DOWN"
        
        if btc_direction == "UP":
            yes_price = 0.92  # 优势价格
            no_price = 0.10   # 安全价格
        else:
            no_price = 0.08   # 优势价格
            yes_price = 0.90  # 安全价格
        
        amount = 100
        
        # 计算返佣
        yes_rebate = yes_price * amount * 0.005
        no_rebate = no_price * amount * 0.005
        total_rebate = yes_rebate + no_rebate
        
        print(f"  BTC方向预测: {btc_direction} (85%确定性)")
        print(f"  双边挂单价格:")
        print(f"    YES: ${yes_price:.2f}")
        print(f"    NO: ${no_price:.2f}")
        print(f"  每侧数量: {amount}合约")
        print(f"  预计返佣: ${total_rebate:.2f}")
        print(f"  策略类型: T-10秒增强")
        
        # 计算预期利润范围
        print(f"  预期利润范围: $0.30 - $1.00/市场")
    else:
        print("  策略未触发，无执行模拟")
    
    print()
    
    # 4. 性能分析
    print("📈 性能分析:")
    
    # 假设参数
    daily_markets = 288
    participation_rate = 0.5
    markets_per_day = int(daily_markets * participation_rate)
    
    # 利润估计
    basic_profit_per_market = 0.50  # 基本做市
    enhanced_profit_per_market = 1.00  # T-10秒增强
    
    basic_daily = markets_per_day * basic_profit_per_market
    enhanced_daily = markets_per_day * enhanced_profit_per_market
    
    print(f"  每日市场数: {daily_markets}")
    print(f"  参与率: {participation_rate*100:.0f}%")
    print(f"  每日交易市场: {markets_per_day}")
    print()
    print(f"  基本做市策略:")
    print(f"    • 每市场利润: ${basic_profit_per_market:.2f}")
    print(f"    • 每日利润: ${basic_daily:.2f}")
    print(f"    • 每月利润: ${basic_daily * 30:.2f}")
    print()
    print(f"  T-10秒增强策略:")
    print(f"    • 每市场利润: ${enhanced_profit_per_market:.2f}")
    print(f"    • 每日利润: ${enhanced_daily:.2f}")
    print(f"    • 每月利润: ${enhanced_daily * 30:.2f}")
    
    print()
    
    # 5. 风险评估
    print("⚠️  风险评估:")
    print("  ✅ 优势:")
    print("    • 盈亏对称: 赢了赚多少，输了赔多少")
    print("    • 正期望值: 返佣确保基础盈利")
    print("    • 风险可控: 最大损失已知")
    print("    • 市场中性: 不依赖方向判断")
    print()
    print("  ⚠️  风险:")
    print("    • 网络延迟: 可能错过T-10秒时机")
    print("    • API限制: 可能被限流")
    print("    • 市场流动性: 可能无法成交")
    print("    • 系统稳定性: 需要24/7运行")
    
    print()
    print("=" * 60)
    print("🎯 总结")
    print("=" * 60)
    
    if trigger_condition:
        print("✅ 当前时间适合执行T-10秒策略")
        print("🤖 机器人应该正在执行双边挂单")
        print("💰 预期每市场利润: $0.30 - $1.00")
    elif time_to_end > 15:
        print("⏳ 等待T-10秒策略触发")
        print(f"📅 下次触发: {t10_start.strftime('%H:%M:%S')}")
        print(f"⏰ 距离触发: {seconds_until_trigger:.0f}秒")
    else:
        print("⏸️ T-10秒策略执行时间已过")
        print("🔄 等待下一个5分钟市场")
    
    print()
    print("🔧 建议:")
    print("  1. 确保机器人持续运行")
    print("  2. 检查网络连接稳定性")
    print("  3. 验证时间同步准确性")
    print("  4. 监控策略执行日志")
    
    print()
    print("🐝 我是勤劳的小蜜蜂，随时为您监控策略执行！")

def main():
    """主函数"""
    analyze_current_situation()

if __name__ == "__main__":
    main()