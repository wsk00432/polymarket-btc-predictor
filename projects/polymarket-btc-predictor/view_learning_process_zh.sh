#!/bin/bash
# 中文版脚本查看BTC预测器的学习过程

echo "🔍 查看BTC预测系统自我学习过程"
echo "=============================================="

cd /root/clawd/projects/polymarket-btc-predictor

# 运行中文版学习查看器
python3 learning_viewer_zh.py

echo ""
echo "📊 额外学习数据文件:"
echo "-----------------------------------"
echo "预测结果:"
ls -la prediction_outcomes.json 2>/dev/null || echo "文件尚未创建 - 等待首次结果评估"
echo ""
echo "性能日志:"
ls -la performance_log.json 2>/dev/null || echo "文件尚未创建 - 等待首次结果评估"
echo ""
echo "策略配置:"
ls -la strategy_config.json 2>/dev/null || echo "文件尚未创建 - 等待首次策略调整"
echo ""

echo "📈 要查看实时学习进度，请:"
echo "   1. 等待预测成熟 (15分钟预测窗口)"
echo "   2. 使用API记录实际结果"
echo "   3. 系统随后会分析并调整策略"
echo ""
echo "   记录结果的API调用示例:"
echo "   curl -X POST http://localhost:5000/record_outcome \\"
echo "   -H 'Content-Type: application/json' \\"
echo "   -d '{\"prediction_timestamp\": \"时间戳\", \"actual_direction\": \"UP|DOWN|HOLD\", \"actual_price_change\": 0.025, \"current_price\": 78750.0}'"