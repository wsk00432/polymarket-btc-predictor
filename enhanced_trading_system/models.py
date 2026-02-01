"""
Data models for the Enhanced Trading Analysis System
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class SignalDirection(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class Recommendation(Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


@dataclass
class TechnicalIndicators:
    """Technical indicators data"""
    symbol: str
    timestamp: datetime
    rsi: float
    macd: Dict[str, float]
    bollinger_bands: Dict[str, float]
    moving_averages: Dict[str, float]
    
    def to_dict(self):
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class KlineData:
    """K-line data structure"""
    symbol: str
    open_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: int
    quote_asset_volume: float
    number_of_trades: int
    taker_buy_base_asset_volume: float
    taker_buy_quote_asset_volume: float
    
    def to_dict(self):
        return asdict(self)


@dataclass
class OrderBookDepth:
    """Order book depth data"""
    symbol: str
    timestamp: datetime
    bids: List[Dict[str, float]]
    asks: List[Dict[str, float]]
    bid_volume: float
    ask_volume: float
    bid_cumulative: List[float]
    ask_cumulative: List[float]
    spread: float
    spread_percentage: float
    
    def to_dict(self):
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class FundFlow:
    """Fund flow analysis data"""
    symbol: str
    timestamp: datetime
    buy_volume: float
    sell_volume: float
    total_volume: float
    buy_ratio: float
    sell_ratio: float
    net_flow: float
    buy_trade_count: int
    sell_trade_count: int
    flow_direction: SignalDirection
    
    def to_dict(self):
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['flow_direction'] = self.flow_direction.value
        return result


@dataclass
class OISignal:
    """Open Interest signal data"""
    symbol: str
    timestamp: datetime
    magnitude: float
    direction: SignalDirection
    source: str = "external"  # Source of the OI signal
    
    def to_dict(self):
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['direction'] = self.direction.value
        return result


@dataclass
class RiskParameters:
    """Risk management parameters"""
    stop_loss: Optional[float]
    take_profit: Optional[float]
    risk_percentage: float
    risk_reward_ratio: float
    
    def to_dict(self):
        return asdict(self)


@dataclass
class TradingSignal:
    """Integrated trading signal"""
    symbol: str
    timestamp: datetime
    composite_score: float
    score_components: Dict[str, float]
    recommendation: Recommendation
    confidence_level: float
    technical_indicators: Optional[TechnicalIndicators] = None
    oi_signals: Optional[OISignal] = None
    fund_flow: Optional[FundFlow] = None
    risk_management: Optional[RiskParameters] = None
    volatility: Optional[float] = None
    
    def to_dict(self):
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['recommendation'] = self.recommendation.value
        
        # Convert nested objects to dict if they exist
        if self.technical_indicators:
            result['technical_indicators'] = self.technical_indicators.to_dict()
        if self.oi_signals:
            result['oi_signals'] = self.oi_signals.to_dict()
        if self.fund_flow:
            result['fund_flow'] = self.fund_flow.to_dict()
        if self.risk_management:
            result['risk_management'] = self.risk_management.to_dict()
        
        return result


@dataclass
class TradingSignalPanel:
    """Collection of trading signals for multiple symbols"""
    timestamp: datetime
    signals: List[TradingSignal]
    market_conditions: Dict[str, float] = None  # Overall market metrics
    
    def to_dict(self):
        result = {
            'timestamp': self.timestamp.isoformat(),
            'signals': [signal.to_dict() for signal in self.signals],
            'market_conditions': self.market_conditions or {}
        }
        return result


@dataclass
class HistoricalDataPoint:
    """Historical data point for backtesting and analysis"""
    symbol: str
    timestamp: datetime
    price: float
    volume: float
    indicators: Dict[str, float]  # All calculated indicators at this point
    signal: Optional[Recommendation] = None
    actual_return: Optional[float] = None  # Actual return after some period
    
    def to_dict(self):
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        if self.signal:
            result['signal'] = self.signal.value
        return result


# Additional utility classes
@dataclass
class MarketSnapshot:
    """Complete market snapshot at a point in time"""
    timestamp: datetime
    symbol: str
    price: float
    volume: float
    technical_indicators: TechnicalIndicators
    order_book: OrderBookDepth
    fund_flow: FundFlow
    oi_data: OISignal
    
    def to_dict(self):
        result = {
            'timestamp': self.timestamp.isoformat(),
            'symbol': self.symbol,
            'price': self.price,
            'volume': self.volume,
            'technical_indicators': self.technical_indicators.to_dict(),
            'order_book': self.order_book.to_dict(),
            'fund_flow': self.fund_flow.to_dict(),
            'oi_data': self.oi_data.to_dict()
        }
        return result


@dataclass
class BacktestResult:
    """Result of a backtesting operation"""
    strategy_name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    trades_executed: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    
    def to_dict(self):
        result = asdict(self)
        result['start_date'] = self.start_date.isoformat()
        result['end_date'] = self.end_date.isoformat()
        return result