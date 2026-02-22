#!/usr/bin/env python3
"""
Periodic Evaluation Script for BTC Predictor
Automatically evaluates predictions every 15 minutes
"""

import time
import sys
import traceback
from datetime import datetime, timedelta
import logging
import schedule

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/clawd/projects/polymarket-btc-predictor/periodic_evaluation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def perform_evaluation_cycle():
    """Perform a single evaluation cycle"""
    logger.info("Starting evaluation cycle...")
    
    try:
        from prediction_manager import PredictionManager
        from btc_predictor import BTCPredictor
        import ccxt
        
        manager = PredictionManager()
        predictor = BTCPredictor()
        
        # Get pending evaluations (predictions that are ready to be evaluated)
        pending_evaluations = manager.get_pending_evaluations()
        
        evaluated_count = 0
        
        if pending_evaluations:
            # Initialize exchange for getting current prices
            exchange = ccxt.binance({
                'enableRateLimit': True,
                'options': {
                    'adjustForTimeDifference': True,
                }
            })
            
            for pred_id, pred_data in pending_evaluations.items():
                try:
                    # Get current price to determine actual outcome
                    ticker = exchange.fetch_ticker('BTC/USDT')
                    current_price = ticker['last']
                    
                    # Determine what the actual direction was based on the prediction window
                    prediction_time = datetime.fromisoformat(pred_data['prediction']['timestamp'].replace('Z', '+00:00'))
                    prediction_window_min = pred_data['prediction']['prediction_window_minutes']
                    
                    # For actual evaluation, we'd compare the price at prediction time vs prediction_window later
                    # Since we can't go back in time, we'll simulate by looking at recent price movements
                    # In a real scenario, we'd have recorded the "future" price when it became available
                    prediction_price = pred_data['prediction']['current_price']
                    price_change = (current_price - prediction_price) / prediction_price
                    
                    # Determine direction based on threshold
                    threshold = 0.005  # 0.5% threshold for significance
                    if abs(price_change) < threshold:
                        actual_direction = 'HOLD'
                    elif price_change > threshold:
                        actual_direction = 'UP'
                    else:
                        actual_direction = 'DOWN'
                    
                    # Record the actual outcome
                    success = manager.record_actual_outcome(
                        pred_id, 
                        actual_direction, 
                        price_change, 
                        current_price
                    )
                    
                    if success:
                        evaluated_count += 1
                        logger.info(f"Evaluation completed for {pred_id}: Predicted {pred_data['prediction']['prediction']} vs Actual {actual_direction}")
                    else:
                        logger.error(f"Failed to record outcome for {pred_id}")
                        
                except Exception as e:
                    logger.error(f"Error evaluating prediction {pred_id}: {e}")
                    logger.error(traceback.format_exc())
        else:
            logger.info("No pending predictions to evaluate")
            
        if evaluated_count > 0:
            logger.info(f"Completed evaluation of {evaluated_count} predictions")
            
            # Update strategy based on new evaluations if learning module is available
            if predictor.use_learning and predictor.learning_module:
                try:
                    predictor.learning_module.update_strategy()
                    logger.info("Strategy updated based on latest evaluations")
                except Exception as e:
                    logger.error(f"Error updating strategy: {e}")
        
    except Exception as e:
        logger.error(f"Error in evaluation cycle: {e}")
        logger.error(traceback.format_exc())

def main():
    """Main function to run the periodic evaluation"""
    logger.info("Starting periodic evaluation service...")
    logger.info("Evaluation will occur every 15 minutes")
    
    # Schedule evaluation every 15 minutes
    schedule.every(15).minutes.do(perform_evaluation_cycle)
    
    # Perform an initial evaluation
    perform_evaluation_cycle()
    
    # Keep the service running
    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    main()