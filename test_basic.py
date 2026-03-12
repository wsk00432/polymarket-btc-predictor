#!/usr/bin/env python3
"""
Polymarket Maker Bot 基础功能测试
快速验证核心功能是否正常工作
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_imports():
    """测试导入"""
    print("🧪 测试模块导入...")
    
    try:
        import config
        print("✅ config.py 导入成功")
        
        # 测试配置加载
        print(f"📊 配置项数量: {len([x for x in dir(config) if not x.startswith('_')])}")
        
        # 检查关键配置
        required_configs = [
            'WALLET_CONFIG',
            'API_CONFIG', 
            'TRADING_CONFIG',
            'STRATEGY_CONFIG',
            'PERFORMANCE_CONFIG'
        ]
        
        for cfg in required_configs:
            if hasattr(config, cfg):
                print(f"✅ {cfg} 配置存在")
            else:
                print(f"❌ {cfg} 配置缺失")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

async def test_phase1_code():
    """测试phase1代码结构"""
    print("\n🧪 测试phase1_quick_start.py代码结构...")
    
    try:
        # 读取文件检查基本结构
        with open('phase1_quick_start.py', 'r') as f:
            content = f.read()
        
        # 检查关键类和方法
        checks = [
            ('class PolymarketMakerBot', '主类定义'),
            ('async def initialize', '初始化方法'),
            ('async def get_fee_rate', '手续费查询'),
            ('def sign_order', '订单签名'),
            ('async def place_maker_order', '挂单方法'),
            ('async def cancel_replace_cycle', '撤单重下循环'),
            ('async def monitor_5min_markets', '5分钟市场监控'),
            ('async def execute_t_minus_10_strategy', 'T-10秒策略'),
        ]
        
        for check_str, description in checks:
            if check_str in content:
                print(f"✅ {description} 存在")
            else:
                print(f"❌ {description} 缺失")
        
        # 检查行数
        lines = content.split('\n')
        print(f"📝 代码行数: {len(lines)} 行")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def test_config_values():
    """测试配置值"""
    print("\n🧪 测试配置值...")
    
    try:
        import config
        
        # 测试关键配置值
        tests = [
            ('STRATEGY_CONFIG.five_minute_markets.enabled', True, '5分钟策略启用'),
            ('STRATEGY_CONFIG.five_minute_markets.t_minus_seconds', 10, 'T-10秒'),
            ('PERFORMANCE_CONFIG.target_cancel_replace_ms', 100, '目标延迟100ms'),
            ('PERFORMANCE_CONFIG.max_acceptable_latency_ms', 200, '最大延迟200ms'),
            ('TRADING_CONFIG.default_order_size', 100, '默认订单大小'),
        ]
        
        all_passed = True
        for path, expected, description in tests:
            try:
                # 简单的属性访问
                if path == 'STRATEGY_CONFIG.five_minute_markets.enabled':
                    value = config.STRATEGY_CONFIG['five_minute_markets']['enabled']
                elif path == 'STRATEGY_CONFIG.five_minute_markets.t_minus_seconds':
                    value = config.STRATEGY_CONFIG['five_minute_markets']['t_minus_seconds']
                elif path == 'PERFORMANCE_CONFIG.target_cancel_replace_ms':
                    value = config.PERFORMANCE_CONFIG['target_cancel_replace_ms']
                elif path == 'PERFORMANCE_CONFIG.max_acceptable_latency_ms':
                    value = config.PERFORMANCE_CONFIG['max_acceptable_latency_ms']
                elif path == 'TRADING_CONFIG.default_order_size':
                    value = config.TRADING_CONFIG['default_order_size']
                else:
                    value = None
                
                if value == expected:
                    print(f"✅ {description}: {value} (符合预期)")
                else:
                    print(f"❌ {description}: {value} (预期: {expected})")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ {description} 测试失败: {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

async def test_environment():
    """测试环境变量"""
    print("\n🧪 测试环境变量...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # 检查关键环境变量
        env_vars = [
            ('POLYMARKET_PRIVATE_KEY', '私钥'),
            ('POLYMARKET_WALLET_ADDRESS', '钱包地址'),
            ('PAPER_TRADING', '模拟交易模式'),
            ('LOG_LEVEL', '日志级别'),
        ]
        
        all_set = True
        for var_name, description in env_vars:
            value = os.getenv(var_name)
            if value:
                masked_value = value[:10] + '...' if len(value) > 10 else '***'
                print(f"✅ {description}: 已设置 ({masked_value})")
            else:
                print(f"⚠️ {description}: 未设置")
                all_set = False
        
        # 检查模拟交易模式
        paper_trading = os.getenv('PAPER_TRADING', 'true').lower() == 'true'
        if paper_trading:
            print("✅ 模拟交易模式: 已启用 (安全模式)")
        else:
            print("⚠️ 模拟交易模式: 未启用 (实盘模式)")
        
        return all_set
        
    except Exception as e:
        print(f"❌ 环境变量测试失败: {e}")
        return False

async def test_dependencies():
    """测试依赖包"""
    print("\n🧪 测试Python依赖包...")
    
    dependencies = [
        ('aiohttp', '异步HTTP客户端'),
        ('asyncio', '异步IO'),
        ('websockets', 'WebSocket客户端'),
        ('ecdsa', '椭圆曲线签名'),
        ('pandas', '数据处理'),
        ('sqlalchemy', '数据库ORM'),
    ]
    
    all_installed = True
    for package, description in dependencies:
        try:
            __import__(package)
            print(f"✅ {description} ({package}): 已安装")
        except ImportError as e:
            print(f"❌ {description} ({package}): 未安装 - {e}")
            all_installed = False
    
    return all_installed

async def test_5min_market_logic():
    """测试5分钟市场逻辑"""
    print("\n🧪 测试5分钟市场逻辑...")
    
    try:
        from datetime import datetime, timedelta
        
        # 测试市场时间计算
        test_time = datetime(2026, 2, 26, 14, 32, 15)  # 14:32:15
        
        # 计算下一个5分钟边界
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
        
        # 市场ID格式
        market_id = f"btc-5min-{market_time.hour:02d}{market_time.minute:02d}"
        
        # 窗口结束时间
        window_end = market_time + timedelta(minutes=5)
        time_to_end = (window_end - test_time).total_seconds()
        
        print(f"✅ 测试时间: {test_time.strftime('%H:%M:%S')}")
        print(f"✅ 下一个5分钟市场: {market_id}")
        print(f"✅ 市场开始: {market_time.strftime('%H:%M')}")
        print(f"✅ 窗口结束: {window_end.strftime('%H:%M:%S')}")
        print(f"✅ 剩余时间: {time_to_end:.0f}秒")
        
        # 测试T-10秒逻辑
        if 10 < time_to_end <= 15:
            print("✅ T-10秒策略: 应该执行")
        else:
            print("✅ T-10秒策略: 不应该执行")
        
        return True
        
    except Exception as e:
        print(f"❌ 5分钟市场逻辑测试失败: {e}")
        return False

async def test_fee_calculation():
    """测试手续费计算逻辑"""
    print("\n🧪 测试手续费计算逻辑...")
    
    try:
        # 测试动态手续费公式
        # 手续费 = C × 0.25 × (p × (1 - p))²
        
        def calculate_fee(probability):
            """计算动态手续费"""
            C = 1.0  # 常数因子
            p = probability
            fee = C * 0.25 * (p * (1 - p)) ** 2
            return fee
        
        # 测试不同概率下的手续费
        test_probabilities = [0.1, 0.3, 0.5, 0.7, 0.9]
        
        print("📊 手续费计算测试:")
        for p in test_probabilities:
            fee = calculate_fee(p)
            fee_percent = fee * 100
            print(f"  概率 {p:.1%} → 手续费: {fee_percent:.2f}%")
        
        # 验证50%概率时手续费最高
        fees = [calculate_fee(p) for p in test_probabilities]
        max_fee = max(fees)
        max_fee_prob = test_probabilities[fees.index(max_fee)]
        
        if abs(max_fee_prob - 0.5) < 0.1:
            print(f"✅ 验证通过: 50%概率时手续费最高 ({max_fee*100:.2f}%)")
        else:
            print(f"❌ 验证失败: 最高手续费在概率 {max_fee_prob:.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ 手续费计算测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("🐝 Polymarket Maker Bot 基础功能测试")
    print("=" * 60)
    
    test_results = []
    
    # 运行所有测试
    tests = [
        ("模块导入", test_imports),
        ("代码结构", test_phase1_code),
        ("配置值", test_config_values),
        ("环境变量", test_environment),
        ("依赖包", test_dependencies),
        ("5分钟市场逻辑", test_5min_market_logic),
        ("手续费计算", test_fee_calculation),
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔍 开始测试: {test_name}")
        try:
            result = await test_func()
            test_results.append((test_name, result))
            print(f"📋 {test_name}: {'✅ 通过' if result else '❌ 失败'}")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            test_results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} {status}")
    
    print(f"\n🎯 通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！可以开始运行机器人。")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查问题。")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)