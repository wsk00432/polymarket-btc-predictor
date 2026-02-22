#!/usr/bin/env python3
"""
Simple dashboard to view BTC Predictor status
"""

import os
from datetime import datetime
import requests
import json

def print_dashboard():
    print("="*80)
    print("₿ BTC PREDICTOR DASHBOARD")
    print("="*80)
    print(f"Dashboard Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if services are running
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("🟢 SERVICE STATUS: RUNNING")
        else:
            print("🔴 SERVICE STATUS: ISSUE DETECTED")
    except:
        print("🔴 SERVICE STATUS: OFFLINE")
    
    print()
    
    # Get latest prediction
    try:
        response = requests.get('http://localhost:5000/predict', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("🔮 LATEST PREDICTION:")
            print(f"   Direction: {data['prediction']}")
            print(f"   Confidence: {data['confidence']:.4f}")
            print(f"   Price: ${data['current_price']:,.2f}")
            print(f"   Time: {data['timestamp']}")
            print(f"   Window: {data['prediction_window_minutes']} minutes")
            
            # Show technical analysis
            if 'technical_analysis' in data:
                ta = data['technical_analysis']
                print(f"   Technical: {ta['direction']} ({ta['confidence']:.3f})")
            
            # Show sentiment analysis if available
            if 'sentiment_analysis' in data:
                sa = data['sentiment_analysis']
                print(f"   Sentiment: {sa['combined_sentiment']:.3f} (S:{sa['social_sentiment']:.3f}, N:{sa['news_sentiment']:.3f})")
            
            print()
    except Exception as e:
        print(f"❌ Could not fetch latest prediction: {e}")
        print()
    
    # Show prediction stats
    try:
        response = requests.get('http://localhost:5000/stats', timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print("📊 STATISTICS:")
            print(f"   Total Predictions: {stats.get('total_predictions', 'N/A')}")
            print(f"   Accuracy: {stats.get('accuracy', 'N/A')}")
            print()
    except:
        print("📊 STATISTICS: Unavailable")
        print()
    
    # Show recent predictions
    try:
        response = requests.get('http://localhost:5000/history', timeout=10)
        if response.status_code == 200:
            history = response.json()
            if history:
                print("📈 RECENT PREDICTIONS:")
                for i, pred in enumerate(history[:3]):  # Show last 3
                    print(f"   {i+1}. {pred['prediction']} - Conf: {pred['confidence']:.3f} - ${pred['current_price']:,.2f}")
                print()
    except:
        print("📈 RECENT PREDICTIONS: Unavailable")
        print()
    
    # File counts
    pred_dir = '/root/clawd/projects/polymarket-btc-predictor/predictions'
    if os.path.exists(pred_dir):
        pred_files = [f for f in os.listdir(pred_dir) if f.startswith('btc_pred_')]
        print(f"💾 PREDICTION FILES: {len(pred_files)} stored")
    
    report_dir = '/root/clawd/projects/polymarket-btc-predictor/reports'
    if os.path.exists(report_dir):
        report_files = [f for f in os.listdir(report_dir) if f.startswith('system_report_')]
        print(f"📋 SYSTEM REPORTS: {len(report_files)} generated")
    
    log_files = ['/root/clawd/projects/polymarket-btc-predictor/service.log', 
                 '/root/clawd/projects/polymarket-btc-predictor/predictions.log',
                 '/root/clawd/projects/polymarket-btc-predictor/service_health.log']
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"📄 {os.path.basename(log_file)}: {size} bytes")
    
    print()
    print("🔧 API ENDPOINTS:")
    print("   GET  http://localhost:5000/ - Service info")
    print("   GET  http://localhost:5000/predict - Latest prediction")
    print("   GET  http://localhost:5000/history - Prediction history")
    print("   GET  http://localhost:5000/stats - Service statistics")
    print("   GET  http://localhost:5000/health - Health check")
    print()
    print("💡 BUSINESS MODEL:")
    print("   - Subscription plans for prediction access")
    print("   - API licensing for trading platforms")
    print("   - High-frequency trading signals")
    print("   - Confidence-based pricing model")
    print()
    print("="*80)

if __name__ == "__main__":
    print_dashboard()