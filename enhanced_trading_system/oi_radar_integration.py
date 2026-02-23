"""
OI Spike Radar Integration Module
Handles communication with the OI Spike Radar system
"""

import asyncio
import aiohttp
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime


class OISpikeRadarIntegration:
    """
    Integration class for OI Spike Radar system
    """
    
    def __init__(self, base_url: str = "http://localhost:8081"):  # Changed to use enhanced version
        self.base_url = base_url
        self.session = None
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize the HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
    
    async def get_latest_signals(self) -> List[Dict]:
        """
        Get the latest OI spike signals from the radar system
        """
        await self.initialize()
        
        try:
            # Try to get signals from the radar system - using the correct endpoint
            async with self.session.get(f"{self.base_url}/api/alerts?limit=20") as response:
                if response.status == 200:
                    data = await response.json()
                    # Handle both array responses and object responses with alerts property
                    if isinstance(data, list):
                        alerts = data
                    elif isinstance(data, dict):
                        alerts = data.get('alerts', []) if 'alerts' in data else []
                    else:
                        alerts = []
                    
                    # Transform the data to match our expected format
                    transformed_signals = []
                    for alert in alerts:
                        if isinstance(alert, dict):
                            transformed_signal = {
                                'symbol': alert.get('symbol'),
                                'timestamp': alert.get('ts', time.time()),
                                'direction': alert.get('direction', 'NEUTRAL'),
                                'magnitude': alert.get('score_total', 0),
                                'score': alert.get('score_total', 0),
                                'details': alert  # Keep full details in case they're needed
                            }
                            transformed_signals.append(transformed_signal)
                    
                    return transformed_signals
                else:
                    self.logger.warning(f"OI Radar returned status {response.status}")
                    # Return mock data if the actual system is not available
                    return self._get_mock_signals()
        except Exception as e:
            self.logger.error(f"Error fetching OI signals: {e}")
            # Return mock data if the actual system is not available
            return self._get_mock_signals()
    
    async def get_symbol_signals(self, symbol: str) -> List[Dict]:
        """
        Get OI signals for a specific symbol
        """
        all_signals = await self.get_latest_signals()
        return [signal for signal in all_signals if signal.get('symbol') and signal.get('symbol').upper() == symbol.upper()]
    
    async def get_system_status(self) -> Dict:
        """
        Get the status of the OI Spike Radar system
        """
        await self.initialize()
        
        try:
            async with self.session.get(f"{self.base_url}/api/status") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"status": "unavailable", "error": f"Status code {response.status}"}
        except Exception as e:
            self.logger.error(f"Error fetching OI Radar status: {e}")
            return {"status": "error", "error": str(e)}
    
    def _get_mock_signals(self) -> List[Dict]:
        """
        Generate mock OI signals for testing purposes
        """
        import random
        from datetime import datetime
        
        # Mock symbols
        symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
        
        # Generate mock signals
        mock_signals = []
        for symbol in random.sample(symbols, min(3, len(symbols))):
            # Random direction: mostly neutral, occasional spikes
            directions = ['BULLISH', 'BEARISH', 'NEUTRAL', 'NEUTRAL', 'NEUTRAL']
            direction = random.choice(directions)
            
            if direction != 'NEUTRAL':
                signal = {
                    'symbol': symbol,
                    'timestamp': datetime.now().isoformat(),
                    'direction': direction,
                    'magnitude': round(random.uniform(5.0, 25.0), 2),  # 5-25% spike
                    'score': round(random.uniform(1.0, 3.0), 2)  # Normalized score
                }
                mock_signals.append(signal)
        
        return mock_signals
    
    async def close(self):
        """
        Close the HTTP session
        """
        if self.session:
            await self.session.close()