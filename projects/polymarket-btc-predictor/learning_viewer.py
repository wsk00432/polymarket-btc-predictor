#!/usr/bin/env python3
"""
Learning Process Viewer for BTC Predictor
Provides visibility into the self-learning process and historical adjustments
"""

import json
import os
from datetime import datetime
from typing import Dict, List
import pandas as pd

class LearningViewer:
    def __init__(self):
        self.prediction_outcomes_path = "/root/clawd/projects/polymarket-btc-predictor/prediction_outcomes.json"
        self.performance_log_path = "/root/clawd/projects/polymarket-btc-predictor/performance_log.json"
        self.strategy_config_path = "/root/clawd/projects/polymarket-btc-predictor/strategy_config.json"
    
    def load_prediction_outcomes(self) -> Dict:
        """Load prediction outcomes from file"""
        if os.path.exists(self.prediction_outcomes_path):
            with open(self.prediction_outcomes_path, 'r') as f:
                return json.load(f)
        else:
            return {}
    
    def load_performance_log(self) -> List[Dict]:
        """Load performance log from file"""
        if os.path.exists(self.performance_log_path):
            with open(self.performance_log_path, 'r') as f:
                return json.load(f)
        else:
            return []
    
    def load_strategy_config(self) -> Dict:
        """Load current strategy configuration"""
        if os.path.exists(self.strategy_config_path):
            with open(self.strategy_config_path, 'r') as f:
                return json.load(f)
        else:
            return {}
    
    def get_learning_summary(self) -> Dict:
        """Get a summary of the learning process"""
        outcomes = self.load_prediction_outcomes()
        performance_log = self.load_performance_log()
        current_strategy = self.load_strategy_config()
        
        # Calculate overall accuracy
        total_predictions = len(outcomes)
        evaluated_predictions = 0
        correct_predictions = 0
        
        for pred_id, data in outcomes.items():
            if data['actual_outcome'] is not None:
                evaluated_predictions += 1
                if data['prediction']['prediction'] == data['actual_outcome']['direction']:
                    correct_predictions += 1
        
        overall_accuracy = correct_predictions / evaluated_predictions if evaluated_predictions > 0 else 0
        
        # Get recent performance
        recent_logs = performance_log[-20:] if performance_log else []
        if recent_logs:
            recent_correct = sum(1 for log in recent_logs if log['analysis']['is_correct'])
            recent_accuracy = recent_correct / len(recent_logs)
        else:
            recent_accuracy = 0
        
        return {
            'total_predictions': total_predictions,
            'evaluated_predictions': evaluated_predictions,
            'correct_predictions': correct_predictions,
            'overall_accuracy': overall_accuracy,
            'recent_accuracy': recent_accuracy,
            'performance_log_count': len(performance_log),
            'current_strategy': current_strategy
        }
    
    def get_detailed_learning_history(self) -> List[Dict]:
        """Get detailed learning history"""
        performance_log = self.load_performance_log()
        
        detailed_history = []
        for record in performance_log[-10:]:  # Last 10 records
            detailed_record = {
                'timestamp': record['timestamp'],
                'predicted_direction': record['predicted_direction'],
                'predicted_confidence': record['predicted_confidence'],
                'actual_direction': record.get('actual_direction', 'Pending'),
                'is_correct': record['analysis']['is_correct'],
                'accuracy_score': record['analysis']['accuracy_score'],
                'market_volatility': record['analysis']['market_volatility'],
                'error_type': record['analysis']['error_type'],
                'indicators': record['indicators'],
                'sentiment_analysis': record.get('sentiment_analysis', {}),
                'technical_analysis': record.get('technical_analysis', {})
            }
            detailed_history.append(detailed_record)
        
        return detailed_history
    
    def print_learning_dashboard(self):
        """Print a comprehensive learning dashboard"""
        print("="*100)
        print("🤖 BTC PREDICTOR SELF-LEARNING DASHBOARD")
        print("="*100)
        print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Learning Summary
        summary = self.get_learning_summary()
        print("📊 LEARNING SUMMARY:")
        print(f"   Total Predictions Made: {summary['total_predictions']}")
        print(f"   Evaluated Predictions: {summary['evaluated_predictions']}")
        print(f"   Correct Predictions: {summary['correct_predictions']}")
        print(f"   Overall Accuracy: {summary['overall_accuracy']:.3f} ({summary['overall_accuracy']*100:.1f}%)")
        print(f"   Recent Accuracy (Last 20): {summary['recent_accuracy']:.3f} ({summary['recent_accuracy']*100:.1f}%)")
        print(f"   Performance Logs: {summary['performance_log_count']}")
        print()
        
        # Current Strategy
        if summary['current_strategy']:
            print("⚙️  CURRENT STRATEGY CONFIGURATION:")
            if 'indicator_weights' in summary['current_strategy']:
                print("   Technical Indicator Weights:")
                for indicator, weight in summary['current_strategy']['indicator_weights'].items():
                    print(f"     - {indicator}: {weight:.3f}")
            if 'sentiment_weight' in summary['current_strategy']:
                print(f"   Sentiment Weight: {summary['current_strategy']['sentiment_weight']:.3f}")
            if 'confidence_threshold' in summary['current_strategy']:
                print(f"   Confidence Threshold: {summary['current_strategy']['confidence_threshold']:.3f}")
            print()
        
        # Detailed Learning History
        detailed_history = self.get_detailed_learning_history()
        if detailed_history:
            print("📚 RECENT LEARNING HISTORY (Last 10):")
            print("-" * 100)
            print(f"{'Time':<20} {'Pred':<6} {'Conf':<6} {'Actual':<6} {'Correct':<7} {'Error':<15} {'Volatility':<10}")
            print("-" * 100)
            
            for record in detailed_history:
                time_str = record['timestamp'][-12:]  # Last 12 chars of timestamp
                pred = record['predicted_direction']
                conf = f"{record['predicted_confidence']:.2f}"
                actual = record['actual_direction']
                correct = "✓" if record['is_correct'] else "✗"
                error_type = record['error_type'][:14]  # Truncate long error types
                vol = f"{abs(record['market_volatility']):.3f}"
                
                print(f"{time_str:<20} {pred:<6} {conf:<6} {actual:<6} {correct:<7} {error_type:<15} {vol:<10}")
            print()
        
        # Learning Insights
        print("💡 LEARNING INSIGHTS:")
        if summary['recent_accuracy'] > summary['overall_accuracy']:
            print("   • Recent performance is improving compared to overall performance")
        elif summary['recent_accuracy'] < summary['overall_accuracy']:
            print("   • Recent performance is declining, system may be adapting to new market conditions")
        else:
            print("   • Performance is stable")
        
        if summary['current_strategy'] and 'confidence_threshold' in summary['current_strategy']:
            print(f"   • Current confidence threshold is set to {summary['current_strategy']['confidence_threshold']:.2f}")
        
        if summary['evaluated_predictions'] > 0:
            hold_accuracy = self._calculate_hold_accuracy()
            up_accuracy = self._calculate_direction_accuracy('UP')
            down_accuracy = self._calculate_direction_accuracy('DOWN')
            
            print(f"   • Direction-specific accuracies - HOLD: {hold_accuracy:.1f}%, UP: {up_accuracy:.1f}%, DOWN: {down_accuracy:.1f}%")
        print()
        
        # File Locations
        print("📁 LEARNING DATA FILES:")
        print(f"   Prediction Outcomes: {self.prediction_outcomes_path}")
        print(f"   Performance Log: {self.performance_log_path}")
        print(f"   Strategy Config: {self.strategy_config_path}")
        print()
        
        print("="*100)
        print("💡 TIP: Check these files to see the detailed learning process and historical adjustments")
        print("="*100)
    
    def _calculate_hold_accuracy(self) -> float:
        """Calculate accuracy specifically for HOLD predictions"""
        outcomes = self.load_prediction_outcomes()
        hold_predictions = 0
        hold_correct = 0
        
        for pred_id, data in outcomes.items():
            if data['actual_outcome'] is not None:
                if data['prediction']['prediction'] == 'HOLD':
                    hold_predictions += 1
                    # HOLD is considered correct if actual movement was minimal (<1%)
                    actual_change = data['actual_outcome'].get('price_change', 0)
                    if abs(actual_change) < 0.01:  # Less than 1% movement
                        hold_correct += 1
        
        return (hold_correct / hold_predictions * 100) if hold_predictions > 0 else 0
    
    def _calculate_direction_accuracy(self, direction: str) -> float:
        """Calculate accuracy for specific direction predictions"""
        outcomes = self.load_prediction_outcomes()
        dir_predictions = 0
        dir_correct = 0
        
        for pred_id, data in outcomes.items():
            if data['actual_outcome'] is not None:
                if data['prediction']['prediction'] == direction:
                    dir_predictions += 1
                    if data['actual_outcome']['direction'] == direction:
                        dir_correct += 1
        
        return (dir_correct / dir_predictions * 100) if dir_predictions > 0 else 0

def main():
    viewer = LearningViewer()
    viewer.print_learning_dashboard()

if __name__ == "__main__":
    main()