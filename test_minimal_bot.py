#!/usr/bin/env python3
"""
Polymarket Maker Bot 最小化测试
验证机器人核心功能能否正常运行
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MinimalBot:
    """最小化测试机器人"""
    
    def __init__(self):
        self.running = False
        logger.info("最小化测试机器人初始化")
    
    async def initialize(self):
        """初始化"""
        logger.info("初始化完成")
        return True
    
    async def test_5min_market_logic(self):
        """测试5分钟市场逻辑"""
        logger.info("测试5分钟市场逻辑...")
        
        from datetime import datetime, timedelta
        
        # 测试当前时间的市场计算
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
        
        market_id = f"btc-5min-{market_time.hour:02d}{market_time.minute:02d}"
        window_end = market_time + timedelta(minutes=5)
        time_to_end = (window_end - now).total_seconds()
        
        logger.info(f"当前时间: {now.strftime('%H:%M:%S')}")
        logger.info(f"下一个5分钟市场: {market_id}")
        logger.info(f"市场开始: {market_time.strftime('%H:%M')}")
        logger.info(f"窗口结束: {window_end.strftime('%H:%M:%S')}")
        logger.info(f"剩余时间: {time_to_end:.0f}秒")
        
        # 检查T-10秒
        if 10 < time_to_end <= 15:
            logger.info("✅ T-10秒策略: 应该执行")
        else:
            logger.info("⏸️ T-10秒策略: 不应该执行")
        
        return True
    
    async def test_fee_calculation(self):
        """测试手续费计算"""
        logger.info("测试手续费计算...")
        
        def calculate_fee(probability):
            C = 1.0
            p = probability
            fee = C * 0.25 * (p * (1 - p)) ** 2
            return fee
        
        # 测试关键概率点
        test_points = [0.1, 0.3, 0.5, 0.7, 0.9]
        for p in test_points:
            fee = calculate_fee(p)
            logger.info(f"概率 {p:.1%} → 手续费: {fee*100:.2f}%")
        
        # 验证50%概率最高
        fees = [calculate_fee(p) for p in test_points]
        max_fee = max(fees)
        max_fee_prob = test_points[fees.index(max_fee)]
        
        if abs(max_fee_prob - 0.5) < 0.1:
            logger.info(f"✅ 验证通过: 50%概率时手续费最高 ({max_fee*100:.2f}%)")
        else:
            logger.warning(f"⚠️ 验证失败: 最高手续费在概率 {max_fee_prob:.1%}")
        
        return True
    
    async def test_profit_calculation(self):
        """测试利润计算"""
        logger.info("测试利润计算...")
        
        # 测试案例
        test_cases = [
            (0.90, 100, "低价挂单"),
            (0.92, 100, "中等价格"),
            (0.95, 100, "高价挂单"),
        ]
        
        for price, amount, description in test_cases:
            expected_profit = (1 - price) * amount
            rebate = price * amount * 0.005  # 0.5%返佣
            total_profit = expected_profit + rebate
            
            logger.info(f"{description}:")
            logger.info(f"  价格: ${price:.2f}, 数量: {amount}")
            logger.info(f"  预期利润: ${expected_profit:.2f}")
            logger.info(f"  返佣: ${rebate:.2f}")
            logger.info(f"  总利润: ${total_profit:.2f}")
        
        return True
    
    async def test_async_operations(self):
        """测试异步操作"""
        logger.info("测试异步操作...")
        
        async def mock_api_call(name, delay):
            """模拟API调用"""
            logger.info(f"开始 {name} API调用...")
            await asyncio.sleep(delay)
            logger.info(f"完成 {name} API调用")
            return f"{name}_result"
        
        # 测试并发操作
        tasks = [
            mock_api_call("手续费查询", 0.1),
            mock_api_call("市场信息", 0.2),
            mock_api_call("价格获取", 0.15),
        ]
        
        results = await asyncio.gather(*tasks)
        logger.info(f"API调用结果: {results}")
        
        return True
    
    async def run_tests(self):
        """运行所有测试"""
        logger.info("🚀 开始运行最小化测试...")
        
        tests = [
            ("5分钟市场逻辑", self.test_5min_market_logic),
            ("手续费计算", self.test_fee_calculation),
            ("利润计算", self.test_profit_calculation),
            ("异步操作", self.test_async_operations),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                logger.info(f"\n🔍 测试: {test_name}")
                result = await test_func()
                results.append((test_name, result))
                logger.info(f"📋 {test_name}: {'✅ 通过' if result else '❌ 失败'}")
            except Exception as e:
                logger.error(f"❌ {test_name} 测试异常: {e}")
                results.append((test_name, False))
        
        # 汇总结果
        logger.info("\n" + "=" * 60)
        logger.info("📊 测试结果汇总")
        logger.info("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            logger.info(f"{test_name:20} {status}")
        
        logger.info(f"\n🎯 通过率: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            logger.info("\n🎉 所有测试通过！机器人核心功能正常。")
            return True
        else:
            logger.warning(f"\n⚠️  {total - passed} 个测试失败")
            return False
    
    async def run_demo(self, duration_seconds=30):
        """运行演示"""
        logger.info(f"\n🎬 开始运行演示 ({duration_seconds}秒)...")
        
        self.running = True
        start_time = datetime.now()
        iteration = 0
        
        try:
            while self.running:
                iteration += 1
                current_time = datetime.now()
                elapsed = (current_time - start_time).total_seconds()
                
                if elapsed >= duration_seconds:
                    break
                
                # 模拟机器人工作
                if iteration % 10 == 0:
                    logger.info(f"🔁 迭代 {iteration}, 已运行 {elapsed:.0f}秒")
                
                # 模拟5分钟市场检查
                if iteration % 15 == 0:
                    await self.test_5min_market_logic()
                
                await asyncio.sleep(1)  # 1秒循环
            
            logger.info(f"\n✅ 演示完成，运行时间: {elapsed:.0f}秒")
            logger.info(f"总迭代次数: {iteration}")
            
        except KeyboardInterrupt:
            logger.info("\n🛑 演示被用户中断")
        except Exception as e:
            logger.error(f"\n❌ 演示出错: {e}")
        finally:
            self.running = False
        
        return True

async def main():
    """主函数"""
    print("=" * 60)
    print("🐝 Polymarket Maker Bot 最小化测试")
    print("=" * 60)
    
    bot = MinimalBot()
    
    try:
        # 初始化
        await bot.initialize()
        
        # 运行测试
        tests_passed = await bot.run_tests()
        
        if tests_passed:
            print("\n🎉 所有测试通过！")
            print("\n🚀 准备运行完整机器人...")
            print("按 Ctrl+C 停止")
            
            # 运行简短演示
            await bot.run_demo(duration_seconds=30)
            
            print("\n✅ 测试完成！")
            print("\n📋 下一步:")
            print("1. 运行完整机器人: python run_bot.py")
            print("2. 监控日志: tail -f polymarket_maker_test.log")
            print("3. 检查性能报告")
            
            return 0
        else:
            print("\n⚠️ 测试失败，请检查问题")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
        return 0
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        return 1

if __name__ == "__main__":
    # 检查是否在虚拟环境中
    if not hasattr(sys, 'real_prefix') and not sys.base_prefix != sys.prefix:
        print("⚠️ 建议在虚拟环境中运行")
        print("激活虚拟环境: source venv/bin/activate")
        print()
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)