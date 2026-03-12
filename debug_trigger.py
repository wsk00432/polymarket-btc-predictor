#!/usr/bin/env python3
"""
调试触发逻辑问题
"""

from datetime import datetime, timedelta
import time

def debug_missed_triggers():
    """调试错过的触发"""
    print("🔍 调试错过的T-10秒触发")
    print("=" * 60)
    
    # 分析机器人运行期间的两个市场
    markets = [
        {
            "name": "10:30结束市场",
            "start": "10:25:00",
            "end": "10:30:00",
            "trigger_start": "10:29:45.500",
            "trigger_end": "10:29:50.500",
            "robot_start": "10:23:20"  # 机器人启动时间
        },
        {
            "name": "10:35结束市场", 
            "start": "10:30:00",
            "end": "10:35:00",
            "trigger_start": "10:34:45.500",
            "trigger_end": "10:34:50.500",
            "robot_start": "10:23:20"
        }
    ]
    
    for market in markets:
        print(f"\n📊 {market['name']}分析:")
        print("-" * 40)
        
        # 解析时间
        today = datetime.now().date()
        market_end = datetime.strptime(market["end"], "%H:%M:%S").replace(
            year=today.year, month=today.month, day=today.day
        )
        trigger_start = datetime.strptime(market["trigger_start"], "%H:%M:%S.%f").replace(
            year=today.year, month=today.month, day=today.day
        )
        trigger_end = datetime.strptime(market["trigger_end"], "%H:%M:%S.%f").replace(
            year=today.year, month=today.month, day=today.day
        )
        robot_start = datetime.strptime(market["robot_start"], "%H:%M:%S").replace(
            year=today.year, month=today.month, day=today.day
        )
        
        print(f"市场结束: {market_end.strftime('%H:%M:%S')}")
        print(f"触发时间: {trigger_start.strftime('%H:%M:%S.%f')[:-3]} 到 {trigger_end.strftime('%H:%M:%S.%f')[:-3]}")
        print(f"机器人启动: {robot_start.strftime('%H:%M:%S')}")
        
        # 检查机器人是否在运行
        if robot_start < trigger_start:
            print("✅ 机器人在触发时间前已启动")
        else:
            print("❌ 机器人在触发时间后启动")
        
        # 检查当前时间
        now = datetime.now()
        if now > trigger_end:
            print("⏸️ 触发时间已过")
            
            # 模拟触发检查
            for check_time in [trigger_start, trigger_start + timedelta(seconds=1), 
                              trigger_start + timedelta(seconds=2), trigger_end]:
                time_to_end = (market_end - check_time).total_seconds()
                
                # 修复后的触发逻辑
                trigger_buffer = 0.5
                lower_bound = 10 - trigger_buffer
                upper_bound = 15 - trigger_buffer
                
                triggers = lower_bound <= time_to_end <= upper_bound
                
                print(f"  {check_time.strftime('%H:%M:%S.%f')[:-3]}: 剩余{time_to_end:.3f}秒 → {'触发' if triggers else '不触发'}")
        
        print()

def test_trigger_precision():
    """测试触发精度"""
    print("\n🎯 触发精度测试")
    print("=" * 60)
    
    # 测试不同的剩余时间
    test_values = [
        15.0,  # T-15秒
        14.9, 14.5, 14.0, 13.5, 13.0,
        12.5, 12.0, 11.5, 11.0,
        10.5, 10.0,  # T-10秒
        9.5,  9.0,  8.5, 8.0,
    ]
    
    trigger_buffer = 0.5
    lower_bound = 10 - trigger_buffer  # 9.5
    upper_bound = 15 - trigger_buffer  # 14.5
    
    print(f"触发条件: {lower_bound:.1f} <= 剩余时间 <= {upper_bound:.1f}")
    print()
    print("测试结果:")
    print("-" * 40)
    
    for remaining in test_values:
        triggers = lower_bound <= remaining <= upper_bound
        marker = "⭐" if remaining == 10.0 else ""
        
        print(f"剩余{remaining:5.1f}秒: {'触发' if triggers else '不触发'} {marker}")
    
    print()
    print("关键验证:")
    print(f"  • T-10秒 (10.0秒): {'包含' if lower_bound <= 10.0 <= upper_bound else '不包含'}")
    print(f"  • T-9.5秒 (9.5秒): {'包含' if lower_bound <= 9.5 <= upper_bound else '不包含'}")
    print(f"  • T-14.5秒 (14.5秒): {'包含' if lower_bound <= 14.5 <= upper_bound else '不包含'}")
    print(f"  • T-15秒 (15.0秒): {'包含' if lower_bound <= 15.0 <= upper_bound else '不包含'}")

def simulate_robot_check():
    """模拟机器人检查过程"""
    print("\n🤖 模拟机器人检查过程")
    print("=" * 60)
    
    # 模拟10:34:45-10:34:50期间
    market_end = datetime.now().replace(hour=10, minute=35, second=0, microsecond=0)
    
    print(f"模拟市场: 结束时间 {market_end.strftime('%H:%M:%S')}")
    print(f"触发时间: 10:34:45.500 到 10:34:50.500")
    print()
    print("模拟检查过程 (每秒检查一次):")
    print("-" * 40)
    
    trigger_count = 0
    
    for second in range(45, 51):  # 45-50秒
        for millisecond in [0, 250, 500, 750]:  # 每250ms检查一次
            check_time = market_end.replace(
                minute=34, second=second, microsecond=millisecond*1000
            )
            
            time_to_end = (market_end - check_time).total_seconds()
            
            # 修复后的触发逻辑
            trigger_buffer = 0.5
            lower_bound = 10 - trigger_buffer
            upper_bound = 15 - trigger_buffer
            
            triggers = lower_bound <= time_to_end <= upper_bound
            
            if triggers:
                trigger_count += 1
                print(f"{check_time.strftime('%H:%M:%S.%f')[:-3]}: 剩余{time_to_end:.3f}秒 → 🎯 触发")
            else:
                print(f"{check_time.strftime('%H:%M:%S.%f')[:-3]}: 剩余{time_to_end:.3f}秒 → ⏸️ 不触发")
    
    print()
    print(f"总计触发次数: {trigger_count}次")
    print(f"触发概率: {trigger_count/24*100:.1f}% (每250ms检查一次)")

def check_code_implementation():
    """检查代码实现"""
    print("\n💻 检查代码实现")
    print("=" * 60)
    
    print("机器人代码中的触发逻辑:")
    print("```python")
    print("# 修复后的触发逻辑")
    print("trigger_buffer = 0.5  # 0.5秒缓冲应对网络延迟")
    print("lower_bound = 10 - trigger_buffer  # 9.5秒")
    print("upper_bound = 15 - trigger_buffer  # 14.5秒")
    print("")
    print("if lower_bound <= time_to_end <= upper_bound:")
    print("    logger.info(f'🎯 T-10秒策略触发 - 市场: {market_id}')")
    print("    logger.info(f'  剩余时间: {time_to_end:.1f}秒 (触发范围: {lower_bound:.1f}-{upper_bound:.1f}秒)')")
    print("    # 执行策略...")
    print("```")
    
    print()
    print("潜在问题:")
    print("1. time_to_end 计算精度 - 使用total_seconds()返回浮点数")
    print("2. 比较操作符 - 使用 <= 包含边界")
    print("3. 时间获取 - datetime.now() 的精度")
    print("4. 执行延迟 - if条件检查到实际执行有时间差")

def main():
    """主函数"""
    print("🐝 Polymarket Maker Bot 触发逻辑调试")
    print("=" * 60)
    
    # 1. 调试错过的触发
    debug_missed_triggers()
    
    # 2. 测试触发精度
    test_trigger_precision()
    
    # 3. 模拟机器人检查
    simulate_robot_check()
    
    # 4. 检查代码实现
    check_code_implementation()
    
    # 5. 总结
    print("\n" + "=" * 60)
    print("🎯 调试总结")
    print("=" * 60)
    
    print("✅ 触发逻辑正确:")
    print("  • 条件: 9.5 <= 剩余时间 <= 14.5")
    print("  • 包含T-10秒: 是")
    print("  • 边界处理: 正确")
    
    print("\n⚠️  可能的问题:")
    print("  1. 时间同步 - 系统时间可能有微小误差")
    print("  2. 检查频率 - 1秒/次可能错过精确时机")
    print("  3. 执行延迟 - 从检查到执行有时间差")
    print("  4. 浮点数比较 - 浮点数精度问题")
    
    print("\n🔧 建议改进:")
    print("  1. 提高检查频率到100ms")
    print("  2. 添加时间容错 (±0.1秒)")
    print("  3. 记录精确的触发时间")
    print("  4. 监控触发成功率")
    
    print("\n" + "=" * 60)
    print("🎉 调试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()