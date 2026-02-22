#!/usr/bin/env python3
"""
Message Sentiment Analyzer for BTC Predictor
Analyzes social media and news sentiment to enhance prediction accuracy
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re
from urllib.parse import quote

class MessageSentimentAnalyzer:
    def __init__(self):
        self.sentiment_weights = {
            'positive': 0.3,  # Positive sentiment contributes to UP prediction
            'negative': -0.3,  # Negative sentiment contributes to DOWN prediction
            'neutral': 0.0
        }
        
        # Keywords related to Bitcoin that indicate market sentiment
        self.positive_keywords = [
            'bull', 'bullish', 'moon', 'rocket', 'buy', 'accumulate', 'diamond hands',
            'hodl', 'fomo', 'green', 'up', 'gain', 'profit', 'success', 'win',
            'strong', 'powerful', 'breakout', 'ath', 'all time high', 'halving',
            'adoption', 'institutional', 'bitcoin ETF', 'spot ETF', 'upgrade', 'halvening'
        ]
        
        self.negative_keywords = [
            'bear', 'bearish', 'dump', 'sell', 'panic', 'fud', 'red', 'down', 'loss',
            'crash', 'fall', 'weak', 'scared', 'shitcoin', 'bubble', 'crack', 'shill',
            'manipulation', 'regulation', 'ban', 'concern', 'worried', 'fear'
        ]
        
        # Crypto influencers and important accounts to monitor
        self.influencer_accounts = [
            'elonmusk', 'cz_binance', 'saylor', 'vitalikbuterin', 'aantonop',
            'btc_pay', 'bitcoinmagazine', 'coincenter', 'nakamoto', 'srmunger',
            'paulg', 'naval', 'balajis', 'timothy_l_swanson', 'nic__carter',
            'mvollmer_', 'jimmysong', 'pierre_rochard', 'gardenfrogs'
        ]
        
        # News sources for Bitcoin-related news
        self.news_sources = [
            'https://newsapi.org/v2/everything?q=btc+OR+bitcoin&sortBy=publishedAt&apiKey=YOUR_API_KEY&language=en',
            'https://api.coindesk.com/v1/bpi/currentprice.json'  # Example API
        ]
        
        print("Message Sentiment Analyzer initialized")
    
    def extract_sentiment_from_text(self, text: str) -> Dict[str, float]:
        """
        Extract sentiment from text based on keywords
        """
        text_lower = text.lower()
        
        positive_score = 0
        negative_score = 0
        
        # Count positive keywords
        for keyword in self.positive_keywords:
            matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text_lower))
            positive_score += matches
        
        # Count negative keywords
        for keyword in self.negative_keywords:
            matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text_lower))
            negative_score += matches
        
        # Calculate sentiment score (-1 to 1 scale)
        total_relevant_words = positive_score + negative_score
        if total_relevant_words == 0:
            sentiment_score = 0.0
        else:
            sentiment_score = (positive_score - negative_score) / total_relevant_words
            # Clamp between -1 and 1
            sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        return {
            'sentiment_score': sentiment_score,
            'positive_count': positive_score,
            'negative_count': negative_score,
            'total_relevant_words': total_relevant_words
        }
    
    def analyze_social_media_sentiment(self) -> Dict[str, float]:
        """
        Simulate analysis of social media sentiment
        In a real implementation, this would connect to social media APIs
        """
        # This is a simulation - in reality, we would connect to Twitter/X API, Reddit API, etc.
        # For now, we'll simulate recent social media sentiment
        
        # Simulated recent posts mentioning Bitcoin
        simulated_posts = [
            "Bitcoin is showing strong signs of recovery with bullish patterns forming",
            "Concerns about regulation still affecting the market sentiment negatively",
            "Major institutions continue to accumulate Bitcoin - very bullish sign!",
            "Market is quite volatile today, many people seem worried about the dip",
            "Bitcoin ETF approval could be a game changer for the market - very positive",
            "Many experts think Bitcoin is oversold right now - good buying opportunity",
            "Fear and uncertainty dominating the market today, red everywhere",
            "Bitcoin halving event approaching - historically bullish for price"
        ]
        
        total_sentiment = 0
        post_count = len(simulated_posts)
        
        for post in simulated_posts:
            sentiment_data = self.extract_sentiment_from_text(post)
            total_sentiment += sentiment_data['sentiment_score']
        
        avg_sentiment = total_sentiment / post_count if post_count > 0 else 0.0
        
        return {
            'average_sentiment': avg_sentiment,
            'post_count': post_count,
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_news_sentiment(self) -> Dict[str, float]:
        """
        Simulate analysis of news sentiment
        In a real implementation, this would connect to news APIs
        """
        # Simulated recent news headlines about Bitcoin
        simulated_headlines = [
            "Bitcoin ETF Approval Expected Soon, Market Optimistic",
            "Regulatory Concerns Weigh on Cryptocurrency Markets",
            "Institutional Investors Continue Bitcoin Accumulation",
            "Bitcoin Mining Difficulty Reaches New All-Time High",
            "Major Bank Announces Bitcoin Investment Services",
            "Government Considering Stricter Crypto Regulations",
            "Bitcoin Network Upgrade Successful, Community Celebrates",
            "Global Adoption of Digital Assets Accelerating"
        ]
        
        total_sentiment = 0
        headline_count = len(simulated_headlines)
        
        for headline in simulated_headlines:
            sentiment_data = self.extract_sentiment_from_text(headline)
            total_sentiment += sentiment_data['sentiment_score']
        
        avg_sentiment = total_sentiment / headline_count if headline_count > 0 else 0.0
        
        return {
            'average_sentiment': avg_sentiment,
            'headline_count': headline_count,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_overall_sentiment_score(self) -> Dict[str, float]:
        """
        Get combined sentiment score from multiple sources
        """
        social_sentiment = self.analyze_social_media_sentiment()
        news_sentiment = self.analyze_news_sentiment()
        
        # Weighted combination of different sentiment sources
        # Social media: 60%, News: 40% (social media often moves markets faster)
        combined_sentiment = (
            social_sentiment['average_sentiment'] * 0.6 +
            news_sentiment['average_sentiment'] * 0.4
        )
        
        return {
            'combined_sentiment': combined_sentiment,
            'social_sentiment': social_sentiment['average_sentiment'],
            'news_sentiment': news_sentiment['average_sentiment'],
            'social_post_count': social_sentiment['post_count'],
            'news_count': news_sentiment['headline_count'],
            'timestamp': datetime.now().isoformat()
        }
    
    def integrate_with_prediction(self, base_prediction_confidence: float, 
                                base_direction: str) -> Dict[str, float]:
        """
        Integrate sentiment analysis with existing technical prediction
        """
        sentiment_data = self.get_overall_sentiment_score()
        
        # Adjust prediction based on sentiment
        sentiment_factor = sentiment_data['combined_sentiment'] * 0.3  # Limit impact to 30%
        
        # Original confidence and direction
        original_confidence = base_prediction_confidence
        original_direction = 1 if base_direction == "UP" else -1 if base_direction == "DOWN" else 0
        
        # Calculate adjusted direction based on sentiment
        adjusted_direction = original_direction + sentiment_factor
        final_direction = "UP" if adjusted_direction > 0.1 else "DOWN" if adjusted_direction < -0.1 else "HOLD"
        
        # Adjust confidence based on agreement between technical and sentiment analysis
        agreement_factor = abs(sentiment_factor)  # Higher sentiment impact increases confidence if aligned
        adjusted_confidence = min(1.0, original_confidence + agreement_factor * 0.2)
        
        return {
            'original_direction': base_direction,
            'original_confidence': base_prediction_confidence,
            'final_direction': final_direction,
            'final_confidence': adjusted_confidence,
            'sentiment_impact': sentiment_factor,
            'sentiment_data': sentiment_data
        }

def main():
    analyzer = MessageSentimentAnalyzer()
    
    print("🔍 Message Sentiment Analyzer Demo")
    print("="*50)
    
    # Simulate integrating with a base prediction
    base_prediction = "UP"
    base_confidence = 0.45
    
    print(f"Base Technical Prediction: {base_prediction} with {base_confidence:.2f} confidence")
    print()
    
    # Get sentiment analysis
    sentiment_data = analyzer.get_overall_sentiment_score()
    print("📊 Sentiment Analysis Results:")
    print(f"  Combined Sentiment: {sentiment_data['combined_sentiment']:.3f}")
    print(f"  Social Media Sentiment: {sentiment_data['social_sentiment']:.3f}")
    print(f"  News Sentiment: {sentiment_data['news_sentiment']:.3f}")
    print(f"  Social Posts Analyzed: {sentiment_data['social_post_count']}")
    print(f"  News Articles Analyzed: {sentiment_data['news_count']}")
    print()
    
    # Integrate sentiment with prediction
    integrated_result = analyzer.integrate_with_prediction(base_confidence, base_prediction)
    print("🎯 Integrated Prediction Results:")
    print(f"  Original: {integrated_result['original_direction']} ({integrated_result['original_confidence']:.3f})")
    print(f"  Final: {integrated_result['final_direction']} ({integrated_result['final_confidence']:.3f})")
    print(f"  Sentiment Impact: {integrated_result['sentiment_impact']:.3f}")
    print()
    
    print("💡 How Sentiment Analysis Enhances Predictions:")
    print("  • Combines technical analysis with market sentiment")
    print("  • Considers social media influence on price movements")
    print("  • Factors in news events that affect market psychology")
    print("  • Provides more comprehensive market view")

if __name__ == "__main__":
    main()