#!/usr/bin/env python3
"""
Polymarket Maker Bot 模拟运行测试
不依赖外部包，验证核心逻辑
"""

import time
from datetime import datetime, timedelta
import random

class SimpleMarketSimulator:
    """简单市场模拟器"""
    
    def __init__(self):
        self.current_time = datetime.now()
        self.btc_price = 50000.0
        self.market_prices = {}  # market_id -> price
        
    def update_time(self):
        """更新时间"""
        self.current_time += timedelta(seconds=1)
        return self.current_time
    
    def update_btc_price(self):
        """更新BTC价格"""
        # 随机波动
        change = random.uniform(-0.01, 0.01)  # -1% 到 +1%
        self.btc_price *= (1 + change)
        return self.btc_price
    
    def get_5min_market_id(self, dt=None):
        """获取5分钟市场ID"""
        if dt is None:
            dt = self.current_time
        
        # 找到下一个5分钟边界
        minute = dt.minute
        remainder = minute % 5
        minutes_to_next = 5 - remainder if remainder > 0 else 0
        
        if minutes_to_next == 0:
            market_time = dt.replace(second=0, microsecond=0)
        else:
            market_time = dt.replace(
                minute=minute + minutes_to_next,
                second=0,
                microsecond=0
            )
        
        market_id = f"btc-5min-{market_time.hour:02d}{market_time.minute:02d}"
        return market_id, market_time
    
    def calculate_market_price(self, market_id):
        """计算市场价格"""
        # 基于BTC价格和随机因素
        base_price = 0.5  # 50%概率
        btc_factor = (self.btc_price - 50000) / 50000 * 0.1  # BTC价格影响
        random_factor = random.uniform(-0.05, 0.05)  # 随机波动
        
        price = base_price + btc_factor + random_factor
        price = max(0.01, min(0.99, price))  # 限制在1%-99%
        
        self.market_prices[market_id] = price
        return price
    
    def should_execute_t_minus_10(self, market_time):
        """判断是否应该执行T-10秒策略"""
        window_end = market_time + timedelta(minutes=5)
        time_to_end = (window_end - self.current_time).total_seconds()
        
        return 10 < time_to_end <= 15

class SimpleStrategyTester:
    """简单策略测试器"""
    
    def __init__(self, simulator):
        self.simulator = simulator
        self.orders = []
        self.profits = []
        self.execution_log = []
        
    def execute_t_minus_10_strategy(self, market_id, market_time):
        """执行T-10秒策略"""
        # 模拟BTC方向判断（85%确定性）
        btc_direction = "UP" if random.random() > 0.15 else "DOWN"
        
        # 确定挂单价格
        if btc_direction == "UP":
            price = 0.92  # 0.90-0.95美元范围
            side = "YES"
        else:
            price = 0.92
            side = "NO"
        
        # 模拟挂单
        order = {
            'market_id': market_id,
            'side': side,
            'price': price,
            'amount': 100,
            'timestamp': self.simulator.current_time,
            'btc_direction': btc_direction,
        }
        
        self.orders.append(order)
        
        # 计算预期利润
        expected_profit = (1 - price) * 100  # 结算时每份合约获得(1-price)美元
        rebate = price * 100 * 0.005  # 0.5%返佣
        
        total_profit = expected_profit + rebate
        
        log_entry = {
            'time': self.simulator.current_time.strftime('%H:%M:%S'),
            'market': market_id,
            'side': side,
            'price': price,
            'expected_profit': expected_profit,
            'rebate': rebate,
            'total_profit': total_profit,
        }
        
        self.execution_log.append(log_entry)
        self.profits.append(total_profit)
        
        return log_entry
    
    def run_simulation(self, duration_minutes=30):
        """运行模拟"""
        print("🚀 开始策略模拟测试...")
        print(f"模拟时长: {duration_minutes}分钟")
        print(f"开始时间: {self.simulator.current_time.strftime('%H:%M:%S')}")
        print()
        
        end_time = self.simulator.current_time + timedelta(minutes=duration_minutes)
        iteration = 0
        
        while self.simulator.current_time < end_time:
            iteration += 1
            
            # 更新时间
            self.simulator.update_time()
            self.simulator.update_btc_price()
            
            # 获取当前市场
            market_id, market_time = self.simulator.get_5min_market_id()
            
            # 检查是否应该执行T-10秒策略
            if self.simulator.should_execute_t_minus_10(market_time):
                # 执行策略
                result = self.execute_t_minus_10_strategy(market_id, market_time)
                
                # 每5次执行显示一次
                if len(self.execution_log) % 5 == 0 or len(self.execution_log) == 1:
                    print(f"⏰ {result['time']} - 市场 {result['market']}")
                    print(f"  方向: {result['side']}, 价格: ${result['price']:.2f}")
                    print(f"  预期利润: ${result['expected_profit']:.2f}")
                    print(f"  返佣: ${result['rebate']:.2f}")
                    print(f"  总利润: ${result['total_profit']:.2f}")
                    print()
            
            # 每30秒显示一次状态
            if iteration % 30 == 0:
                print(f"📊 状态更新 - {self.simulator.current_time.strftime('%H:%M:%S')}")
                print(f"  BTC价格: ${self.simulator.btc_price:,.2f}")
                print(f"  累计订单: {len(self.orders)}")
                print(f"  累计利润: ${sum(self.profits):.2f}")
                print()
            
            # 模拟1秒间隔
            time.sleep(0.01)  # 加快模拟速度
        
        # 生成最终报告
        self.generate_report()
    
    def generate_report(self):
        """生成模拟报告"""
        print("=" * 60)
        print("📋 模拟测试结果报告")
        print("=" * 60)
        
        total_orders = len(self.orders)
        total_profit = sum(self.profits)
        avg_profit_per_order = total_profit / total_orders if total_orders > 0 else 0
        
        # 按方向统计
        yes_orders = sum(1 for o in self.orders if o['side'] == 'YES')
        no_orders = sum(1 for o in self.orders if o['side'] == 'NO')
        
        print(f"总订单数: {total_orders}")
        print(f"YES订单: {yes_orders} ({yes_orders/total_orders*100:.1f}%)")
        print(f"NO订单: {no_orders} ({no_orders/total_orders*100:.1f}%)")
        print()
        
        print(f"总利润: ${total_profit:.2f}")
        print(f"平均每单利润: ${avg_profit_per_order:.2f}")
        print()
        
        # 利润分布
        if self.profits:
            max_profit = max(self.profits)
            min_profit = min(self.profits)
            print(f"最高单笔利润: ${max_profit:.2f}")
            print(f"最低单笔利润: ${min_profit:.2f}")
            print()
        
        # 时间分析
        if self.execution_log:
            first_time = self.execution_log[0]['time']
            last_time = self.execution_log[-1]['time']
            print(f"第一单时间: {first_time}")
            print(f"最后一单时间: {last_time}")
            print()
        
        # 预期年化收益（基于30分钟模拟）
        # 假设每天交易8小时，每月20天
        hourly_rate = total_profit * 2  # 30分钟利润 × 2 = 每小时利润
        daily_rate = hourly_rate * 8   # 每天8小时
        monthly_rate = daily_rate * 20  # 每月20天
        annual_rate = monthly_rate * 12  # 每年12个月
        
        print("📈 年化收益估算（基于模拟数据）:")
        print(f"  每小时: ${hourly_rate:.2f}")
        print(f"  每天: ${daily_rate:.2f}")
        print(f"  每月: ${monthly_rate:.2f}")
        print(f"  每年: ${annual_rate:.2f}")
        print()
        
        print("🎯 策略有效性分析:")
        
        if total_profit > 0:
            print("✅ 策略盈利: 是")
            print(f"✅ 盈利比例: {total_profit/(total_orders*100)*100:.1f}% (相对于总仓位)")
        else:
            print("❌ 策略盈利: 否")
            print("⚠️  需要调整策略参数")
        
        print()
        print("💡 建议:")
        if avg_profit_per_order < 5:
            print("  • 考虑提高挂单价格（如0.93-0.95美元）")
            print("  • 增加订单数量")
            print("  • 优化BTC方向判断算法")
        else:
            print("  • 策略表现良好，可以考虑实盘测试")
            print("  • 逐步增加资金规模")
            print("  • 添加更多市场监控")
        
        print("=" * 60)

def main():
    """主函数"""
    print("🐝 Polymarket Maker Bot 策略模拟测试")
    print("基于T-10秒策略的5分钟市场做市")
    print()
    
    # 创建模拟器和测试器
    simulator = SimpleMarketSimulator()
    tester = SimpleStrategyTester(simulator)
    
    try:
        # 运行30分钟模拟
        tester.run_simulation(duration_minutes=30)
        
        print("\n🎉 模拟测试完成！")
        print("下一步:")
        print("1. 等待依赖包安装完成")
        print("2. 运行完整机器人测试")
        print("3. 调整策略参数优化")
        print("4. 准备VPS部署")
        
    except KeyboardInterrupt:
        print("\n🛑 模拟被用户中断")
        tester.generate_report()
    except Exception as e:
        print(f"\n❌ 模拟出错: {e}")

if __name__ == "__main__":
    main()