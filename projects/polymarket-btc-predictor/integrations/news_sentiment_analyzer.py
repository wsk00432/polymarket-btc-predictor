#!/usr/bin/env python3
"""
News Sentiment Analyzer for BTC Predictor
Analyzes news sentiment from ClawFeed and other sources
"""

import re
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class NewsSentimentAnalyzer:
    """
    Analyzes sentiment from news articles and social media
    Integrates with ClawFeed for news collection
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "/root/clawd/projects/polymarket-btc-predictor/news_sources/crypto_news_sources.json"
        self.sentiment_weights = {
            'positive_keywords': {
                'surge': 0.8, 'soar': 0.8, 'rally': 0.7, 'gain': 0.6, 'rise': 0.6,
                'bullish': 0.7, 'breakout': 0.8, 'record': 0.6, 'high': 0.5,
                'adoption': 0.6, 'institutional': 0.5, 'etf': 0.6, 'approval': 0.7,
                'growth': 0.6, 'positive': 0.7, 'optimistic': 0.7, 'upgrade': 0.6
            },
            'negative_keywords': {
                'crash': -0.8, 'plunge': -0.8, 'drop': -0.6, 'fall': -0.6, 'decline': -0.6,
                'bearish': -0.7, 'breakdown': -0.8, 'low': -0.5, 'sell': -0.5,
                'regulation': -0.4, 'ban': -0.8, 'crackdown': -0.8, 'warning': -0.6,
                'negative': -0.7, 'pessimistic': -0.7, 'downgrade': -0.6, 'concern': -0.5
            },
            'neutral_keywords': {
                'stable', 'steady', 'unchanged', 'sideways', 'consolidate'
            }
        }
        
        # Load custom sentiment sources if available
        self.news_sources = self._load_news_sources()
        
        logger.info("News Sentiment Analyzer initialized")
    
    def _load_news_sources(self) -> Dict:
        """Load news source configurations"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading news sources: {e}")
        
        # Default sources
        return {
            'sources': [
                {'name': 'CoinDesk', 'type': 'news', 'weight': 1.0},
                {'name': 'Cointelegraph', 'type': 'news', 'weight': 1.0},
                {'name': 'The Block', 'type': 'news', 'weight': 0.9},
                {'name': 'Decrypt', 'type': 'news', 'weight': 0.8},
                {'name': 'Bitcoin Magazine', 'type': 'news', 'weight': 0.9}
            ],
            'social_media': [
                {'name': 'twitter', 'weight': 0.7},
                {'name': 'reddit', 'weight': 0.6}
            ]
        }
    
    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        Analyze sentiment of a text
        
        Args:
            text: Text to analyze
        
        Returns:
            Tuple of (sentiment_score, sentiment_label)
            Score range: -1.0 (very negative) to 1.0 (very positive)
        """
        if not text:
            return 0.0, 'neutral'
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        total_score = 0.0
        word_count = 0
        
        # Check positive keywords
        for word in words:
            if word in self.sentiment_weights['positive_keywords']:
                total_score += self.sentiment_weights['positive_keywords'][word]
                word_count += 1
            elif word in self.sentiment_weights['negative_keywords']:
                total_score += self.sentiment_weights['negative_keywords'][word]
                word_count += 1
        
        # Normalize score
        if word_count > 0:
            avg_score = total_score / word_count
            # Clamp to [-1, 1]
            normalized_score = max(-1.0, min(1.0, avg_score))
        else:
            normalized_score = 0.0
        
        # Determine label
        if normalized_score > 0.2:
            label = 'positive'
        elif normalized_score < -0.2:
            label = 'negative'
        else:
            label = 'neutral'
        
        return normalized_score, label
    
    def analyze_news_batch(self, news_items: List[Dict]) -> Dict:
        """
        Analyze sentiment for a batch of news items
        
        Args:
            news_items: List of news items with 'title', 'content', 'source'
        
        Returns:
            Dictionary with aggregated sentiment analysis
        """
        if not news_items:
            return {
                'combined_sentiment': 0.0,
                'sentiment_label': 'neutral',
                'item_count': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'source_breakdown': {},
                'timestamp': datetime.now().isoformat()
            }
        
        total_score = 0.0
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        source_scores = {}
        
        for item in news_items:
            # Combine title and content for analysis
            text = f"{item.get('title', '')} {item.get('content', '')}"
            score, label = self.analyze_sentiment(text)
            
            # Apply source weight
            source = item.get('source', 'unknown')
            source_weight = self._get_source_weight(source)
            weighted_score = score * source_weight
            
            total_score += weighted_score
            
            if label == 'positive':
                positive_count += 1
            elif label == 'negative':
                negative_count += 1
            else:
                neutral_count += 1
            
            # Track source breakdown
            if source not in source_scores:
                source_scores[source] = {'total': 0.0, 'count': 0}
            source_scores[source]['total'] += weighted_score
            source_scores[source]['count'] += 1
        
        # Calculate averages
        item_count = len(news_items)
        combined_score = total_score / item_count if item_count > 0 else 0.0
        
        # Determine overall label
        if combined_score > 0.2:
            combined_label = 'positive'
        elif combined_score < -0.2:
            combined_label = 'negative'
        else:
            combined_label = 'neutral'
        
        # Calculate source averages
        source_breakdown = {}
        for source, data in source_scores.items():
            source_breakdown[source] = {
                'avg_score': data['total'] / data['count'],
                'count': data['count']
            }
        
        return {
            'combined_sentiment': combined_score,
            'sentiment_label': combined_label,
            'item_count': item_count,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'source_breakdown': source_breakdown,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_source_weight(self, source: str) -> float:
        """Get weight for a news source"""
        source_lower = source.lower()
        
        for src_config in self.news_sources.get('sources', []):
            if src_config['name'].lower() in source_lower:
                return src_config.get('weight', 1.0)
        
        # Default weight for unknown sources
        return 0.8
    
    def get_sentiment_trend(self, historical_data: List[Dict]) -> str:
        """
        Analyze sentiment trend from historical data
        
        Args:
            historical_data: List of historical sentiment analyses
        
        Returns:
            Trend description: 'improving', 'declining', 'stable'
        """
        if len(historical_data) < 2:
            return 'stable'
        
        # Compare recent vs older sentiment
        mid_point = len(historical_data) // 2
        recent_avg = sum(d.get('combined_sentiment', 0) for d in historical_data[:mid_point]) / mid_point
        older_avg = sum(d.get('combined_sentiment', 0) for d in historical_data[mid_point:]) / (len(historical_data) - mid_point)
        
        diff = recent_avg - older_avg
        
        if diff > 0.1:
            return 'improving'
        elif diff < -0.1:
            return 'declining'
        else:
            return 'stable'


def create_news_sentiment_analyzer() -> NewsSentimentAnalyzer:
    """Factory function to create sentiment analyzer"""
    return NewsSentimentAnalyzer()


if __name__ == "__main__":
    # Test the analyzer
    logging.basicConfig(level=logging.INFO)
    
    analyzer = NewsSentimentAnalyzer()
    
    # Test with sample news
    test_news = [
        {
            'title': 'Bitcoin Surges Past $66,000 as Institutional Interest Grows',
            'content': 'Major institutional investors continue to accumulate Bitcoin as ETF inflows reach record highs.',
            'source': 'CoinDesk'
        },
        {
            'title': 'Crypto Market Faces Pressure from Regulatory Concerns',
            'content': 'Global regulatory uncertainty continues to weigh on cryptocurrency markets.',
            'source': 'Cointelegraph'
        },
        {
            'title': 'Ethereum Network Upgrade Successfully Deployed',
            'content': 'The latest Ethereum network upgrade has been successfully implemented, improving scalability.',
            'source': 'The Block'
        }
    ]
    
    result = analyzer.analyze_news_batch(test_news)
    
    print("\nSentiment Analysis Results:")
    print(f"Combined Sentiment: {result['combined_sentiment']:.3f}")
    print(f"Sentiment Label: {result['sentiment_label']}")
    print(f"Total Items: {result['item_count']}")
    print(f"Positive: {result['positive_count']} | Negative: {result['negative_count']} | Neutral: {result['neutral_count']}")
    print(f"\nSource Breakdown:")
    for source, data in result['source_breakdown'].items():
        print(f"  {source}: {data['avg_score']:.3f} ({data['count']} items)")
