#!/usr/bin/env python3
"""
Polymarket Maker Bot - 主运行脚本
快速启动方案
"""

import asyncio
import os
import sys
import signal
import logging
from datetime import datetime
from phase1_quick_start import PolymarketMakerBot
import config

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOGGING_CONFIG['level']),
    format=config.LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(config.LOGGING_CONFIG['file_path']),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BotRunner:
    """机器人运行器"""
    
    def __init__(self):
        self.bot = None
        self.running = False
        self.tasks = []
        
    async def initialize(self):
        """初始化机器人"""
        logger.info("🚀 初始化Polymarket Maker Bot...")
        
        # 从环境变量读取敏感信息
        private_key = os.getenv('POLYMARKET_PRIVATE_KEY')
        wallet_address = os.getenv('POLYMARKET_WALLET_ADDRESS')
        
        if not private_key or not wallet_address:
            logger.warning("⚠️ 未找到环境变量，使用模拟模式")
            private_key = '0x' + '0' * 64  # 模拟私钥
            wallet_address = '0x' + '0' * 40  # 模拟地址
        
        # 创建机器人实例
        self.bot = PolymarketMakerBot(private_key, wallet_address)
        
        # 初始化连接
        await self.bot.initialize()
        
        logger.info("✅ 机器人初始化完成")
    
    async def start(self):
        """启动机器人"""
        if not self.bot:
            await self.initialize()
        
        self.running = True
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("🤖 启动Polymarket Maker Bot...")
        
        try:
            # 启动各个任务
            tasks = [
                self.run_main_loop(),
                self.bot.monitor_5min_markets(),
                self.bot.run_performance_monitor(),
            ]
            
            # 如果配置启用，启动WebSocket连接
            if config.STRATEGY_CONFIG['market_making']['enabled']:
                tasks.append(self.bot.connect_binance_websocket())
                tasks.append(self.bot.connect_polymarket_websocket())
            
            # 运行所有任务
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except asyncio.CancelledError:
            logger.info("机器人任务被取消")
        except Exception as e:
            logger.error(f"机器人运行异常: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def run_main_loop(self):
        """主循环"""
        logger.info("🔄 启动主循环...")
        
        iteration = 0
        while self.running:
            try:
                iteration += 1
                
                # 执行主循环任务
                await self.main_loop_iteration(iteration)
                
                # 等待下一次循环
                await asyncio.sleep(1)  # 1秒循环
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"主循环异常: {e}")
                await asyncio.sleep(5)  # 异常后等待5秒
    
    async def main_loop_iteration(self, iteration: int):
        """主循环迭代"""
        # 每10次迭代记录一次状态
        if iteration % 10 == 0:
            logger.info(f"🔁 主循环迭代: {iteration}")
            
            # 报告状态
            active_orders = len(self.bot.active_orders) if self.bot else 0
            ws_messages = self.bot.latency_stats['ws_messages'] if self.bot else 0
            
            status_report = f"""
            📊 状态报告
            时间: {datetime.now().strftime('%H:%M:%S')}
            迭代: {iteration}
            活跃订单: {active_orders}
            WebSocket消息: {ws_messages}
            运行时间: {iteration}秒
            """
            logger.info(status_report)
        
        # 每60次迭代执行一次健康检查
        if iteration % 60 == 0:
            await self.health_check()
    
    async def health_check(self):
        """健康检查"""
        try:
            logger.info("🏥 执行健康检查...")
            
            # 检查连接状态
            if self.bot and self.bot.session:
                # 测试API连接
                test_url = "https://clob.polymarket.com/health"
                try:
                    async with self.bot.session.get(test_url, timeout=5) as response:
                        if response.status == 200:
                            logger.info("✅ API连接正常")
                        else:
                            logger.warning(f"⚠️ API连接异常: {response.status}")
                except Exception as e:
                    logger.error(f"❌ API连接失败: {e}")
            
            # 检查性能
            if self.bot and self.bot.latency_stats['cancel_replace_cycles']:
                cycles = self.bot.latency_stats['cancel_replace_cycles'][-10:]  # 最近10次
                if cycles:
                    avg_latency = sum(cycles) / len(cycles)
                    if avg_latency > config.PERFORMANCE_CONFIG['max_acceptable_latency_ms']:
                        logger.warning(f"⚠️ 平均延迟过高: {avg_latency:.1f}ms")
                    else:
                        logger.info(f"✅ 平均延迟正常: {avg_latency:.1f}ms")
            
            logger.info("✅ 健康检查完成")
            
        except Exception as e:
            logger.error(f"健康检查异常: {e}")
    
    def signal_handler(self, signum, frame):
        """信号处理"""
        logger.info(f"收到信号 {signum}，正在关闭...")
        self.running = False
    
    async def shutdown(self):
        """关闭机器人"""
        logger.info("🛑 正在关闭机器人...")
        
        self.running = False
        
        # 取消所有活跃订单
        if self.bot and self.bot.active_orders:
            logger.info(f"取消 {len(self.bot.active_orders)} 个活跃订单...")
            cancel_tasks = []
            for order_id in list(self.bot.active_orders.keys()):
                cancel_tasks.append(self.bot.cancel_order(order_id))
            
            if cancel_tasks:
                results = await asyncio.gather(*cancel_tasks, return_exceptions=True)
                success_count = sum(1 for r in results if r is True)
                logger.info(f"成功取消 {success_count} 个订单")
        
        # 关闭会话
        if self.bot and self.bot.session:
            await self.bot.session.close()
            logger.info("HTTP会话已关闭")
        
        # 生成最终报告
        await self.generate_final_report()
        
        logger.info("👋 机器人关闭完成")
    
    async def generate_final_report(self):
        """生成最终报告"""
        if not self.bot:
            return
        
        report = f"""
        📋 最终运行报告
        ====================
        结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        性能统计:
        • WebSocket消息: {self.bot.latency_stats['ws_messages']}
        • 错误次数: {self.bot.latency_stats['errors']}
        • 撤单/重下循环次数: {len(self.bot.latency_stats['cancel_replace_cycles'])}
        
        订单统计:
        • 最后活跃订单数: {len(self.bot.active_orders)}
        
        延迟统计:
        """
        
        cycles = self.bot.latency_stats['cancel_replace_cycles']
        if cycles:
            avg = sum(cycles) / len(cycles)
            min_val = min(cycles)
            max_val = max(cycles)
            report += f"""
            • 平均: {avg:.1f}ms
            • 最快: {min_val:.1f}ms
            • 最慢: {max_val:.1f}ms
            """
        
        report += "\n====================\n"
        
        logger.info(report)
        
        # 写入日志文件
        with open('final_run_report.txt', 'w') as f:
            f.write(report)

def print_banner():
    """打印横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║                                                      ║
    ║      🐝 Polymarket Maker Bot - 快速启动方案 🐝       ║
    ║                                                      ║
    ║          基于2026年新规则的自动化做市机器人           ║
    ║                                                      ║
    ║      • WebSocket实时连接                            ║
    ║      • 手续费感知订单签名                            ║
    ║      • 极速撤单/重下循环 (<100ms)                   ║
    ║      • 5分钟市场T-10秒策略                          ║
    ║                                                      ║
    ║      按 Ctrl+C 停止机器人                           ║
    ║                                                      ║
    ╚══════════════════════════════════════════════════════╝
    """
    print(banner)

async def main():
    """主函数"""
    print_banner()
    
    runner = BotRunner()
    
    try:
        await runner.start()
    except KeyboardInterrupt:
        logger.info("用户中断")
    except Exception as e:
        logger.error(f"运行失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # 设置环境变量（测试用）
    if not os.getenv('POLYMARKET_PRIVATE_KEY'):
        os.environ['POLYMARKET_PRIVATE_KEY'] = 'test_private_key'
    if not os.getenv('POLYMARKET_WALLET_ADDRESS'):
        os.environ['POLYMARKET_WALLET_ADDRESS'] = '0xTestWalletAddress1234567890'
    
    # 运行机器人
    exit_code = asyncio.run(main())
    sys.exit(exit_code)