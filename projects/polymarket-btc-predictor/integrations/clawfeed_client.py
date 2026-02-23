#!/usr/bin/env python3
"""
ClawFeed Client for BTC Predictor
Fetches news from ClawFeed API for sentiment analysis
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ClawFeedClient:
    """Client for interacting with ClawFeed API"""
    
    def __init__(self, api_url: str = "http://localhost:8767", api_key: Optional[str] = None):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
    
    def get_digests(self, digest_type: str = '4h', limit: int = 20) -> List[Dict]:
        """
        Fetch digests from ClawFeed
        
        Args:
            digest_type: Type of digest (4h, daily, weekly, monthly)
            limit: Maximum number of digests to fetch
        
        Returns:
            List of digest objects
        """
        try:
            url = f"{self.api_url}/api/digests"
            params = {
                'type': digest_type,
                'limit': limit
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched {len(data)} {digest_type} digests from ClawFeed")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching digests: {e}")
            return []
    
    def get_latest_news(self, sources: List[str] = None, limit: int = 50) -> List[Dict]:
        """
        Fetch latest news items
        
        Args:
            sources: List of source names to filter by
            limit: Maximum number of news items
        
        Returns:
            List of news items with title, content, source, timestamp
        """
        try:
            # Get the latest digest and extract news items
            digests = self.get_digests('4h', limit=1)
            
            if not digests:
                logger.warning("No digests available")
                return []
            
            latest_digest = digests[0]
            news_items = []
            
            # Extract news from digest structure
            # Note: Actual structure depends on ClawFeed's digest format
            if 'items' in latest_digest:
                for item in latest_digest['items']:
                    if sources is None or item.get('source') in sources:
                        news_items.append({
                            'title': item.get('title', ''),
                            'content': item.get('summary', item.get('content', '')),
                            'source': item.get('source', 'unknown'),
                            'url': item.get('url', ''),
                            'timestamp': item.get('timestamp', datetime.now().isoformat())
                        })
                        
                        if len(news_items) >= limit:
                            break
            
            logger.info(f"Extracted {len(news_items)} news items")
            return news_items
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    def get_crypto_news(self, limit: int = 50) -> List[Dict]:
        """
        Fetch cryptocurrency-related news
        
        Args:
            limit: Maximum number of news items
        
        Returns:
            List of crypto-related news items
        """
        # Filter for crypto-related sources
        crypto_sources = [
            'CoinDesk',
            'Cointelegraph',
            'The Block',
            'Decrypt',
            'Bitcoin Magazine',
            'CryptoSlate',
            'coindesk-twitter',
            'cointelegraph-twitter'
        ]
        
        return self.get_latest_news(sources=crypto_sources, limit=limit)
    
    def health_check(self) -> bool:
        """Check if ClawFeed API is available"""
        try:
            response = self.session.get(f"{self.api_url}/api/digests", params={'limit': 1}, timeout=5)
            return response.status_code == 200
        except:
            return False


class MockClawFeedClient:
    """
    Mock ClawFeed client for testing and fallback
    Simulates news data when ClawFeed is not available
    """
    
    def __init__(self):
        self.sample_news = [
            {
                'title': 'Bitcoin Surges Past $66,000 as Institutional Interest Grows',
                'content': 'Major institutional investors continue to accumulate Bitcoin as ETF inflows reach record highs.',
                'source': 'CoinDesk',
                'sentiment': 'positive'
            },
            {
                'title': 'SEC Delays Decision on Ethereum ETF Applications',
                'content': 'The Securities and Exchange Commission has postponed its decision on multiple Ethereum ETF applications.',
                'source': 'The Block',
                'sentiment': 'neutral'
            },
            {
                'title': 'Crypto Market Faces Pressure from Regulatory Concerns',
                'content': 'Global regulatory uncertainty continues to weigh on cryptocurrency markets.',
                'source': 'Cointelegraph',
                'sentiment': 'negative'
            }
        ]
    
    def get_crypto_news(self, limit: int = 50) -> List[Dict]:
        """Return sample crypto news"""
        import random
        from datetime import datetime
        
        news = []
        for i in range(min(limit, len(self.sample_news))):
            item = self.sample_news[i].copy()
            item['timestamp'] = (datetime.now() - timedelta(hours=i)).isoformat()
            item['url'] = f'https://example.com/news/{i}'
            news.append(item)
        
        logger.info(f"Generated {len(news)} mock news items")
        return news
    
    def health_check(self) -> bool:
        """Mock client is always available"""
        return True


def create_clawfeed_client(api_url: str = "http://localhost:8767", api_key: str = None, use_mock: bool = False) -> ClawFeedClient:
    """
    Factory function to create appropriate ClawFeed client
    
    Args:
        api_url: ClawFeed API URL
        api_key: API key for authentication
        use_mock: Force use of mock client
    
    Returns:
        ClawFeedClient or MockClawFeedClient instance
    """
    if use_mock:
        logger.info("Using MockClawFeedClient")
        return MockClawFeedClient()
    
    try:
        client = ClawFeedClient(api_url, api_key)
        if client.health_check():
            logger.info(f"Connected to ClawFeed API at {api_url}")
            return client
        else:
            logger.warning("ClawFeed API health check failed, falling back to mock client")
            return MockClawFeedClient()
    except Exception as e:
        logger.error(f"Failed to connect to ClawFeed: {e}, using mock client")
        return MockClawFeedClient()


if __name__ == "__main__":
    # Test the client
    logging.basicConfig(level=logging.INFO)
    
    print("Testing ClawFeed Client...")
    client = create_clawfeed_client()
    
    print(f"Health check: {client.health_check()}")
    
    news = client.get_crypto_news(limit=5)
    print(f"\nRetrieved {len(news)} news items:")
    for item in news:
        print(f"  - {item['title']} ({item['source']})")
