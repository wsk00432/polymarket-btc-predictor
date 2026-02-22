#!/usr/bin/env python3
"""
Self-Learning Module for BTC Predictor
Implements prediction result analysis, self-evaluation, and strategy adjustment
"""

import json
import os
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

class SelfLearningModule:
    def __init__(self):
        self.prediction_history_path = "/root/clawd/projects/polymarket-btc-predictor/predictions"
        self.performance_log_path = "/root/clawd/projects/polymarket-btc-predictor/performance_log.json"
        self.strategy_config_path = "/root/clawd/projects/polymarket-btc-predictor/strategy_config.json"
        
        # Initialize performance tracking
        self.performance_metrics = {
            'total_predictions': 0,
            'correct_predictions': 0,
            'accuracy_rate': 0.0,
            'by_strategy': {},
            'by_timeframe': {},
            'by_market_condition': {}
        }
        
        # Load or initialize strategy configuration
        self.strategy_config = self._load_strategy_config()
        
        # Performance thresholds for strategy adjustment
        self.adjustment_thresholds = {
            'accuracy_drop': 0.05,  # Trigger adjustment if accuracy drops by 5%
            'low_performance_streak': 5,  # Adjust after 5 consecutive poor predictions
            'high_accuracy_streak': 10  # Increase confidence after 10 consecutive good predictions
        }
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Self-Learning Module initialized")
    
    def _load_strategy_config(self) -> Dict:
        """Load strategy configuration or create default"""
        if os.path.exists(self.strategy_config_path):
            with open(self.strategy_config_path, 'r') as f:
                return json.load(f)
        else:
            # Default strategy configuration
            default_config = {
                'indicator_weights': {
                    'rsi': 0.25,
                    'macd': 0.25,
                    'ma_trend': 0.2,
                    'volume': 0.15,
                    'bollinger': 0.15
                },
                'sentiment_weight': 0.3,
                'confidence_threshold': 0.6,
                'learning_rate': 0.1,
                'adjustment_sensitivity': 0.05
            }
            self._save_strategy_config(default_config)
            return default_config
    
    def _save_strategy_config(self, config: Dict):
        """Save strategy configuration"""
        with open(self.strategy_config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _load_performance_log(self) -> List[Dict]:
        """Load performance log or create empty list"""
        if os.path.exists(self.performance_log_path):
            with open(self.performance_log_path, 'r') as f:
                return json.load(f)
        else:
            return []
    
    def _save_performance_log(self, log: List[Dict]):
        """Save performance log"""
        with open(self.performance_log_path, 'w') as f:
            json.dump(log, f, indent=2)
    
    def record_prediction_result(self, prediction_data: Dict, actual_outcome: Optional[str] = None, actual_price_change: Optional[float] = None):
        """
        Record prediction result and perform self-analysis
        """
        self.logger.info(f"Recording prediction result for analysis")
        
        # Create a comprehensive record
        record = {
            'timestamp': prediction_data['timestamp'],
            'predicted_direction': prediction_data['prediction'],
            'predicted_confidence': prediction_data['confidence'],
            'actual_direction': actual_outcome,
            'actual_price_change': actual_price_change,
            'current_price': prediction_data['current_price'],
            'indicators': prediction_data.get('indicators', {}),
            'sentiment_analysis': prediction_data.get('sentiment_analysis', {}),
            'technical_analysis': prediction_data.get('technical_analysis', {}),
            'prediction_window_minutes': prediction_data.get('prediction_window_minutes', 15),
            'analysis': {}
        }
        
        # Perform self-analysis if actual outcome is provided
        if actual_outcome is not None:
            analysis = self._analyze_prediction_performance(record)
            record['analysis'] = analysis
            
            # Update performance metrics
            self._update_performance_metrics(record)
            
            # Evaluate if strategy adjustment is needed
            adjustment_needed = self._evaluate_adjustment_needed()
            
            if adjustment_needed:
                self._adjust_strategy()
        
        # Add to performance log
        log = self._load_performance_log()
        log.append(record)
        
        # Keep only recent records (last 1000)
        if len(log) > 1000:
            log = log[-1000:]
        
        self._save_performance_log(log)
        
        return record
    
    def _analyze_prediction_performance(self, record: Dict) -> Dict:
        """
        Analyze individual prediction performance
        """
        predicted = record['predicted_direction']
        actual = record['actual_direction']
        
        # Determine if prediction was correct
        is_correct = self._is_prediction_correct(predicted, actual, record['actual_price_change'])
        record['is_correct'] = is_correct
        
        # Analyze contributing factors
        analysis = {
            'is_correct': is_correct,
            'accuracy_score': 1.0 if is_correct else 0.0,
            'prediction_strength': record['predicted_confidence'],
            'market_volatility': abs(record.get('actual_price_change', 0)),
            'technical_factors': self._analyze_technical_factors(record),
            'sentiment_factors': self._analyze_sentiment_factors(record),
            'error_type': self._classify_error_type(predicted, actual)
        }
        
        return analysis
    
    def _is_prediction_correct(self, predicted: str, actual: str, price_change: Optional[float] = None) -> bool:
        """
        Determine if prediction was correct
        """
        if predicted == 'HOLD':
            # For HOLD predictions, consider it correct if actual movement was minimal
            if price_change is not None:
                return abs(price_change) < 0.01  # Less than 1% movement
            else:
                return predicted == actual
        else:
            # For UP/DOWN predictions, check if direction matched
            return predicted == actual
    
    def _analyze_technical_factors(self, record: Dict) -> Dict:
        """
        Analyze which technical indicators contributed to the prediction
        """
        indicators = record.get('indicators', {})
        technical_analysis = record.get('technical_analysis', {})
        
        factor_analysis = {}
        
        # Analyze RSI contribution
        rsi = indicators.get('rsi', 50)
        if rsi < 30:  # Oversold
            factor_analysis['rsi_contribution'] = 'predicted_UP_due_to_oversold'
        elif rsi > 70:  # Overbought
            factor_analysis['rsi_contribution'] = 'predicted_DOWN_due_to_overbought'
        else:
            factor_analysis['rsi_contribution'] = 'neutral_rsi'
        
        # Analyze MACD contribution
        macd_hist = indicators.get('macd_histogram', 0)
        if macd_hist > 0:
            factor_analysis['macd_contribution'] = 'predicted_UP_due_to_positive_macd'
        elif macd_hist < 0:
            factor_analysis['macd_contribution'] = 'predicted_DOWN_due_to_negative_macd'
        else:
            factor_analysis['macd_contribution'] = 'neutral_macd'
        
        # Analyze moving average trend
        ma_trend = indicators.get('ma_trend', 0)
        if ma_trend > 0:
            factor_analysis['ma_contribution'] = 'predicted_UP_due_to_positive_trend'
        elif ma_trend < 0:
            factor_analysis['ma_contribution'] = 'predicted_DOWN_due_to_negative_trend'
        else:
            factor_analysis['ma_contribution'] = 'neutral_ma_trend'
        
        return factor_analysis
    
    def _analyze_sentiment_factors(self, record: Dict) -> Dict:
        """
        Analyze sentiment contribution to prediction
        """
        sentiment_data = record.get('sentiment_analysis', {})
        
        if not sentiment_data:
            return {'sentiment_impact': 'none'}
        
        combined_sentiment = sentiment_data.get('combined_sentiment', 0)
        
        if combined_sentiment > 0.1:
            return {'sentiment_impact': 'positive_sentiment_pushed_UP', 'strength': combined_sentiment}
        elif combined_sentiment < -0.1:
            return {'sentiment_impact': 'negative_sentiment_pushed_DOWN', 'strength': combined_sentiment}
        else:
            return {'sentiment_impact': 'neutral_sentiment', 'strength': combined_sentiment}
    
    def _classify_error_type(self, predicted: str, actual: str) -> str:
        """
        Classify type of prediction error
        """
        if predicted == actual:
            return 'correct_prediction'
        elif predicted == 'HOLD' and actual in ['UP', 'DOWN']:
            return 'missed_opportunity'
        elif predicted in ['UP', 'DOWN'] and actual == 'HOLD':
            return 'false_signal'
        elif predicted == 'UP' and actual == 'DOWN':
            return 'direction_inverted_UP_to_DOWN'
        elif predicted == 'DOWN' and actual == 'UP':
            return 'direction_inverted_DOWN_to_UP'
        else:
            return 'other_error'
    
    def _update_performance_metrics(self, record: Dict):
        """
        Update overall performance metrics
        """
        self.performance_metrics['total_predictions'] += 1
        
        if record['analysis']['is_correct']:
            self.performance_metrics['correct_predictions'] += 1
        
        if self.performance_metrics['total_predictions'] > 0:
            self.performance_metrics['accuracy_rate'] = (
                self.performance_metrics['correct_predictions'] / 
                self.performance_metrics['total_predictions']
            )
        
        # Update strategy-specific metrics
        strategy_key = f"tech_{record.get('technical_analysis', {}).get('direction', 'N/A')}_sent_{record.get('sentiment_analysis', {}).get('combined_sentiment', 0) > 0}"
        if strategy_key not in self.performance_metrics['by_strategy']:
            self.performance_metrics['by_strategy'][strategy_key] = {
                'total': 0,
                'correct': 0,
                'accuracy': 0.0
            }
        
        self.performance_metrics['by_strategy'][strategy_key]['total'] += 1
        if record['analysis']['is_correct']:
            self.performance_metrics['by_strategy'][strategy_key]['correct'] += 1
        
        strategy_total = self.performance_metrics['by_strategy'][strategy_key]['total']
        if strategy_total > 0:
            self.performance_metrics['by_strategy'][strategy_key]['accuracy'] = (
                self.performance_metrics['by_strategy'][strategy_key]['correct'] / strategy_total
            )
    
    def _evaluate_adjustment_needed(self) -> bool:
        """
        Evaluate if strategy adjustment is needed based on performance
        """
        # Get recent performance from log
        log = self._load_performance_log()
        recent_records = log[-20:]  # Look at last 20 predictions
        
        if len(recent_records) < 10:  # Not enough data to evaluate
            return False
        
        # Calculate recent accuracy
        recent_correct = sum(1 for r in recent_records if r['analysis']['is_correct'])
        recent_accuracy = recent_correct / len(recent_records)
        
        # Compare to overall accuracy
        overall_accuracy = self.performance_metrics['accuracy_rate']
        
        # Trigger adjustment if recent performance is significantly worse
        if overall_accuracy > 0 and (overall_accuracy - recent_accuracy) > self.adjustment_thresholds['accuracy_drop']:
            self.logger.info(f"Adjustment triggered: Recent accuracy {recent_accuracy:.3f} vs overall {overall_accuracy:.3f}")
            return True
        
        # Check for streaks of incorrect predictions
        incorrect_streak = 0
        for record in reversed(recent_records):
            if not record['analysis']['is_correct']:
                incorrect_streak += 1
            else:
                break
        
        if incorrect_streak >= self.adjustment_thresholds['low_performance_streak']:
            self.logger.info(f"Adjustment triggered: {incorrect_streak} consecutive incorrect predictions")
            return True
        
        return False
    
    def _adjust_strategy(self):
        """
        Adjust strategy based on performance analysis
        """
        self.logger.info("Adjusting strategy based on performance analysis...")
        
        # Get recent performance data
        log = self._load_performance_log()
        recent_records = log[-50:]  # Use last 50 records for analysis
        
        if len(recent_records) < 10:
            self.logger.warning("Not enough records to adjust strategy")
            return
        
        # Analyze performance by different factors
        self._adjust_indicator_weights(recent_records)
        self._adjust_sentiment_weight(recent_records)
        self._adjust_confidence_threshold(recent_records)
        
        # Save updated configuration
        self._save_strategy_config(self.strategy_config)
        
        self.logger.info("Strategy adjustment completed")
        self.logger.info(f"New indicator weights: {self.strategy_config['indicator_weights']}")
        self.logger.info(f"New sentiment weight: {self.strategy_config['sentiment_weight']}")
        self.logger.info(f"New confidence threshold: {self.strategy_config['confidence_threshold']}")
    
    def _adjust_indicator_weights(self, recent_records: List[Dict]):
        """
        Adjust weights of technical indicators based on their recent performance
        """
        # Calculate performance of each indicator
        indicator_performance = {}
        
        for record in recent_records:
            indicators = record.get('indicators', {})
            analysis = record['analysis']
            
            # Simplified: check how well each indicator aligned with the actual outcome
            for indicator_name, value in indicators.items():
                if indicator_name not in indicator_performance:
                    indicator_performance[indicator_name] = {'correct_count': 0, 'total_count': 0, 'sum_abs_value': 0}
                
                indicator_performance[indicator_name]['total_count'] += 1
                
                # This is a simplified approach - in practice, we'd need more sophisticated correlation analysis
                # For now, we'll adjust based on whether the indicator's signal aligned with the actual outcome
                if self._indicator_aligned_with_outcome(indicator_name, value, record['actual_direction']):
                    indicator_performance[indicator_name]['correct_count'] += 1
                
                indicator_performance[indicator_name]['sum_abs_value'] += abs(value)
        
        # Adjust weights based on performance
        learning_rate = self.strategy_config['learning_rate']
        
        for indicator_name, perf in indicator_performance.items():
            if perf['total_count'] > 0:
                accuracy = perf['correct_count'] / perf['total_count']
                
                # Adjust weight based on performance vs expected (0.5 = neutral)
                performance_diff = accuracy - 0.5
                adjustment = performance_diff * learning_rate
                
                # Apply adjustment to current weight
                current_weight = self.strategy_config['indicator_weights'].get(indicator_name, 0.2)
                new_weight = max(0.05, min(0.5, current_weight + adjustment))  # Keep between 0.05 and 0.5
                self.strategy_config['indicator_weights'][indicator_name] = new_weight
    
    def _indicator_aligned_with_outcome(self, indicator_name: str, indicator_value: float, actual_direction: str) -> bool:
        """
        Determine if an indicator's signal aligned with the actual outcome
        """
        if actual_direction == 'HOLD':
            return True  # For HOLD, consider all indicators as aligned
        
        if indicator_name == 'rsi':
            # RSI: <30 suggests UP, >70 suggests DOWN
            if actual_direction == 'UP' and indicator_value < 40:
                return True
            elif actual_direction == 'DOWN' and indicator_value > 60:
                return True
        elif indicator_name == 'macd_histogram':
            # Positive MACD suggests UP, negative suggests DOWN
            if actual_direction == 'UP' and indicator_value > 0:
                return True
            elif actual_direction == 'DOWN' and indicator_value < 0:
                return True
        elif indicator_name == 'ma_trend':
            # Positive trend suggests UP, negative suggests DOWN
            if actual_direction == 'UP' and indicator_value > 0:
                return True
            elif actual_direction == 'DOWN' and indicator_value < 0:
                return True
        elif indicator_name == 'bollinger_position':
            # Low position suggests UP (mean reversion), high suggests DOWN
            if actual_direction == 'UP' and indicator_value < 0.3:
                return True
            elif actual_direction == 'DOWN' and indicator_value > 0.7:
                return True
        elif indicator_name == 'momentum':
            # Positive momentum suggests UP, negative suggests DOWN
            if actual_direction == 'UP' and indicator_value > 0:
                return True
            elif actual_direction == 'DOWN' and indicator_value < 0:
                return True
        
        return False
    
    def _adjust_sentiment_weight(self, recent_records: List[Dict]):
        """
        Adjust the weight of sentiment analysis based on its recent performance
        """
        if not recent_records:
            return
        
        # Count how often sentiment analysis was helpful vs harmful
        helpful_count = 0
        total_count = 0
        
        for record in recent_records:
            sentiment_data = record.get('sentiment_analysis', {})
            if not sentiment_data:
                continue
            
            total_count += 1
            
            # Check if sentiment alignment helped or hurt the prediction
            # This is simplified - in practice, we'd need more sophisticated analysis
            sentiment_aligned = self._sentiment_aligned_with_outcome(
                sentiment_data.get('combined_sentiment', 0), 
                record['actual_direction']
            )
            
            # Check if the prediction would have been correct without sentiment
            tech_direction = record.get('technical_analysis', {}).get('direction', 'HOLD')
            tech_correct = (tech_direction == record['actual_direction'])
            
            # If technical analysis was wrong but sentiment helped, or if technical was right and sentiment didn't hurt
            if (not tech_correct and sentiment_aligned) or (tech_correct and sentiment_aligned):
                helpful_count += 1
        
        if total_count > 0:
            helpful_ratio = helpful_count / total_count
            current_weight = self.strategy_config['sentiment_weight']
            
            # Adjust weight based on helpfulness
            learning_rate = self.strategy_config['learning_rate']
            target_weight = 0.3  # Base weight
            
            if helpful_ratio > 0.6:  # Sentiment is helpful
                target_weight = min(0.5, current_weight + (helpful_ratio - 0.5) * learning_rate)
            elif helpful_ratio < 0.4:  # Sentiment is harmful
                target_weight = max(0.1, current_weight - (0.5 - helpful_ratio) * learning_rate)
            else:  # Sentiment is neutral, keep current weight
                target_weight = current_weight
            
            self.strategy_config['sentiment_weight'] = target_weight
    
    def _sentiment_aligned_with_outcome(self, sentiment_score: float, actual_direction: str) -> bool:
        """
        Determine if sentiment aligned with actual outcome
        """
        if actual_direction == 'HOLD':
            return abs(sentiment_score) < 0.2  # Neutral sentiment aligns with HOLD
        
        if actual_direction == 'UP' and sentiment_score > 0:
            return True
        elif actual_direction == 'DOWN' and sentiment_score < 0:
            return True
        
        return False
    
    def _adjust_confidence_threshold(self, recent_records: List[Dict]):
        """
        Adjust confidence threshold based on recent performance
        """
        if len(recent_records) < 5:
            return
        
        # Analyze performance at different confidence levels
        high_conf_correct = 0
        high_conf_total = 0
        low_conf_correct = 0
        low_conf_total = 0
        
        for record in recent_records:
            conf = record['predicted_confidence']
            is_correct = record['analysis']['is_correct']
            
            if conf >= 0.7:  # High confidence
                high_conf_total += 1
                if is_correct:
                    high_conf_correct += 1
            elif conf <= 0.3:  # Low confidence
                low_conf_total += 1
                if is_correct:
                    low_conf_correct += 1
        
        # Adjust threshold based on performance
        if high_conf_total > 0 and low_conf_total > 0:
            high_acc = high_conf_correct / high_conf_total
            low_acc = low_conf_correct / low_conf_total
            
            # If low confidence predictions are surprisingly accurate, lower the threshold
            if low_acc > high_acc and low_acc > 0.6:
                self.strategy_config['confidence_threshold'] = max(0.4, self.strategy_config['confidence_threshold'] - 0.05)
            # If high confidence predictions aren't accurate enough, raise the threshold
            elif high_acc < 0.6:
                self.strategy_config['confidence_threshold'] = min(0.8, self.strategy_config['confidence_threshold'] + 0.05)
    
    def get_performance_summary(self) -> Dict:
        """
        Get a summary of system performance
        """
        log = self._load_performance_log()
        
        # Calculate recent performance
        recent_records = log[-20:] if log else []
        if recent_records:
            recent_correct = sum(1 for r in recent_records if r['analysis']['is_correct'])
            recent_accuracy = recent_correct / len(recent_records)
        else:
            recent_accuracy = 0.0
        
        return {
            'overall_metrics': self.performance_metrics,
            'recent_accuracy': recent_accuracy,
            'total_records_analyzed': len(log),
            'last_adjustment': self.strategy_config.get('last_adjustment', 'Never'),
            'current_strategy': self.strategy_config
        }

def main():
    # Example usage
    learner = SelfLearningModule()
    
    print("🔍 Self-Learning Module initialized")
    print("="*50)
    
    # Get performance summary
    summary = learner.get_performance_summary()
    print(f"\n📊 Performance Summary:")
    print(f"  Total Predictions: {summary['overall_metrics']['total_predictions']}")
    print(f"  Correct Predictions: {summary['overall_metrics']['correct_predictions']}")
    print(f"  Overall Accuracy: {summary['overall_metrics']['accuracy_rate']:.3f}")
    print(f"  Recent Accuracy: {summary['recent_accuracy']:.3f}")
    print(f"  Total Records Analyzed: {summary['total_records_analyzed']}")

if __name__ == "__main__":
    main()