#!/bin/bash
# Health check script for BTC Predictor service

LOG_FILE="/root/clawd/projects/polymarket-btc-predictor/service_health.log"
API_URL="http://localhost:5000/health"

# Log timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') - Checking service health..." >> $LOG_FILE

# Check if API is responding
if curl -s --max-time 10 $API_URL > /dev/null; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Service is healthy" >> $LOG_FILE
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Service is unhealthy, restarting..." >> $LOG_FILE
    cd /root/clawd/projects/polymarket-btc-predictor && python3 start_service.py start >> $LOG_FILE 2>&1
fi