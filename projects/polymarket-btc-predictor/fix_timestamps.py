#!/usr/bin/env python3
"""
Fix timestamps in performance log to remove artificial timestamps
"""

import json
import os
from datetime import datetime, timedelta

def fix_performance_log_timestamps():
    """Fix artificial timestamps in performance log"""
    perf_log_path = "/root/clawd/projects/polymarket-btc-predictor/performance_log.json"
    
    # Load the performance log
    if not os.path.exists(perf_log_path):
        print("Performance log not found!")
        return
    
    with open(perf_log_path, 'r', encoding='utf-8') as f:
        perf_data = json.load(f)
    
    print(f"Loaded {len(perf_data)} records from performance log")
    
    # Identify and remove records with artificial timestamps
    fixed_data = []
    removed_count = 0
    
    for record in perf_data:
        timestamp = record.get('timestamp', '')
        # Check if timestamp has the problematic pattern (T07:00:00)
        if ':00:00"' in timestamp or '"2026-02-03T07:00:00"' in timestamp:
            print(f"Found artificial timestamp: {timestamp}")
            removed_count += 1
        else:
            fixed_data.append(record)
    
    print(f"Removed {removed_count} records with artificial timestamps")
    print(f"Remaining records: {len(fixed_data)}")
    
    # Save the fixed data
    with open(perf_log_path, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, indent=2, ensure_ascii=False)
    
    print("Fixed performance log saved!")

def verify_fix():
    """Verify the fix worked"""
    perf_log_path = "/root/clawd/projects/polymarket-btc-predictor/performance_log.json"
    
    with open(perf_log_path, 'r', encoding='utf-8') as f:
        perf_data = json.load(f)
    
    print(f"\nVerification - Now have {len(perf_data)} records in performance log")
    
    # Show last few records
    print("Last 5 records:")
    for record in perf_data[-5:]:
        print(f"  {record['timestamp']} - {record['predicted_direction']} -> {record.get('actual_direction', 'N/A')}")

if __name__ == "__main__":
    print("Fixing performance log timestamps...")
    fix_performance_log_timestamps()
    verify_fix()