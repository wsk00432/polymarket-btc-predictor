#!/usr/bin/env python3
"""
Prediction Manager for BTC Predictor
Handles the complete prediction lifecycle with self-learning capabilities
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
from btc_predictor import BTCPredictor

class PredictionManager:
    def __init__(self):
        self.predictor = BTCPredictor()
        self.prediction_history_path = "/root/clawd/projects/polymarket-btc-predictor/prediction_outcomes.json"
        self.logger = logging.getLogger(__name__)
        
        # Load prediction outcomes history
        self.prediction_outcomes = self._load_prediction_outcomes()
    
    def _load_prediction_outcomes(self) -> Dict:
        """Load prediction outcomes from file"""
        if os.path.exists(self.prediction_history_path):
            with open(self.prediction_history_path, 'r') as f:
                return json.load(f)
        else:
            return {}
    
    def _save_prediction_outcomes(self, outcomes: Dict):
        """Save prediction outcomes to file"""
        with open(self.prediction_history_path, 'w') as f:
            json.dump(outcomes, f, indent=2)
    
    def make_prediction(self) -> Dict:
        """Make a prediction using the predictor"""
        prediction = self.predictor.predict_next_movement()
        
        # Store prediction for later outcome evaluation
        prediction_id = prediction['timestamp']
        self.prediction_outcomes[prediction_id] = {
            'prediction': prediction,
            'actual_outcome': None,  # Will be filled in later
            'evaluation_time': None
        }
        
        self._save_prediction_outcomes(self.prediction_outcomes)
        
        return prediction
    
    def record_actual_outcome(self, prediction_timestamp: str, actual_direction: str, actual_price_change: float, current_price: float):
        """Record the actual outcome for a previous prediction"""
        if prediction_timestamp in self.prediction_outcomes:
            self.prediction_outcomes[prediction_timestamp]['actual_outcome'] = {
                'direction': actual_direction,
                'price_change': actual_price_change,
                'current_price': current_price,
                'recorded_at': datetime.now().isoformat()
            }
            
            # Perform self-analysis if learning module is available
            if self.predictor.use_learning and self.predictor.learning_module:
                try:
                    prediction_data = self.prediction_outcomes[prediction_timestamp]['prediction']
                    self.predictor.learning_module.record_prediction_result(
                        prediction_data,
                        actual_outcome=actual_direction,
                        actual_price_change=actual_price_change
                    )
                except Exception as e:
                    self.logger.error(f"Error in learning module: {e}")
            
            self._save_prediction_outcomes(self.prediction_outcomes)
            return True
        else:
            self.logger.warning(f"No prediction found for timestamp: {prediction_timestamp}")
            return False
    
    def record_prediction_for_evaluation(self, prediction: Dict):
        """Record a prediction for later evaluation (used by continuous prediction service)"""
        prediction_id = prediction['timestamp']
        
        # Only add if it doesn't already exist
        if prediction_id not in self.prediction_outcomes:
            self.prediction_outcomes[prediction_id] = {
                'prediction': prediction,
                'actual_outcome': None,  # Will be filled in later
                'evaluation_time': None
            }
            
            self._save_prediction_outcomes(self.prediction_outcomes)
            self.logger.info(f"Recorded prediction {prediction_id} for evaluation")
        else:
            self.logger.info(f"Prediction {prediction_id} already exists, skipping")

    def get_prediction_performance(self) -> Dict:
        """Get performance metrics for predictions"""
        if not self.predictor.use_learning or not self.predictor.learning_module:
            return {"error": "Learning module not available"}
        
        return self.predictor.learning_module.get_performance_summary()
    
    def get_pending_evaluations(self) -> Dict:
        """Get predictions that are waiting for outcome evaluation"""
        pending = {}
        for pred_id, data in self.prediction_outcomes.items():
            if data['actual_outcome'] is None:
                # Check if enough time has passed to evaluate (prediction window + buffer)
                pred_time = datetime.fromisoformat(data['prediction']['timestamp'].replace('Z', '+00:00'))
                eval_time = pred_time + timedelta(minutes=data['prediction']['prediction_window_minutes'] + 5)  # 5-min buffer
                
                if datetime.now(pred_time.tzinfo) >= eval_time:
                    pending[pred_id] = data
        
        return pending

def simulate_prediction_evaluation():
    """Simulate the prediction and evaluation cycle"""
    manager = PredictionManager()
    
    print("🔍 Prediction Manager Demo")
    print("="*50)
    
    # Make a prediction
    print("Making prediction...")
    prediction = manager.make_prediction()
    
    print(f"Prediction: {prediction['prediction']}")
    print(f"Confidence: {prediction['confidence']:.3f}")
    print(f"Current Price: ${prediction['current_price']:,.2f}")
    print(f"Time: {prediction['timestamp']}")
    
    if 'sentiment_analysis' in prediction:
        sa = prediction['sentiment_analysis']
        print(f"Sentiment: {sa['combined_sentiment']:.3f}")
    
    print()
    print("💡 To properly evaluate this prediction, we need to wait for the outcome.")
    print("In a real system, this would happen after the prediction window (15 minutes).")
    print("The system would then:")
    print("1. Record the actual price movement")
    print("2. Analyze prediction accuracy")
    print("3. Adjust strategy based on results")
    print("4. Improve future predictions")
    
    # Show how to record an actual outcome (for demo purposes)
    print()
    print("📝 Example of how to record actual outcome:")
    print(f"manager.record_actual_outcome('{prediction['timestamp']}', 'UP', 0.025, 78790.0)")

if __name__ == "__main__":
    simulate_prediction_evaluation()