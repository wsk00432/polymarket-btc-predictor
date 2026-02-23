# Enhanced Trading Analysis System

This project implements an advanced cryptocurrency trading analysis system that combines technical indicators with Open Interest (OI) spike detection to generate comprehensive trading signals.

## Architecture

The system consists of two main components:

1. **OI Radar Services** (ports 8080 and 8081)
2. **Enhanced Trading Analysis System**

## Running the Systems

### 1. Start the OI Radar Services

#### Enhanced OI Radar (Recommended)
```bash
cd /root/clawd/oi_radar_enhanced
python3 app.py
```
This runs on port 8081 and provides advanced OI spike detection.

#### Original OI Radar (Legacy)
```bash
cd /root/clawd/oi_radar
python3 app.py
```
This runs on port 8080 with basic functionality.

### 2. Run the Trading Analysis System

```bash
cd /root/clawd/enhanced_trading_system
python3 monitor.py
```

This will start continuous monitoring of BTCUSDT, ETHUSDT, and SOLUSDT with updates every 30 seconds.

## Key Features

- **Technical Analysis**: RSI, MACD, Bollinger Bands, Moving Averages
- **OI Spike Detection**: Advanced algorithms for detecting unusual OI changes
- **Risk Management**: Dynamic stop-loss and take-profit calculations
- **Composite Scoring**: Weighted algorithm combining multiple factors
- **Real-time Monitoring**: Continuous analysis with regular updates

## Signal Types

- STRONG_BUY, BUY: Positive market movement expected
- HOLD: Neutral market conditions
- SELL, STRONG_SELL: Negative market movement expected

Confidence levels and risk management parameters are provided with each signal.

## Project Structure

- `/oi_radar_enhanced/` - Enhanced OI spike detection service
- `/enhanced_trading_system/` - Main trading analysis system
- `PROJECT_SUMMARY.md` - Detailed project overview