#!/usr/bin/env python3
"""
BTC Price Movement Predictor
Predicts 15-minute Bitcoin price movements using technical indicators and ML
"""

import time
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BTCPredictor:
    def __init__(self):
        self.binance_endpoint = "https://api.binance.com/api/v3/klines"
        self.symbol = "BTCUSDT"
        self.interval = "1m"  # 1 minute candles
        self.lookback_minutes = 15  # For prediction
        self.prediction_window = 15  # Predict next 15 minutes
        self.confidence_threshold = 0.6  # Minimum confidence to trade
        self.data_buffer = []
        self.max_buffer_size = 1000  # Maximum data points to keep
        
        # Technical indicator weights
        self.weights = {
            'rsi': 0.25,
            'macd': 0.25,
            'ma_trend': 0.2,
            'volume': 0.15,
            'bollinger': 0.15
        }
        
        # Import production-ready sentiment analyzer (using reliable real data sources)
        # CRITICAL: Only use real data sources, never use simulated data
        try:
            from production_sentiment_analyzer import ProductionSentimentAnalyzer
            self.sentiment_analyzer = ProductionSentimentAnalyzer()
            self.use_sentiment = True
            logger.info("Production Sentiment Analyzer loaded (using reliable real data sources)")
        except ImportError:
            # Fallback to real-time sentiment analyzer if production one fails
            try:
                from real_time_sentiment_analyzer import RealTimeSentimentAnalyzer
                self.sentiment_analyzer = RealTimeSentimentAnalyzer()
                self.use_sentiment = True
                logger.info("Real-time Sentiment Analyzer loaded (using real data sources)")
            except ImportError:
                # DO NOT use message_sentiment_analyzer as it contains simulated data
                # Only disable sentiment analysis rather than using simulated data
                self.sentiment_analyzer = None
                self.use_sentiment = False
                logger.warning("No real-data sentiment analyzer available, sentiment analysis disabled to prevent simulated data usage")
        
        # Import self-learning module
        try:
            from self_learning_module import SelfLearningModule
            self.learning_module = SelfLearningModule()
            self.use_learning = True
            logger.info("Self-Learning Module loaded")
        except ImportError:
            self.learning_module = None
            self.use_learning = False
            logger.warning("Self-Learning Module not available")
        
        logger.info("BTC Predictor initialized")
    
    def fetch_kline_data(self, limit: int = 100) -> List[Dict]:
        """
        Fetch kline/candlestick data from Binance
        """
        try:
            params = {
                'symbol': self.symbol,
                'interval': self.interval,
                'limit': limit
            }
            response = requests.get(self.binance_endpoint, params=params)
            response.raise_for_status()
            
            # Parse response - Binance returns raw arrays
            raw_data = response.json()
            
            # Convert to structured format
            columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                      'close_time', 'quote_asset_volume', 'num_trades', 
                      'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore']
            
            df = pd.DataFrame(raw_data, columns=columns)
            
            # Convert to numeric
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Convert to dict format
            data = []
            for _, row in df.iterrows():
                data.append({
                    'timestamp': row['timestamp'],
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume'])
                })
            
            logger.info(f"Fetched {len(data)} klines from Binance")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching kline data: {e}")
            return []
    
    def calculate_rsi(self, closes: List[float], window: int = 14) -> float:
        """
        Calculate Relative Strength Index
        """
        if len(closes) < window + 1:
            return 50.0  # Neutral if insufficient data
        
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-window:])
        avg_loss = np.mean(losses[-window:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)
    
    def calculate_macd(self, closes: List[float]) -> Tuple[float, float, float]:
        """
        Calculate MACD indicator
        """
        if len(closes) < 26:
            return 0.0, 0.0, 0.0
        
        closes = np.array(closes)
        ema12 = pd.Series(closes).ewm(span=12).mean().iloc[-1]
        ema26 = pd.Series(closes).ewm(span=26).mean().iloc[-1]
        macd_line = ema12 - ema26
        
        signal_line = pd.Series([macd_line]).ewm(span=9).mean().iloc[-1] if len(closes) >= 35 else macd_line
        histogram = macd_line - signal_line
        
        return float(macd_line), float(signal_line), float(histogram)
    
    def calculate_moving_average_trend(self, closes: List[float], short_window: int = 10, long_window: int = 20) -> float:
        """
        Calculate moving average trend indicator
        """
        if len(closes) < long_window:
            return 0.0
        
        short_ma = np.mean(closes[-short_window:])
        long_ma = np.mean(closes[-long_window:])
        
        # Return normalized difference
        if long_ma != 0:
            return float((short_ma - long_ma) / long_ma)
        return 0.0
    
    def calculate_bollinger_bands(self, closes: List[float], window: int = 20, num_std: int = 2) -> Tuple[float, float, float]:
        """
        Calculate Bollinger Bands
        """
        if len(closes) < window:
            return float(np.mean(closes)), float(np.mean(closes)), float(np.mean(closes))
        
        prices = np.array(closes[-window:])
        sma = np.mean(prices)
        std = np.std(prices)
        
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        return float(upper_band), float(sma), float(lower_band)
    
    def calculate_volume_indicator(self, volumes: List[float], closes: List[float]) -> float:
        """
        Calculate volume-based indicator
        """
        if len(volumes) < 2:
            return 0.0
        
        recent_avg_vol = np.mean(volumes[-5:])
        prev_avg_vol = np.mean(volumes[-10:-5])
        
        if prev_avg_vol != 0:
            volume_change = (recent_avg_vol - prev_avg_vol) / prev_avg_vol
        else:
            volume_change = 0.0
        
        # Combine with price change
        recent_price_change = (closes[-1] - closes[-2]) / closes[-2] if len(closes) > 1 else 0.0
        
        return float(volume_change * recent_price_change)
    
    def analyze_technical_indicators(self, data: List[Dict]) -> Dict[str, float]:
        """
        Analyze technical indicators for prediction
        """
        if len(data) < 30:  # Need sufficient data
            return {
                'rsi': 50.0,
                'macd_histogram': 0.0,
                'ma_trend': 0.0,
                'volume_indicator': 0.0,
                'bollinger_position': 0.5,
                'momentum': 0.0
            }
        
        closes = [float(item['close']) for item in data]
        volumes = [float(item['volume']) for item in data]
        
        # Calculate indicators
        rsi = self.calculate_rsi(closes)
        macd_line, signal_line, histogram = self.calculate_macd(closes)
        ma_trend = self.calculate_moving_average_trend(closes)
        volume_indicator = self.calculate_volume_indicator(volumes, closes)
        
        # Bollinger Bands position (where price sits relative to bands)
        upper, middle, lower = self.calculate_bollinger_bands(closes)
        current_price = closes[-1]
        
        if upper != lower:
            bb_position = (current_price - lower) / (upper - lower)
        else:
            bb_position = 0.5  # Neutral if bands are equal
        
        # Momentum indicator
        if len(closes) >= 5:
            momentum = (closes[-1] - closes[-5]) / closes[-5]
        else:
            momentum = 0.0
        
        return {
            'rsi': rsi,
            'macd_histogram': histogram,
            'ma_trend': ma_trend,
            'volume_indicator': volume_indicator,
            'bollinger_position': bb_position,
            'momentum': momentum
        }
    
    def generate_prediction(self, indicators: Dict[str, float]) -> Tuple[str, float, Dict]:
        """
        Generate prediction based on technical indicators
        """
        # Calculate weighted score
        score = 0.0
        
        # RSI: Overbought/oversold
        if indicators['rsi'] < 30:  # Oversold, likely to go UP
            score += self.weights['rsi'] * 1.0
        elif indicators['rsi'] > 70:  # Overbought, likely to go DOWN
            score -= self.weights['rsi'] * 1.0
        else:  # Neutral RSI
            score += self.weights['rsi'] * 0.0
        
        # MACD histogram
        score += self.weights['macd'] * np.clip(indicators['macd_histogram'] * 5, -1, 1)
        
        # Moving average trend
        score += self.weights['ma_trend'] * np.clip(indicators['ma_trend'] * 10, -1, 1)
        
        # Volume indicator
        score += self.weights['volume'] * np.clip(indicators['volume_indicator'] * 10, -1, 1)
        
        # Bollinger Bands position
        if indicators['bollinger_position'] < 0.2:  # Below 20%, likely to go UP
            score += self.weights['bollinger'] * 1.0
        elif indicators['bollinger_position'] > 0.8:  # Above 80%, likely to go DOWN
            score -= self.weights['bollinger'] * 1.0
        else:
            score += self.weights['bollinger'] * 0.0
        
        # Overall momentum
        score += 0.1 * np.clip(indicators['momentum'] * 10, -1, 1)
        
        # Convert to confidence and direction
        confidence = min(abs(score), 1.0)  # Confidence is absolute score, capped at 1.0
        direction = "UP" if score > 0 else "DOWN"
        
        return direction, confidence, indicators
    
    def predict_next_movement(self) -> Dict:
        """
        Main prediction method - predicts next 15-minute movement
        """
        logger.info("Fetching latest market data...")
        data = self.fetch_kline_data(limit=50)  # Get last 50 minutes of data
        
        if not data:
            logger.error("Failed to fetch market data")
            return {
                'prediction': 'HOLD',
                'confidence': 0.0,
                'timestamp': datetime.now().isoformat(),
                'reason': 'No data available'
            }
        
        # Analyze technical indicators
        indicators = self.analyze_technical_indicators(data)
        
        # Generate base prediction from technical analysis
        direction, confidence, analyzed_indicators = self.generate_prediction(indicators)
        
        # Integrate sentiment analysis if available
        if self.use_sentiment and self.sentiment_analyzer:
            try:
                sentiment_result = self.sentiment_analyzer.integrate_with_prediction(confidence, direction)
                final_direction = sentiment_result['final_direction']
                final_confidence = sentiment_result['final_confidence']
                sentiment_data = sentiment_result['sentiment_data']
            except Exception as e:
                logger.error(f"Error in sentiment analysis: {e}")
                # Fall back to technical-only prediction
                final_direction = direction
                final_confidence = confidence
                sentiment_data = None
        else:
            # Use technical analysis only
            final_direction = direction
            final_confidence = confidence
            sentiment_data = None
        
        # Only predict if confidence is high enough
        if final_confidence < self.confidence_threshold:
            prediction = 'HOLD'
            if sentiment_data:
                reason = f'Low confidence: {final_confidence:.2f}, Tech: {direction}({confidence:.2f}), Sentiment: {sentiment_data["combined_sentiment"]:.2f}'
            else:
                reason = f'Low confidence: {final_confidence:.2f}, Tech: {direction}({confidence:.2f})'
        else:
            prediction = final_direction
            if sentiment_data:
                reason = f'Confidence: {final_confidence:.2f}, Tech: {direction}({confidence:.2f}), Sentiment: {sentiment_data["combined_sentiment"]:.2f}'
            else:
                reason = f'Confidence: {final_confidence:.2f}, Tech: {direction}({confidence:.2f})'
        
        result = {
            'prediction': prediction,
            'confidence': final_confidence,
            'timestamp': datetime.now().isoformat(),
            'current_price': data[-1]['close'],
            'indicators': analyzed_indicators,
            'reason': reason,
            'prediction_window_minutes': self.prediction_window,
            'technical_analysis': {
                'direction': direction,
                'confidence': confidence
            }
        }
        
        # Add sentiment data if available
        if sentiment_data:
            result['sentiment_analysis'] = sentiment_data
        
        logger.info(f"Prediction: {prediction}, Confidence: {final_confidence:.3f}, Current Price: {data[-1]['close']}")
        
        return result
    
    def run_continuous_predictions(self, interval_seconds: int = 60):
        """
        Run continuous prediction cycles
        """
        logger.info(f"Starting continuous prediction service, checking every {interval_seconds}s")
        
        # Import PredictionManager to record predictions for evaluation
        from prediction_manager import PredictionManager
        manager = PredictionManager()
        
        while True:
            try:
                prediction = self.predict_next_movement()
                
                # Log prediction
                logger.info(f"Prediction: {prediction['prediction']}, "
                           f"Confidence: {prediction['confidence']:.3f}, "
                           f"Price: ${prediction['current_price']}")
                
                # Save to individual file (original functionality)
                self.save_prediction(prediction)
                
                # ALSO record with PredictionManager for outcome tracking and learning
                try:
                    manager.record_prediction_for_evaluation(prediction)
                except Exception as e:
                    logger.error(f"Error recording prediction for evaluation: {e}")
                
                # Wait before next prediction
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Prediction service interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in prediction cycle: {e}")
                time.sleep(10)  # Wait 10 seconds before retrying
    
    def save_prediction(self, prediction: Dict):
        """
        Save prediction to local storage
        """
        # Create predictions directory if it doesn't exist
        os.makedirs('/root/clawd/projects/polymarket-btc-predictor/predictions', exist_ok=True)
        
        filename = f'/root/clawd/projects/polymarket-btc-predictor/predictions/btc_pred_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(filename, 'w') as f:
            json.dump(prediction, f, indent=2)
    
    def get_accuracy_stats(self) -> Dict:
        """
        Calculate accuracy statistics from saved predictions
        Note: This is simplified - in practice, you'd compare predictions to actual outcomes
        """
        pred_dir = '/root/clawd/projects/polymarket-btc-predictor/predictions'
        if not os.path.exists(pred_dir):
            return {'total_predictions': 0, 'accuracy': 0.0}
        
        prediction_files = [f for f in os.listdir(pred_dir) if f.startswith('btc_pred_')]
        
        # This is a placeholder - in real implementation you'd track actual outcomes
        # and calculate accuracy against them
        return {
            'total_predictions': len(prediction_files),
            'accuracy': 'N/A - Actual outcome tracking required'
        }

def main():
    predictor = BTCPredictor()
    
    # For initial testing, just make one prediction
    print("Making initial BTC price movement prediction...")
    prediction = predictor.predict_next_movement()
    
    print(f"\nPrediction Result:")
    print(f"Direction: {prediction['prediction']}")
    print(f"Confidence: {prediction['confidence']:.3f}")
    print(f"Current Price: ${prediction['current_price']}")
    print(f"Timestamp: {prediction['timestamp']}")
    print(f"Reason: {prediction['reason']}")
    
    print(f"\nTechnical Indicators:")
    for key, value in prediction['indicators'].items():
        print(f"  {key}: {value:.4f}")
    
    print(f"\nAccuracy Tracking: {predictor.get_accuracy_stats()}")
    
    # Uncomment the next line to run continuous predictions
    # predictor.run_continuous_predictions(interval_seconds=900)  # Every 15 minutes

if __name__ == "__main__":
    main()