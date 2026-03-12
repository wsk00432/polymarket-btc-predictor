#!/bin/bash
# T-10秒策略触发倒计时监控

echo "🐝 Polymarket Maker Bot T-10秒触发倒计时监控"
echo "=========================================="

# 检查机器人是否运行
if pgrep -f "python corrected_phase1.py" > /dev/null; then
    PID=$(pgrep -f "python corrected_phase1.py")
    echo "✅ 机器人正在运行 (PID: $PID)"
else
    echo "❌ 机器人未运行"
    echo "启动命令: source venv/bin/activate && python corrected_phase1.py"
    exit 1
fi

echo ""
echo "⏰ 倒计时开始..."
echo "=========================================="

# 持续监控直到触发
while true; do
    clear
    echo "🐝 Polymarket Maker Bot T-10秒触发倒计时监控"
    echo "=========================================="
    echo "监控时间: $(date '+%H:%M:%S')"
    echo ""
    
    # 计算下一个触发时间
    python3 -c "
from datetime import datetime, timedelta

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

market_id = f'btc-5min-{market_time.hour:02d}{market_time.minute:02d}'
window_end = market_time + timedelta(minutes=5)
time_to_end = (window_end - now).total_seconds()

# 修复后的触发逻辑
trigger_buffer = 0.5
lower_bound = 10 - trigger_buffer  # 9.5秒
upper_bound = 15 - trigger_buffer  # 14.5秒

t10_start = window_end - timedelta(seconds=upper_bound)
t10_end = window_end - timedelta(seconds=lower_bound)

print('📊 当前市场状态:')
print(f'  当前市场: {market_id}')
print(f'  市场开始: {market_time.strftime(\"%H:%M\")}')
print(f'  窗口结束: {window_end.strftime(\"%H:%M:%S\")}')
print(f'  剩余时间: {time_to_end:.0f}秒')
print()
print('🎯 T-10秒触发:')
print(f'  触发条件: {lower_bound:.1f} <= 剩余时间 <= {upper_bound:.1f}')
print(f'  触发时间: {t10_start.strftime(\"%H:%M:%S\")} 到 {t10_end.strftime(\"%H:%M:%S\")}')
print()

if lower_bound <= time_to_end <= upper_bound:
    print('🚨 🎯 🚨 T-10秒策略正在触发! 🚨 🎯 🚨')
    print(f'  剩余时间: {time_to_end:.1f}秒')
    print('  机器人应该正在执行双边挂单策略')
    print('  请查看机器人控制台输出确认')
elif time_to_end > upper_bound:
    seconds_until = time_to_end - upper_bound
    minutes = int(seconds_until // 60)
    seconds = int(seconds_until % 60)
    
    print(f'⏳ 等待触发:')
    print(f'  距离触发: {seconds_until:.0f}秒 ({minutes}分{seconds}秒)')
    print(f'  预计触发: {t10_start.strftime(\"%H:%M:%S\")}')
else:
    print('⏸️ 触发时间已过')
    print('  等待下一个5分钟市场')
    
print()
print('📋 监控命令:')
print('  • 查看日志: 机器人控制台输出')
print('  • 停止监控: Ctrl+C')
print('  • 停止机器人: pkill -f \"python corrected_phase1.py\"')
"
    
    # 检查是否在触发时间内
    python3 -c "
from datetime import datetime, timedelta

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
time_to_end = (window_end - now).total_seconds()

trigger_buffer = 0.5
lower_bound = 10 - trigger_buffer
upper_bound = 15 - trigger_buffer

if lower_bound <= time_to_end <= upper_bound:
    # 在触发时间内，快速刷新
    sleep_time=0.5
else:
    # 不在触发时间内，慢速刷新
    sleep_time=2
print(sleep_time)
" > /tmp/sleep_time.txt
    
    sleep_time=$(cat /tmp/sleep_time.txt)
    
    # 等待
    sleep $sleep_time
done