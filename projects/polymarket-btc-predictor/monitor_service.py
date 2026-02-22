#!/usr/bin/env python3
"""
Monitor the BTC Predictor service
Check service health and generate reports
"""

import requests
import json
import time
from datetime import datetime
import os

def check_api_health():
    """Check if the API is running and responding"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"API returned status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"API not accessible: {str(e)}"

def get_latest_prediction():
    """Get the latest prediction from the API"""
    try:
        response = requests.get('http://localhost:5000/predict', timeout=15)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Prediction endpoint returned status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Prediction request failed: {str(e)}"

def get_prediction_history():
    """Get prediction history from the API"""
    try:
        response = requests.get('http://localhost:5000/history', timeout=15)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"History endpoint returned status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"History request failed: {str(e)}"

def get_service_stats():
    """Get service statistics from the API"""
    try:
        response = requests.get('http://localhost:5000/stats', timeout=15)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Stats endpoint returned status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Stats request failed: {str(e)}"

def check_system_resources():
    """Check system resource usage"""
    import psutil
    
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage('/').percent
    
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory_percent,
        'disk_percent': disk_percent,
        'timestamp': datetime.now().isoformat()
    }

def generate_report():
    """Generate a comprehensive system report"""
    report = {
        'generated_at': datetime.now().isoformat(),
        'checks': {}
    }
    
    print("🔍 Running system checks...")
    
    # Check API health
    print("Checking API health...")
    health_ok, health_info = check_api_health()
    report['checks']['api_health'] = {
        'status': 'OK' if health_ok else 'ERROR',
        'details': health_info
    }
    print(f"  API Health: {'✅' if health_ok else '❌'}")
    
    # Get latest prediction
    print("Getting latest prediction...")
    pred_ok, pred_info = get_latest_prediction()
    report['checks']['latest_prediction'] = {
        'status': 'OK' if pred_ok else 'ERROR',
        'details': pred_info
    }
    print(f"  Latest Prediction: {'✅' if pred_ok else '❌'}")
    
    # Get prediction history
    print("Getting prediction history...")
    hist_ok, hist_info = get_prediction_history()
    report['checks']['prediction_history'] = {
        'status': 'OK' if hist_ok else 'ERROR',
        'details': hist_info
    }
    print(f"  Prediction History: {'✅' if hist_ok else '❌'}")
    
    # Get service stats
    print("Getting service stats...")
    stats_ok, stats_info = get_service_stats()
    report['checks']['service_stats'] = {
        'status': 'OK' if stats_ok else 'ERROR',
        'details': stats_info
    }
    print(f"  Service Stats: {'✅' if stats_ok else '❌'}")
    
    # Check system resources
    print("Checking system resources...")
    try:
        resources = check_system_resources()
        report['checks']['system_resources'] = {
            'status': 'OK',
            'details': resources
        }
        print(f"  System Resources: ✅ (CPU: {resources['cpu_percent']}%, Mem: {resources['memory_percent']}%)")
    except ImportError:
        report['checks']['system_resources'] = {
            'status': 'ERROR',
            'details': 'psutil not available'
        }
        print("  System Resources: ❌ (psutil not available)")
    
    # Count prediction files
    pred_dir = '/root/clawd/projects/polymarket-btc-predictor/predictions'
    if os.path.exists(pred_dir):
        pred_files = [f for f in os.listdir(pred_dir) if f.startswith('btc_pred_')]
        report['prediction_files_count'] = len(pred_files)
    else:
        report['prediction_files_count'] = 0
    
    # Save report
    report_filename = f"/root/clawd/projects/polymarket-btc-predictor/reports/system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs('/root/clawd/projects/polymarket-btc-predictor/reports', exist_ok=True)
    
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

def print_summary(report):
    """Print a summary of the report"""
    print("\n" + "="*60)
    print("BTC PREDICTOR SERVICE STATUS REPORT")
    print("="*60)
    print(f"Generated at: {report['generated_at']}")
    print(f"Prediction files: {report.get('prediction_files_count', 0)}")
    print()
    
    for check_name, check_result in report['checks'].items():
        status = check_result['status']
        icon = "✅" if status == "OK" else "❌"
        print(f"{icon} {check_name.replace('_', ' ').title()}: {status}")
    
    print()
    
    # Print latest prediction details if available
    if report['checks'].get('latest_prediction', {}).get('status') == 'OK':
        pred_details = report['checks']['latest_prediction']['details']
        print("📊 LATEST PREDICTION:")
        print(f"   Direction: {pred_details.get('prediction', 'N/A')}")
        print(f"   Confidence: {pred_details.get('confidence', 'N/A')}")
        print(f"   Current Price: ${pred_details.get('current_price', 'N/A')}")
        print(f"   Timestamp: {pred_details.get('timestamp', 'N/A')}")
        print()
    
    # Print system resources if available
    if report['checks'].get('system_resources', {}).get('status') == 'OK':
        res_details = report['checks']['system_resources']['details']
        print("💻 SYSTEM RESOURCES:")
        print(f"   CPU: {res_details.get('cpu_percent', 'N/A')}%")
        print(f"   Memory: {res_details.get('memory_percent', 'N/A')}%")
        print(f"   Disk: {res_details.get('disk_percent', 'N/A')}%")
        print()
    
    print("="*60)

def main():
    print("Running BTC Predictor service health check...")
    report = generate_report()
    print_summary(report)
    
    # Also display a simple status
    api_ok, _ = check_api_health()
    pred_ok, _ = get_latest_prediction()
    
    if api_ok and pred_ok:
        print("🟢 Service is running normally")
    else:
        print("🔴 Service may have issues - check logs")

if __name__ == "__main__":
    main()