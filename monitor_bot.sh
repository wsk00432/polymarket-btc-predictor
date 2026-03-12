#!/bin/bash
# Polymarket Maker Bot 监控脚本

echo "🐝 Polymarket Maker Bot 监控面板"
echo "================================="

# 检查机器人是否在运行
if pgrep -f "python phase1_fixed.py" > /dev/null; then
    echo "✅ 机器人正在运行"
    
    # 获取进程信息
    PID=$(pgrep -f "python phase1_fixed.py")
    echo "进程ID: $PID"
    
    # 检查运行时间
    START_TIME=$(ps -o lstart= -p $PID)
    echo "启动时间: $START_TIME"
    
    # 检查日志文件
    LOG_FILE="polymarket_maker_test.log"
    if [ -f "$LOG_FILE" ]; then
        echo "📊 日志文件: $LOG_FILE"
        echo "最近日志:"
        tail -5 "$LOG_FILE"
    else
        echo "📝 日志文件不存在"
    fi
    
    # 检查性能报告
    echo ""
    echo "🔍 搜索性能报告..."
    if [ -f "$LOG_FILE" ]; then
        grep -A 10 "⚡ 性能报告" "$LOG_FILE" | tail -15
    fi
    
    # 检查T-10秒策略触发
    echo ""
    echo "🎯 搜索T-10秒策略..."
    if [ -f "$LOG_FILE" ]; then
        grep -B 2 -A 5 "T-10秒策略触发" "$LOG_FILE" | tail -10
    fi
    
    # 检查模拟订单
    echo ""
    echo "📦 搜索模拟订单..."
    if [ -f "$LOG_FILE" ]; then
        grep -B 1 -A 3 "模拟挂单成功" "$LOG_FILE" | tail -10
    fi
    
else
    echo "❌ 机器人未运行"
    echo ""
    echo "启动命令:"
    echo "  source venv/bin/activate"
    echo "  python phase1_fixed.py"
fi

echo ""
echo "================================="
echo "监控命令:"
echo "• 实时日志: tail -f polymarket_maker_test.log"
echo "• 性能报告: grep '⚡ 性能报告' polymarket_maker_test.log"
echo "• 停止机器人: pkill -f 'python phase1_fixed.py'"
echo "================================="

# 显示当前时间信息
echo ""
echo "⏰ 当前时间信息:"
python3 -c "
from datetime import datetime, timedelta
now = datetime.now()
print(f'当前时间: {now.strftime(\"%H:%M:%S\")}')

# 计算下一个5分钟市场
minute = now.minute
remainder = minute % 5
minutes_to_next = 5 - remainder if remainder > 0 else 0

if minutes_to_next == 0:
    market_time = now.replace(second=0, microsecond=0)
else:
    market_time = now.replace(minute=minute + minutes_to_next, second=0, microsecond=0)

market_id = f'btc-5min-{market_time.hour:02d}{market_time.minute:02d}'
window_end = market_time + timedelta(minutes=5)
time_to_end = (window_end - now).total_seconds()

print(f'下一个市场: {market_id}')
print(f'市场开始: {market_time.strftime(\"%H:%M\")}')
print(f'窗口结束: {window_end.strftime(\"%H:%M:%S\")}')
print(f'剩余时间: {time_to_end:.0f}秒')

# T-10秒信息
if time_to_end > 15:
    seconds_until_t10 = time_to_end - 15
    t10_time = window_end - timedelta(seconds=10)
    print(f'T-10秒时间: {t10_time.strftime(\"%H:%M:%S\")}')
    print(f'距离T-10秒: {seconds_until_t10:.0f}秒')
elif 10 < time_to_end <= 15:
    print('🎯 T-10秒策略: 应该正在执行!')
else:
    print('⏸️ T-10秒策略: 已过执行时间')
"