#!/bin/bash
# Script to view the learning process of BTC Predictor

echo "🔍 Viewing BTC Predictor Self-Learning Process"
echo "=============================================="

cd /root/clawd/projects/polymarket-btc-predictor

# Run the learning viewer
python3 learning_viewer.py

echo ""
echo "📊 Additional Learning Data Files:"
echo "-----------------------------------"
echo "Prediction Outcomes:"
ls -la prediction_outcomes.json 2>/dev/null || echo "File not yet created - waiting for first outcome evaluation"
echo ""
echo "Performance Log:"
ls -la performance_log.json 2>/dev/null || echo "File not yet created - waiting for first outcome evaluation"
echo ""
echo "Strategy Configuration:"
ls -la strategy_config.json 2>/dev/null || echo "File not yet created - waiting for first strategy adjustment"
echo ""

echo "📈 To see real-time learning progress, you need to:"
echo "   1. Wait for predictions to mature (15 min prediction window)"
echo "   2. Record actual outcomes using the API"
echo "   3. The system will then analyze and adjust strategies"
echo ""
echo "   Example API call to record an outcome:"
echo "   curl -X POST http://localhost:5000/record_outcome \\"
echo "   -H 'Content-Type: application/json' \\"
echo "   -d '{\"prediction_timestamp\": \"TIMESTAMP\", \"actual_direction\": \"UP|DOWN|HOLD\", \"actual_price_change\": 0.025, \"current_price\": 78750.0}'"