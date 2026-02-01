#!/usr/bin/env node
// Script to get binance radar status and format it for messaging

const { execSync } = require('child_process');

function getRadarStatus() {
  try {
    const statusOutput = execSync('curl -s http://localhost:8080/api/status', { encoding: 'utf8' });
    const status = JSON.parse(statusOutput);
    
    const report = `
📊 **Binance OI Spike Radar Status Report**
    
📈 Running: ${status.running ? '✅ Yes' : '❌ No'}
💰 Symbols Monitored: ${status.symbols}
🔄 Scans Completed: ${status.scanned_symbols_count}/${status.scanned_symbols_total}
⚡ Requests Success/Fail: ${status.request_ok}/${status.request_fail}
⏱️ Avg Latency: ${(status.avg_scan_latency_ms / 1000).toFixed(2)}s
🕒 Uptime: ${Math.floor(status.uptime_seconds / 3600)}h ${Math.floor((status.uptime_seconds % 3600) / 60)}m

Last scan: ${new Date(status.last_scan_ts * 1000).toLocaleString()}
    `;
    
    console.log(report);
  } catch (error) {
    console.error('Error getting radar status:', error.message);
  }
}

getRadarStatus();