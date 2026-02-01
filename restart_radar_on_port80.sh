#!/bin/bash
cd /root/clawd/binance-oi-spike-radar-clone
source .venv/bin/activate

# 尝试使用sudo运行在80端口（如果权限允许）
# 否则在其他常用端口运行
if [ "$EUID" -eq 0 ]; then
  # 如果是root用户，尝试绑定到80端口
  nohup python -c "
import uvicorn
from src.webapp import app
uvicorn.run(app, host='0.0.0.0', port=8080, log_level='info')
" > app.log 2>&1 &
else
  # 普通用户只能使用大于1024的端口
  nohup python -c "
import uvicorn
from src.webapp import app
uvicorn.run(app, host='0.0.0.0', port=8080, log_level='info')
" > app.log 2>&1 &
fi

echo $! > app.pid
echo "Binance OI Spike Radar started on port 8080"
echo "PID saved to app.pid"
echo "Check logs with: tail -f /root/clawd/binance-oi-spike-radar-clone/app.log"