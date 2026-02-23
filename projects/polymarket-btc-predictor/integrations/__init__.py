"""
Integrations package for BTC Predictor
External service integrations including ClawFeed, news sentiment analysis, etc.
"""

from .clawfeed_client import ClawFeedClient, MockClawFeedClient, create_clawfeed_client
from .news_sentiment_analyzer import NewsSentimentAnalyzer, create_news_sentiment_analyzer

__all__ = [
    'ClawFeedClient',
    'MockClawFeedClient',
    'create_clawfeed_client',
    'NewsSentimentAnalyzer',
    'create_news_sentiment_analyzer'
]
