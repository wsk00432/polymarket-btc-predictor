#!/usr/bin/env python3
"""
Service Manager for BTC Predictor
Manages the prediction service lifecycle
"""

import subprocess
import sys
import os
import time
import signal
import atexit
from datetime import datetime

class ServiceManager:
    def __init__(self):
        self.process = None
        self.service_name = "BTC Predictor Service"
        self.log_file = "/root/clawd/projects/polymarket-btc-predictor/service.log"
        
    def start_web_api(self):
        """Start the web API service"""
        print(f"[{datetime.now()}] Starting {self.service_name}...")
        
        # Create log file if it doesn't exist
        open(self.log_file, 'a').close()
        
        # Start the Flask web server
        self.process = subprocess.Popen([
            sys.executable, '-u', 'web_api.py'
        ], stdout=open(self.log_file, 'a'), stderr=subprocess.STDOUT)
        
        print(f"[{datetime.now()}] {self.service_name} started with PID {self.process.pid}")
        return self.process.pid
    
    def start_continuous_predictions(self):
        """Start the continuous prediction service"""
        print(f"[{datetime.now()}] Starting continuous prediction service...")
        
        log_file = "/root/clawd/projects/polymarket-btc-predictor/predictions.log"
        open(log_file, 'a').close()
        
        # Start the continuous prediction process
        process = subprocess.Popen([
            sys.executable, '-u', '-c', 
            '''
import sys
sys.path.append(".")
from btc_predictor import BTCPredictor
predictor = BTCPredictor()
predictor.run_continuous_predictions(interval_seconds=60)  # Every minute for testing
            '''
        ], stdout=open(log_file, 'a'), stderr=subprocess.STDOUT)
        
        print(f"[{datetime.now()}] Continuous prediction service started with PID {process.pid}")
        return process.pid
    
    def stop_service(self):
        """Stop the service"""
        if self.process:
            print(f"[{datetime.now()}] Stopping {self.service_name}...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            print(f"[{datetime.now()}] {self.service_name} stopped")
    
    def check_status(self):
        """Check service status"""
        if self.process and self.process.poll() is None:
            return f"Service running with PID {self.process.pid}"
        else:
            return "Service is not running"
    
    def install_dependencies(self):
        """Install required dependencies"""
        print("Installing required dependencies...")
        
        deps = ['flask', 'numpy', 'pandas', 'requests']
        for dep in deps:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
                print(f"✓ Installed {dep}")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install {dep}")

def main():
    manager = ServiceManager()
    
    if len(sys.argv) < 2:
        print("Usage: python start_service.py [start|stop|status|install]")
        print("  start  - Start the BTC prediction services")
        print("  stop   - Stop the BTC prediction services") 
        print("  status - Check service status")
        print("  install - Install dependencies")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'install':
        manager.install_dependencies()
    elif command == 'start':
        # Install dependencies first
        manager.install_dependencies()
        # Start both services
        manager.start_web_api()
        manager.start_continuous_predictions()
        print(f"[{datetime.now()}] Both services started successfully!")
        print("Web API available at: http://localhost:5000")
    elif command == 'stop':
        manager.stop_service()
    elif command == 'status':
        print(manager.check_status())
    else:
        print(f"Unknown command: {command}")
        print("Usage: python start_service.py [start|stop|status|install]")

if __name__ == "__main__":
    main()