#!/bin/bash
cd /root/clawd/binance-oi-spike-radar-clone
source .venv/bin/activate
nohup python -m src.main > app.log 2>&1 &
echo $! > app.pid
echo "Binance OI Spike Radar started on port 8000"
echo "PID saved to app.pid"
echo "Check logs with: tail -f /root/clawd/binance-oi-spike-radar-clone/app.log"