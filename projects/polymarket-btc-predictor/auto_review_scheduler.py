#!/usr/bin/env python3
"""
Automated Review Scheduler for BTC Predictor
Automatically reviews predictions after their time window expires
"""

import time
import requests
import json
from datetime import datetime, timedelta
import schedule
import threading
import logging
from typing import Dict, List

class AutoReviewScheduler:
    def __init__(self):
        self.api_base_url = "http://localhost:5000"
        self.prediction_outcomes_path = "/root/clawd/projects/polymarket-btc-predictor/prediction_outcomes.json"
        self.logger = logging.getLogger(__name__)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self.running = False
        self.scheduler_thread = None
    
    def get_pending_predictions(self) -> List[Dict]:
        """Get predictions that are ready for review"""
        try:
            response = requests.get(f"{self.api_base_url}/pending_evaluations", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Failed to get pending evaluations: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error getting pending evaluations: {e}")
            return []
    
    def get_current_price(self) -> float:
        """Get current BTC price from Binance"""
        try:
            response = requests.get(
                "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", 
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return float(data['price'])
            else:
                self.logger.error(f"Failed to get current price: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting current price: {e}")
            return None
    
    def determine_actual_direction(self, prediction_price: float, current_price: float, window_minutes: int = 15) -> tuple:
        """Determine actual direction based on price change"""
        if prediction_price is None or current_price is None:
            return "HOLD", 0.0
        
        price_change = (current_price - prediction_price) / prediction_price
        abs_change = abs(price_change)
        
        # Define thresholds for determining direction
        threshold = 0.005  # 0.5% threshold for meaningful movement
        
        if abs_change < threshold:
            return "HOLD", price_change
        elif price_change > 0:
            return "UP", price_change
        else:
            return "DOWN", price_change
    
    def record_outcome(self, prediction_timestamp: str, actual_direction: str, actual_price_change: float, current_price: float) -> bool:
        """Record the actual outcome for a prediction"""
        try:
            payload = {
                "prediction_timestamp": prediction_timestamp,
                "actual_direction": actual_direction,
                "actual_price_change": actual_price_change,
                "current_price": current_price
            }
            
            response = requests.post(
                f"{self.api_base_url}/record_outcome",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully recorded outcome for {prediction_timestamp}: {actual_direction}")
                return True
            else:
                self.logger.error(f"Failed to record outcome: {response.status_code}, {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error recording outcome: {e}")
            return False
    
    def review_ready_predictions(self):
        """Review all predictions that are ready for evaluation"""
        self.logger.info("Checking for predictions ready for review...")
        
        pending_predictions = self.get_pending_predictions()
        
        if not pending_predictions:
            self.logger.info("No predictions ready for review")
            return
        
        current_price = self.get_current_price()
        if current_price is None:
            self.logger.error("Could not get current price, skipping review")
            return
        
        for pred_id, pred_data in pending_predictions.items():
            # Get the original prediction price
            original_price = pred_data['prediction']['current_price']
            
            # Determine actual direction
            actual_direction, price_change = self.determine_actual_direction(original_price, current_price)
            
            # Record the outcome
            success = self.record_outcome(
                pred_id,
                actual_direction,
                price_change,
                current_price
            )
            
            if success:
                self.logger.info(f"Completed review for {pred_id}: Predicted {pred_data['prediction']['prediction']}, Actual {actual_direction}, Change {price_change:.4f}")
            else:
                self.logger.error(f"Failed to complete review for {pred_id}")
    
    def start_scheduler(self):
        """Start the automated review scheduler"""
        self.running = True
        
        # Schedule the review to run every 10 minutes (more frequent than prediction window)
        schedule.every(10).minutes.do(self.review_ready_predictions)
        
        self.logger.info("Auto Review Scheduler started")
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def stop_scheduler(self):
        """Stop the automated review scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        self.logger.info("Auto Review Scheduler stopped")
    
    def manual_run(self):
        """Manually run a review cycle"""
        self.review_ready_predictions()

def main():
    scheduler = AutoReviewScheduler()
    
    print("🤖 BTC Predictor Auto Review Scheduler")
    print("="*50)
    print("This scheduler will automatically review predictions after their time window expires")
    print("It will:")
    print("  1. Check for predictions ready for review every 10 minutes")
    print("  2. Get current BTC price from Binance")
    print("  3. Determine actual price movement direction")
    print("  4. Record the outcome for learning")
    print("  5. Trigger the self-learning process")
    print()
    print("Starting scheduler...")
    
    scheduler.start_scheduler()
    
    try:
        # Keep the scheduler running
        while True:
            time.sleep(60)  # Sleep for 1 minute
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        scheduler.stop_scheduler()
        print("Scheduler stopped.")

if __name__ == "__main__":
    main()