#!/usr/bin/env python3
"""
Auto Review Service for BTC Predictor
Runs in background to automatically review predictions
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def start_auto_review_service():
    """Start the auto review service in the background"""
    print(f"[{datetime.now()}] Starting Auto Review Service...")
    
    log_file = "/root/clawd/projects/polymarket-btc-predictor/auto_review.log"
    
    # Create log file if it doesn't exist
    open(log_file, 'a').close()
    
    # Start the auto review scheduler
    process = subprocess.Popen([
        sys.executable, '-u', 'auto_review_scheduler.py'
    ], stdout=open(log_file, 'a'), stderr=subprocess.STDOUT, cwd='/root/clawd/projects/polymarket-btc-predictor')
    
    print(f"[{datetime.now()}] Auto Review Service started with PID {process.pid}")
    print(f"Log file: {log_file}")
    
    return process.pid

def main():
    if len(sys.argv) < 2:
        print("Usage: python auto_review_service.py [start|status|stop]")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        pid = start_auto_review_service()
        print(f"Auto Review Service started successfully with PID {pid}")
    elif command == 'status':
        # In a real implementation, we would check if the process is running
        print("Auto Review Service - Check process list for running instances")
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()