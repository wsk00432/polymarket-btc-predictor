#!/bin/bash
# Launch script for BTC Predictor service

echo "🚀 Launching BTC Predictor Service..."

# Navigate to project directory
cd /root/clawd/projects/polymarket-btc-predictor

# Install dependencies if needed
echo "📦 Installing dependencies..."
python3 -m pip install flask numpy pandas requests psutil

# Start the services
echo "⚙️ Starting BTC Predictor services..."
python3 start_service.py start

# Wait a moment for services to initialize
sleep 5

# Display dashboard
echo "📊 Service status:"
python3 dashboard.py

echo ""
echo "🤖 自学习系统信息:"
echo "   查看学习过程 (中文): ./view_learning_process_zh.sh"
echo "   查看详细仪表板 (中文): python3 learning_viewer_zh.py"
echo "   查看学习过程 (English): ./view_learning_process.sh"
echo "   查看详细仪表板 (English): python3 learning_viewer.py"
echo ""
echo "✅ BTC预测系统现在正在运行!"
echo "🌐 Web API地址: http://localhost:5000"
echo "📈 查看仪表板: cd /root/clawd/projects/polymarket-btc-predictor && python3 dashboard.py"