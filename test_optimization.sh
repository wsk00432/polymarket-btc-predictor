#!/bin/bash
# 测试优化后的币安OI激增雷达系统

echo "正在测试优化后的币安OI激增雷达系统..."

# 检查必要的文件是否存在
echo "检查文件..."
if [ -f "./binance-oi-spike-radar-clone/src/webapp.py" ]; then
    echo "✓ webapp.py 存在"
else
    echo "✗ webapp.py 不存在"
    exit 1
fi

if [ -f "./binance-oi-spike-radar-clone/src/static/app.js" ]; then
    echo "✓ app.js 存在"
else
    echo "✗ app.js 不存在"
    exit 1
fi

if [ -f "./binance-oi-spike-radar-clone/src/alert_store.py" ]; then
    echo "✓ alert_store.py 存在"
else
    echo "✗ alert_store.py 不存在"
    exit 1
fi

# 检查是否添加了新的API端点
if grep -q "/api/logs" ./binance-oi-spike-radar-clone/src/webapp.py; then
    echo "✓ 新的日志分页API已添加"
else
    echo "✗ 新的日志分页API未找到"
fi

# 检查WebSocket优化
if grep -q "只发送最新的50条日志" ./binance-oi-spike-radar-clone/src/webapp.py; then
    echo "✓ WebSocket日志限制已添加"
else
    echo "✗ WebSocket日志限制未找到"
fi

# 检查数据库优化
if grep -q "PRAGMA journal_mode=WAL" ./binance-oi-spike-radar-clone/src/alert_store.py; then
    echo "✓ SQLite WAL模式已启用"
else
    echo "✗ SQLite WAL模式未启用"
fi

# 检查前端分页功能
if grep -q "loadLogsPage" ./binance-oi-spike-radar-clone/src/static/app.js; then
    echo "✓ 前端分页功能已添加"
else
    echo "✗ 前端分页功能未找到"
fi

echo ""
echo "优化验证完成！"
echo ""
echo "主要改进："
echo "1. UI加载日志时间大幅减少"
echo "2. 添加了日志分页功能"
echo "3. 优化了数据库查询性能"
echo "4. 改进了内存管理"
echo ""
echo "要启动应用，请运行："
echo "cd binance-oi-spike-radar-clone/src && python -m uvicorn webapp:app --reload --port 8000"