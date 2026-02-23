#!/usr/bin/env python3
"""
Generate investment recommendations based on OI spike detection from the original radar system
Runs every 5 minutes to provide trading signals with contract addresses and rationale
"""

import requests
import time
import json
from datetime import datetime
import schedule

def get_oi_recommendations():
    """Fetch OI spike data and generate investment recommendations"""
    try:
        # Connect to the original OI radar service on port 8080
        response = requests.get("http://localhost:8080/api/alerts", timeout=10)
        alerts_data = response.json()
        
        recommendations = []
        
        # Process alerts to generate recommendations
        if 'alerts' in alerts_data:
            for alert in alerts_data['alerts']:
                if alert.get('confidence', 0) > 0.7:  # Only high confidence alerts
                    recommendation = {
                        'timestamp': datetime.now().isoformat(),
                        'symbol': alert.get('symbol'),
                        'contract_address': alert.get('contract_address', 'N/A'),  # Placeholder - real contract addresses would be here
                        'recommendation': 'STRONG_' + alert.get('verdict', 'HOLD').upper(),
                        'reason': f"OI Spike detected: {alert.get('oi_change', 0):.2f}% change, "
                                 f"Volume Ratio: {alert.get('volume_ratio', 0):.2f}, "
                                 f"Confidence: {alert.get('confidence', 0):.2f}",
                        'current_price': alert.get('current_price', 'N/A'),
                        'oi_value': alert.get('oi_value', 'N/A'),
                        'oi_change': alert.get('oi_change', 'N/A')
                    }
                    recommendations.append(recommendation)
        
        return recommendations
    except Exception as e:
        print(f"Error fetching OI data: {str(e)}")
        return []

def generate_report():
    """Generate and print the investment recommendation report"""
    print("="*80)
    print(f"POLYMARKET INVESTMENT RECOMMENDATIONS REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    recommendations = get_oi_recommendations()
    
    if not recommendations:
        print("No high-confidence recommendations available at this time.")
        print("Monitoring OI spikes for potential opportunities...")
    else:
        for rec in recommendations:
            print(f"\n📈 SYMBOL: {rec['symbol']}")
            print(f"📍 CONTRACT ADDRESS: {rec['contract_address']}")
            print(f"💡 RECOMMENDATION: {rec['recommendation']}")
            print(f"🔍 REASON: {rec['reason']}")
            print(f"💰 CURRENT PRICE: {rec['current_price']}")
            print(f"📊 OI VALUE: {rec['oi_value']}")
            print(f"📈 OI CHANGE: {rec['oi_change']}")
            print("-" * 80)
    
    print("\nReport generated successfully.")

def main():
    """Main function to run the recommendation generator"""
    print("Starting Polymarket Investment Recommendation System...")
    print("Generating reports every 5 minutes based on OI spike detection.")
    
    # Generate initial report
    generate_report()
    
    # Schedule reports every 5 minutes
    schedule.every(5).minutes.do(generate_report)
    
    print("\nSystem running. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSystem stopped by user.")

if __name__ == "__main__":
    main()