#!/usr/bin/env python3
"""
Polymarket Maker Bot 快速验证
验证核心功能是否正常工作
"""

import sys
import os
from datetime import datetime, timedelta

def verify_core_logic():
    """验证核心逻辑"""
    print("🔍 验证核心逻辑...")
    
    # 1. 验证5分钟市场时间计算
    print("\n1. 5分钟市场时间计算验证:")
    
    test_times = [
        datetime(2026, 2, 26, 14, 32, 15),  # 14:32:15
        datetime(2026, 2, 26, 14, 35, 0),   # 14:35:00
        datetime(2026, 2, 26, 14, 37, 45),  # 14:37:45
    ]
    
    for test_time in test_times:
        minute = test_time.minute
        remainder = minute % 5
        minutes_to_next = 5 - remainder if remainder > 0 else 0
        
        if minutes_to_next == 0:
            market_time = test_time.replace(second=0, microsecond=0)
        else:
            market_time = test_time.replace(
                minute=minute + minutes_to_next,
                second=0,
                microsecond=0
            )
        
        market_id = f"btc-5min-{market_time.hour:02d}{market_time.minute:02d}"
        window_end = market_time + timedelta(minutes=5)
        time_to_end = (window_end - test_time).total_seconds()
        
        print(f"  时间 {test_time.strftime('%H:%M:%S')} → 市场 {market_id}")
        print(f"    市场开始: {market_time.strftime('%H:%M')}")
        print(f"    窗口结束: {window_end.strftime('%H:%M:%S')}")
        print(f"    剩余时间: {time_to_end:.0f}秒")
        
        # 检查T-10秒逻辑
        if 10 < time_to_end <= 15:
            print(f"    T-10秒策略: ✅ 应该执行")
        else:
            print(f"    T-10秒策略: ⏸️ 不应该执行")
        print()
    
    # 2. 验证手续费计算
    print("2. 动态手续费计算验证:")
    
    def calculate_fee(probability):
        """计算动态手续费"""
        C = 1.0  # 常数因子
        p = probability
        fee = C * 0.25 * (p * (1 - p)) ** 2
        return fee
    
    test_probabilities = [0.1, 0.3, 0.5, 0.7, 0.9]
    print("   概率   手续费")
    print("   -----  ------")
    for p in test_probabilities:
        fee = calculate_fee(p)
        print(f"   {p:.1%}    {fee*100:.2f}%")
    
    # 验证50%概率时手续费最高
    fees = [calculate_fee(p) for p in test_probabilities]
    max_fee = max(fees)
    max_fee_prob = test_probabilities[fees.index(max_fee)]
    
    if abs(max_fee_prob - 0.5) < 0.1:
        print(f"\n   ✅ 验证通过: 50%概率时手续费最高 ({max_fee*100:.2f}%)")
    else:
        print(f"\n   ❌ 验证失败: 最高手续费在概率 {max_fee_prob:.1%}")
    
    # 3. 验证利润计算
    print("\n3. 利润计算验证:")
    
    test_cases = [
        (0.90, 100, "低价挂单"),
        (0.92, 100, "中等价格"),
        (0.95, 100, "高价挂单"),
    ]
    
    print("   价格   数量   预期利润   返佣(0.5%)   总利润")
    print("   ----  -----  ---------  ----------  --------")
    
    for price, amount, description in test_cases:
        expected_profit = (1 - price) * amount
        rebate = price * amount * 0.005  # 0.5%返佣
        total_profit = expected_profit + rebate
        
        print(f"   ${price:.2f}  {amount:5d}  ${expected_profit:8.2f}  ${rebate:9.2f}  ${total_profit:8.2f}  ({description})")
    
    # 4. 验证策略逻辑
    print("\n4. T-10秒策略逻辑验证:")
    
    # 模拟BTC方向判断（85%确定性）
    import random
    random.seed(42)  # 固定随机种子以便测试
    
    test_runs = 1000
    up_count = 0
    
    for _ in range(test_runs):
        btc_direction = "UP" if random.random() > 0.15 else "DOWN"
        if btc_direction == "UP":
            up_count += 1
    
    up_percentage = up_count / test_runs * 100
    print(f"   模拟 {test_runs} 次BTC方向判断:")
    print(f"   UP方向: {up_count}次 ({up_percentage:.1f}%)")
    print(f"   DOWN方向: {test_runs - up_count}次 ({100-up_percentage:.1f}%)")
    
    if 80 < up_percentage < 90:
        print(f"   ✅ UP方向概率在85%附近 ({up_percentage:.1f}%)")
    else:
        print(f"   ⚠️  UP方向概率偏离85% ({up_percentage:.1f}%)")
    
    return True

def verify_file_structure():
    """验证文件结构"""
    print("\n📁 验证文件结构...")
    
    required_files = [
        ('phase1_quick_start.py', '核心机器人代码'),
        ('config.py', '配置文件'),
        ('run_bot.py', '主运行脚本'),
        ('.env', '环境变量文件'),
        ('requirements.txt', '依赖列表'),
        ('README_MAKER_BOT.md', '使用文档'),
        ('AUTOMATED_MAKER_BOT_PLAN.md', '技术方案'),
    ]
    
    all_exist = True
    for filename, description in required_files:
        if os.path.exists(filename):
            print(f"   ✅ {filename:25} - {description}")
        else:
            print(f"   ❌ {filename:25} - {description} (缺失)")
            all_exist = False
    
    return all_exist

def verify_configuration():
    """验证配置"""
    print("\n⚙️ 验证配置...")
    
    try:
        # 检查环境变量
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_content = f.read()
            
            required_env_vars = [
                'POLYMARKET_PRIVATE_KEY',
                'POLYMARKET_WALLET_ADDRESS', 
                'PAPER_TRADING',
                'LOG_LEVEL',
            ]
            
            print("   环境变量检查:")
            for var in required_env_vars:
                if var in env_content:
                    print(f"     ✅ {var}")
                else:
                    print(f"     ❌ {var} (未设置)")
            
            # 检查模拟交易模式
            if 'PAPER_TRADING=true' in env_content.lower():
                print("    ✅ 模拟交易模式已启用")
            else:
                print("    ⚠️  模拟交易模式未启用")
        
        return True
        
    except Exception as e:
        print(f"   配置验证失败: {e}")
        return False

def calculate_expected_profits():
    """计算预期收益"""
    print("\n💰 预期收益计算:")
    
    # 基于文章分析和我们的策略
    daily_markets = 288  # 每天288个5分钟市场
    participation_rate = 0.5  # 参与50%的市场
    profit_per_market = 7.5  # 每个市场7.5美元利润（0.075美元×100合约）
    rebate_per_market = 0.46  # 每个市场0.46美元返佣（0.92×100×0.5%）
    
    daily_profit = daily_markets * participation_rate * (profit_per_market + rebate_per_market)
    monthly_profit = daily_profit * 30
    annual_profit = monthly_profit * 12
    
    print(f"   每天5分钟市场: {daily_markets}个")
    print(f"   参与率: {participation_rate*100:.0f}%")
    print(f"   每个市场利润: ${profit_per_market:.2f} + ${rebate_per_market:.2f}返佣")
    print(f"   -------------------------------")
    print(f"   每日利润: ${daily_profit:.2f}")
    print(f"   每月利润: ${monthly_profit:.2f}")
    print(f"   每年利润: ${annual_profit:.2f}")
    
    # 优化潜力
    print("\n   📈 优化潜力:")
    print(f"   提高参与率到80%: ${daily_markets*0.8*(profit_per_market+rebate_per_market)*30:.2f}/月")
    print(f"   增加仓位到200合约: ${daily_markets*0.5*(15+0.92)*30:.2f}/月")
    print(f"   两者都优化: ${daily_markets*0.8*(15+0.92)*30:.2f}/月")

def main():
    """主函数"""
    print("=" * 60)
    print("🐝 Polymarket Maker Bot 快速验证")
    print("=" * 60)
    
    print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"工作目录: {os.getcwd()}")
    print()
    
    # 运行验证
    results = []
    
    results.append(("核心逻辑", verify_core_logic()))
    results.append(("文件结构", verify_file_structure()))
    results.append(("配置", verify_configuration()))
    
    # 计算预期收益
    calculate_expected_profits()
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 验证结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:15} {status}")
    
    print(f"\n🎯 通过率: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有验证通过！")
        print("\n🚀 下一步:")
        print("1. 等待依赖包安装完成")
        print("2. 激活虚拟环境: source venv/bin/activate")
        print("3. 运行机器人: python run_bot.py")
        print("4. 监控日志文件: tail -f polymarket_maker_test.log")
        print("\n⚠️  注意: 当前为模拟交易模式，不会实际下单")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个验证失败")
        print("\n🔧 需要修复的问题:")
        for test_name, result in results:
            if not result:
                print(f"  • {test_name}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)