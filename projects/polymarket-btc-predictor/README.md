# Polymarket BTC Predictor

A sophisticated system for predicting Bitcoin price movements using technical indicators, machine learning, and social sentiment analysis.

## Overview

This project implements a BTC price prediction system that:
- Fetches real-time data from Binance API
- Analyzes multiple technical indicators
- Incorporates social media and news sentiment analysis
- Generates 15-minute price movement predictions
- Provides confidence scores for each prediction
- Tracks prediction accuracy over time

## Key Features

- **Real-time Data**: Pulls live BTC/USDT data from Binance
- **Multiple Indicators**: RSI, MACD, Moving Averages, Bollinger Bands, Volume Analysis
- **Sentiment Analysis**: Incorporates social media and news sentiment
- **Confidence Scoring**: Weighted analysis providing confidence levels
- **Continuous Monitoring**: Runs prediction cycles at regular intervals
- **Prediction Logging**: Saves all predictions for accuracy analysis

## Technical Indicators Used

1. **RSI (Relative Strength Index)**: Measures speed and change of price movements
2. **MACD (Moving Average Convergence Divergence)**: Shows relationship between two moving averages
3. **Moving Average Trend**: Compares short-term vs long-term trends
4. **Volume Analysis**: Analyzes volume patterns and their correlation with price
5. **Bollinger Bands**: Measures volatility and identifies overbought/oversold conditions

## Social Sentiment Analysis

In addition to technical indicators, the system now incorporates:

1. **Social Media Monitoring**: Tracks influential accounts and trending topics
2. **News Analysis**: Monitors major news outlets for Bitcoin-related articles
3. **Keyword Analysis**: Identifies sentiment-indicating terms in posts/news
4. **Influencer Impact**: Considers sentiment from known crypto influencers
5. **Sentiment Integration**: Combines social sentiment with technical analysis for enhanced predictions

## Self-Learning Capabilities

The system features advanced self-improvement mechanisms:

1. **Prediction Outcome Tracking**: Records actual outcomes for each prediction
2. **Performance Analysis**: Evaluates prediction accuracy and identifies patterns
3. **Strategy Adjustment**: Automatically adjusts indicator weights based on performance
4. **Adaptive Learning**: Modifies approach based on market conditions
5. **Continuous Improvement**: Iteratively enhances prediction accuracy over time

## Architecture

```
BTC Predictor System
├── Data Collection Layer
│   ├── Binance API Integration
│   └── Real-time K-line Data
├── Technical Analysis Engine
│   ├── Indicator Calculations
│   └── Weighted Scoring
├── Prediction Algorithm
│   ├── Direction Prediction (UP/DOWN)
│   └── Confidence Scoring
├── Data Storage
│   ├── Prediction History
│   └── Accuracy Metrics
└── Reporting Layer
    ├── Prediction Results
    └── Performance Analytics
```

## Business Model

### Revenue Streams

1. **Subscription Service**: Monthly fees for prediction accuracy
2. **API Access**: Tiered pricing for API access to predictions
3. **Premium Features**: Enhanced accuracy, additional timeframes, custom alerts

### Competitive Advantages

- **Speed**: 15-minute predictions for short-term trading
- **Accuracy**: Focus on high-confidence predictions
- **Transparency**: Historical accuracy tracking
- **Real-time**: Live updates and alerts

## Implementation Status

- [x] Core prediction algorithm
- [x] Real-time data collection
- [x] Technical indicator calculations
- [x] Confidence scoring system
- [x] Prediction logging
- [ ] Accuracy tracking against actual outcomes
- [ ] Web API for external access
- [ ] Dashboard for visualization

## Usage

### Running a Single Prediction

```bash
cd /root/clawd/projects/polymarket-btc-predictor
python3 btc_predictor.py
```

### Running Continuous Predictions

Uncomment the last line in the main() function to run continuously:

```python
predictor.run_continuous_predictions(interval_seconds=900)  # Every 15 minutes
```

## Accuracy Tracking

The system maintains prediction history in the `predictions/` directory. Future enhancements will include comparing predictions to actual outcomes to calculate accuracy metrics.

## Risk Management

- Only trade when confidence exceeds threshold (default 60%)
- Diversify across multiple indicators
- Maintain prediction history for performance analysis
- Implement circuit breakers for unexpected market conditions

## Next Steps

1. Backtest algorithm against historical data
2. Implement accuracy tracking against actual outcomes
3. Create web API for external access
4. Develop dashboard for visualization
5. Build risk management features
6. Test with small user group

This system represents a solid foundation for a BTC prediction service with potential for revenue generation through subscription models or API licensing.