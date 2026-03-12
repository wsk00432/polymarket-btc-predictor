#!/usr/bin/env python3
"""
Polymarket Investment Advice Generator
Connects to Polymarket API to generate investment advice
with market question, condition ID (contract address), and recommendation reason.
"""

import requests
import time
import json
from datetime import datetime
import threading
import sys
import os

def get_polymarket_investment_advice():
    """
    Fetches Polymarket data and generates investment advice
    """
    try:
        # Connect to Polymarket API to get active markets
        response = requests.get("https://gamma-api.polymarket.com/markets?limit=10&active=true&closed=false", timeout=10)
        data = response.json()
        
        # Create formatted output
        output_lines = []
        output_lines.append("="*80)
        output_lines.append(f"POLYMARKET 投资建议 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append("="*80)
        
        if 'data' in data and data['data'] or isinstance(data, list):
            markets = data['data'] if 'data' in data else data
            # Show top 5 markets by volume
            sorted_markets = sorted(markets, key=lambda x: float(x.get('volume', 0)), reverse=True)[:5]
            
            for market in sorted_markets:
                question = market.get('question', 'N/A')
                condition_id = market.get('conditionId', 'N/A')
                slug = market.get('slug', 'N/A')
                volume = float(market.get('volume', 0))
                liquidity = float(market.get('liquidity', 0))
                
                # Safely parse outcomes and prices
                try:
                    outcomes = market.get('outcomes', ['N/A', 'N/A'])
                    # If outcomes is a string, try to parse it as JSON
                    if isinstance(outcomes, str):
                        outcomes = json.loads(outcomes)
                except:
                    outcomes = ['N/A', 'N/A']
                
                try:
                    outcome_prices = market.get('outcomePrices', [0, 0])
                    # If outcome_prices is a string, try to parse it as JSON
                    if isinstance(outcome_prices, str):
                        outcome_prices = json.loads(outcome_prices)
                except:
                    outcome_prices = [0, 0]
                
                # Convert string prices to floats for comparison
                float_prices = []
                for price in outcome_prices:
                    try:
                        float_prices.append(float(price))
                    except (ValueError, TypeError):
                        float_prices.append(0.0)
                
                # Find the outcome with highest price (highest probability)
                if len(float_prices) > 0:
                    max_price_idx = float_prices.index(max(float_prices))
                    recommended_outcome = outcomes[max_price_idx] if max_price_idx < len(outcomes) else 'N/A'
                    recommended_price = float_prices[max_price_idx]
                    
                    # Determine recommendation based on price
                    if recommended_price > 0.8:
                        recommendation = "强烈买入"
                    elif recommended_price > 0.6:
                        recommendation = "买入"
                    elif recommended_price < 0.2:
                        recommendation = "强烈卖出"
                    elif recommended_price < 0.4:
                        recommendation = "卖出"
                    else:
                        recommendation = "持有"
                else:
                    recommended_outcome = 'N/A'
                    recommended_price = 0
                    recommendation = "观望"
                
                output_lines.append(f"📈 事件: {question}")
                output_lines.append(f"📍 条件ID (合约地址): {condition_id}")
                output_lines.append(f"💡 推荐: {recommendation}")
                output_lines.append(f"🎯 结果: {recommended_outcome} (概率: {recommended_price:.2%})")
                output_lines.append(f"📊 市场数据:")
                output_lines.append(f"   • 交易量: ${volume:,.2f}")
                output_lines.append(f"   • 流动性: ${liquidity:,.2f}")
                output_lines.append(f"   • 市场slug: {slug}")
                
                # Add analysis based on market metrics
                reasons = []
                if volume > 100000:
                    reasons.append("高交易量")
                if liquidity > 1000:
                    reasons.append("高流动性")
                if recommended_price > 0.7 or recommended_price < 0.3:
                    reasons.append("价格偏差明显")
                    
                if reasons:
                    output_lines.append(f"   • 分析: {', '.join(reasons)}")
                
                output_lines.append("-" * 80)
        else:
            output_lines.append("当前无活跃市场。")
            output_lines.append("正在监控Polymarket机会...")
            output_lines.append("-" * 80)
        
        # Print to console
        for line in output_lines:
            print(line)
        
        # Append to log file
        with open("/root/clawd/polymarket_real_advice.log", "a", encoding="utf-8") as f:
            f.write('\n'.join(output_lines) + '\n')
            
    except requests.exceptions.ConnectionError:
        error_msg = [
            "❌ 错误: 无法连接到Polymarket API",
            "请检查网络连接。",
            "-" * 80
        ]
        for line in error_msg:
            print(line)
        with open("polymarket_real_advice.log", "a", encoding="utf-8") as f:
            f.write('\n'.join(error_msg) + '\n')
    except json.JSONDecodeError:
        error_msg = [
            "❌ 错误: Polymarket API返回无效JSON响应",
            "-" * 80
        ]
        for line in error_msg:
            print(line)
        with open("polymarket_real_advice.log", "a", encoding="utf-8") as f:
            f.write('\n'.join(error_msg) + '\n')
    except Exception as e:
        error_msg = [
            f"❌ 错误: {str(e)}",
            "-" * 80
        ]
        for line in error_msg:
            print(line)
        with open("polymarket_real_advice.log", "a", encoding="utf-8") as f:
            f.write('\n'.join(error_msg) + '\n')

def run_periodic_advice():
    """
    Runs the investment advice generator every 5 minutes
    """
    startup_msg = [
        "🤖 开始Polymarket投资建议服务...",
        "📡 获取Polymarket数据",
        "⏰ 每5分钟生成报告",
        "💡 按Ctrl+C停止服务",
        ""
    ]
    for line in startup_msg:
        print(line)
    
    # Write startup message to log
    with open("polymarket_real_advice.log", "a", encoding="utf-8") as f:
        f.write('\n'.join(startup_msg))
    
    # Initial run
    get_polymarket_investment_advice()
    
    try:
        while True:
            # Wait 5 minutes (300 seconds) before next run
            time.sleep(300)
            get_polymarket_investment_advice()
    except KeyboardInterrupt:
        end_msg = [
            "\n🛑 投资建议服务被用户停止。",
            "👋 感谢使用Polymarket投资顾问！"
        ]
        for line in end_msg:
            print(line)
        with open("polymarket_real_advice.log", "a", encoding="utf-8") as f:
            f.write('\n'.join(end_msg) + '\n')

if __name__ == "__main__":
    run_periodic_advice()