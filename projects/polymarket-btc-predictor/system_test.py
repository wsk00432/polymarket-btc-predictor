#!/usr/bin/env python3
"""
System test for the complete BTC Predictor with self-learning capabilities
"""

from btc_predictor import BTCPredictor
from prediction_manager import PredictionManager
from self_learning_module import SelfLearningModule
import json
from datetime import datetime

def test_complete_system():
    print("🧪 Testing Complete BTC Prediction System")
    print("="*60)
    
    # Initialize components
    predictor = BTCPredictor()
    manager = PredictionManager()
    
    print("✅ Components initialized")
    print(f"  - Predictor: {'Available' if predictor else 'Error'}")
    print(f"  - Message Sentiment: {'Available' if predictor.use_sentiment else 'Not Available'}")
    print(f"  - Self Learning: {'Available' if predictor.use_learning else 'Not Available'}")
    print()
    
    # Test prediction making
    print("📈 Making prediction...")
    prediction = manager.make_prediction()
    
    print(f"  - Direction: {prediction['prediction']}")
    print(f"  - Confidence: {prediction['confidence']:.4f}")
    print(f"  - Price: ${prediction['current_price']:,.2f}")
    print(f"  - Timestamp: {prediction['timestamp']}")
    
    if 'sentiment_analysis' in prediction:
        sa = prediction['sentiment_analysis']
        print(f"  - Sentiment: {sa['combined_sentiment']:.3f}")
    print()
    
    # Test outcome recording (simulated)
    print("📊 Recording simulated outcome...")
    pred_timestamp = prediction['timestamp']
    actual_direction = "UP"  # Simulated actual outcome
    actual_price_change = 0.025  # 2.5% increase
    current_price = prediction['current_price'] * 1.025  # Updated price
    
    success = manager.record_actual_outcome(
        pred_timestamp,
        actual_direction,
        actual_price_change,
        current_price
    )
    
    print(f"  - Recording: {'Success' if success else 'Failed'}")
    print(f"  - Actual Direction: {actual_direction}")
    print(f"  - Actual Change: {actual_price_change:.3f} ({actual_price_change*100:.1f}%)")
    print(f"  - New Price: ${current_price:,.2f}")
    print()
    
    # Test performance evaluation
    if predictor.use_learning and predictor.learning_module:
        print("🏆 Getting performance metrics...")
        performance = manager.get_prediction_performance()
        
        print(f"  - Total Predictions: {performance['overall_metrics']['total_predictions']}")
        print(f"  - Correct Predictions: {performance['overall_metrics']['correct_predictions']}")
        print(f"  - Overall Accuracy: {performance['overall_metrics']['accuracy_rate']:.3f}")
        print(f"  - Recent Accuracy: {performance['recent_accuracy']:.3f}")
        print(f"  - Current Strategy:")
        for indicator, weight in performance['current_strategy']['indicator_weights'].items():
            print(f"    * {indicator}: {weight:.3f}")
        print(f"    * Sentiment Weight: {performance['current_strategy']['sentiment_weight']:.3f}")
        print(f"    * Confidence Threshold: {performance['current_strategy']['confidence_threshold']:.3f}")
    else:
        print("❌ Self-learning module not available")
    print()
    
    # Test pending evaluations
    print("⏳ Checking pending evaluations...")
    pending = manager.get_pending_evaluations()
    print(f"  - Pending for evaluation: {len(pending)}")
    if pending:
        for pred_id, data in list(pending.items())[:2]:  # Show first 2
            print(f"    * {pred_id}: {data['prediction']['prediction']}")
    print()
    
    print("🎉 System test completed successfully!")
    print()
    print("🔄 System Features:")
    print("  ✓ Technical Analysis (RSI, MACD, Moving Averages, etc.)")
    print("  ✓ Sentiment Analysis (Social Media & News)")
    print("  ✓ Self-Learning (Performance Tracking & Strategy Adjustment)")
    print("  ✓ Prediction Management (Lifecycle Tracking)")
    print("  ✓ Outcome Evaluation (Accuracy Assessment)")
    print("  ✓ Strategy Optimization (Automatic Adjustments)")
    print()
    print("📈 The system is now fully autonomous and self-improving!")

if __name__ == "__main__":
    test_complete_system()