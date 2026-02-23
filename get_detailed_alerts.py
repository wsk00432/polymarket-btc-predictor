#!/usr/bin/env python3
"""
Script to fetch and display detailed alerts with proper contract addresses
"""

import requests
import json
from datetime import datetime

def get_full_alert_details():
    try:
        # Get full alerts data
        response = requests.get("http://localhost:8080/api/alerts", timeout=10)
        data = response.json()
        
        print("🔍 详细警报数据结构分析:")
        print("="*80)
        
        if 'alerts' in data and data['alerts']:
            for i, alert in enumerate(data['alerts'][:3]):  # Show first 3 alerts
                print(f"\n警报 {i+1}:")
                print("-" * 40)
                for key, value in alert.items():
                    print(f"{key}: {value}")
                print("-" * 40)
        else:
            print("当前无警报数据")
            
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    get_full_alert_details()