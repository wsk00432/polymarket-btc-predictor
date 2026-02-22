#!/usr/bin/env python3
"""
Improved Service Manager for BTC Predictor
Manages the prediction service lifecycle with better error handling and auto-restart
"""

import subprocess
import sys
import os
import time
import signal
import atexit
from datetime import datetime
import threading
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedServiceManager:
    def __init__(self):
        self.web_api_process = None
        self.continuous_pred_process = None
        self.service_name = "BTC Predictor Service"
        self.running = False
        
    def start_web_api(self):
        """Start the web API service"""
        logger.info("Starting Web API service...")
        
        log_file = "/root/clawd/projects/polymarket-btc-predictor/web_api_service.log"
        
        # Start the Flask web server
        self.web_api_process = subprocess.Popen([
            sys.executable, '-u', 'web_api.py'
        ], stdout=open(log_file, 'a'), stderr=subprocess.STDOUT)
        
        logger.info(f"Web API service started with PID {self.web_api_process.pid}")
        return self.web_api_process.pid
    
    def start_continuous_predictions(self):
        """Start the continuous prediction service with error handling and auto-restart"""
        logger.info("Starting continuous prediction service with auto-restart capability...")
        
        # Create a separate script for the continuous predictor that includes error handling
        continuous_script = '''
import sys
import time
import traceback
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/clawd/projects/polymarket-btc-predictor/continuous_predictions_detailed.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_continuous_predictions_with_logging():
    """Run continuous predictions with comprehensive error handling"""
    sys.path.append('.')
    
    while True:
        predictor = None
        try:
            from btc_predictor import BTCPredictor
            predictor = BTCPredictor()
            logger.info('Continuous prediction service started...')
            
            # Import PredictionManager to record predictions for evaluation
            from prediction_manager import PredictionManager
            manager = PredictionManager()
            
            while True:
                try:
                    prediction = predictor.predict_next_movement()
                    
                    # Log prediction
                    logger.info('Prediction: {}, Confidence: {:.3f}, Price: $ {}'.format(
                        prediction['prediction'], 
                        prediction['confidence'],
                        prediction['current_price']))
                    
                    # Save to individual file (original functionality)
                    predictor.save_prediction(prediction)
                    
                    # ALSO record with PredictionManager for outcome tracking and learning
                    try:
                        manager.record_prediction_for_evaluation(prediction)
                        logger.info('Recorded prediction {} for evaluation'.format(prediction['timestamp']))
                    except Exception as e:
                        logger.error('Error recording prediction for evaluation: {}'.format(e))
                        logger.error(traceback.format_exc())
                    
                    # Wait before next prediction - using 120 seconds (2 minutes)
                    logger.info("Waiting 120 seconds before next prediction...")
                    time.sleep(120)
                    
                except KeyboardInterrupt:
                    logger.info('Prediction service interrupted by user')
                    break
                except Exception as e:
                    logger.error('Error in prediction cycle: {}'.format(e))
                    logger.error(traceback.format_exc())
                    logger.info('Restarting prediction cycle in 10 seconds...')
                    time.sleep(10)  # Wait 10 seconds before retrying
                    
        except KeyboardInterrupt:
            logger.info('Continuous prediction service interrupted by user')
            break
        except Exception as e:
            logger.error('Critical error in continuous prediction service: {}'.format(e))
            logger.error(traceback.format_exc())
            logger.info('Attempting to restart service in 30 seconds...')
            if predictor:
                del predictor
            time.sleep(30)  # Wait 30 seconds before restarting

if __name__ == "__main__":
    run_continuous_predictions_with_logging()
        '''
        
        # Write the script to a temporary file
        script_path = "/root/clawd/projects/polymarket-btc-predictor/continuous_runner.py"
        with open(script_path, 'w') as f:
            f.write(continuous_script)
        
        # Start the continuous prediction process
        log_file = "/root/clawd/projects/polymarket-btc-predictor/continuous_predictions.log"
        self.continuous_pred_process = subprocess.Popen([
            sys.executable, '-u', script_path
        ], stdout=open(log_file, 'a'), stderr=subprocess.STDOUT)
        
        logger.info(f"Continuous prediction service started with PID {self.continuous_pred_process.pid}")
        return self.continuous_pred_process.pid
    
    def monitor_services(self):
        """Monitor service health and restart if needed"""
        while self.running:
            try:
                # Check web API process
                if self.web_api_process and self.web_api_process.poll() is not None:
                    logger.warning("Web API process died, attempting restart...")
                    self.start_web_api()
                
                # Check continuous prediction process
                if self.continuous_pred_process and self.continuous_pred_process.poll() is not None:
                    logger.warning("Continuous prediction process died, attempting restart...")
                    self.start_continuous_predictions()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in service monitoring: {e}")
                time.sleep(30)
    
    def start_all_services(self):
        """Start all services with monitoring"""
        self.running = True
        
        # Start services
        self.start_web_api()
        self.start_continuous_predictions()
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
        monitor_thread.start()
        
        logger.info("All services started successfully!")
        logger.info("Web API available at: http://localhost:5000")
        
        return True
    
    def stop_all_services(self):
        """Stop all services"""
        self.running = False
        logger.info("Stopping all services...")
        
        if self.web_api_process:
            logger.info(f"Stopping Web API service (PID {self.web_api_process.pid})...")
            self.web_api_process.terminate()
            try:
                self.web_api_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.web_api_process.kill()
            logger.info("Web API service stopped")
        
        if self.continuous_pred_process:
            logger.info(f"Stopping Continuous Prediction service (PID {self.continuous_pred_process.pid})...")
            self.continuous_pred_process.terminate()
            try:
                self.continuous_pred_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.continuous_pred_process.kill()
            logger.info("Continuous Prediction service stopped")
        
        # Clean up the temporary script
        script_path = "/root/clawd/projects/polymarket-btc-predictor/continuous_runner.py"
        if os.path.exists(script_path):
            os.remove(script_path)
        
        logger.info("All services stopped")
    
    def check_status(self):
        """Check service status"""
        status_info = {}
        
        if self.web_api_process and self.web_api_process.poll() is None:
            status_info['web_api'] = f"Running (PID {self.web_api_process.pid})"
        else:
            status_info['web_api'] = "Not running"
        
        if self.continuous_pred_process and self.continuous_pred_process.poll() is None:
            status_info['continuous_prediction'] = f"Running (PID {self.continuous_pred_process.pid})"
        else:
            status_info['continuous_prediction'] = "Not running"
        
        status_info['monitoring'] = "Active" if self.running else "Inactive"
        
        return status_info

def main():
    manager = ImprovedServiceManager()
    
    if len(sys.argv) < 2:
        print("Usage: python improved_start_service.py [start|stop|status]")
        print("  start  - Start the BTC prediction services with auto-restart")
        print("  stop   - Stop the BTC prediction services") 
        print("  status - Check service status")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        logger.info("Starting BTC prediction services with improved reliability...")
        manager.start_all_services()
        print("Services started successfully! Use 'python improved_start_service.py status' to check status.")
        
        # Keep the main process alive
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\\nReceived interrupt signal, stopping services...")
            manager.stop_all_services()
            
    elif command == 'stop':
        manager.stop_all_services()
    elif command == 'status':
        status = manager.check_status()
        print("Service Status:")
        for service, info in status.items():
            print(f"  {service}: {info}")
    else:
        print(f"Unknown command: {command}")
        print("Usage: python improved_start_service.py [start|stop|status]")

if __name__ == "__main__":
    main()