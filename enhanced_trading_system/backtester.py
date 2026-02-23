"""
Backtesting module for the Enhanced Trading Analysis System
Allows testing of trading strategies on historical data
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Callable
from dataclasses import asdict

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import HistoricalDataPoint, BacktestResult, TradingSignal, Recommendation
from utils import calculate_sharpe_ratio, calculate_atr
from config import get_config


class Backtester:
    """
    Backtesting engine for evaluating trading strategies
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.data = []
        self.signals = []
        self.trades = []
        self.results = None
    
    def load_historical_data(self, data_points: List[HistoricalDataPoint]):
        """
        Load historical data for backtesting
        """
        self.data = sorted(data_points, key=lambda x: x.timestamp)
        print(f"Loaded {len(self.data)} historical data points for backtesting")
    
    def apply_strategy(self, strategy_func: Callable[[HistoricalDataPoint], Recommendation]) -> List[TradingSignal]:
        """
        Apply a trading strategy to historical data
        """
        signals = []
        
        for data_point in self.data:
            recommendation = strategy_func(data_point)
            
            signal = TradingSignal(
                symbol=data_point.symbol,
                timestamp=data_point.timestamp,
                composite_score=0.0,  # Will calculate based on recommendation
                score_components={},
                recommendation=recommendation,
                confidence_level=80.0,  # Assume 80% confidence for backtesting
                technical_indicators=None,
                oi_signals=None,
                fund_flow=None,
                risk_management=None,
                volatility=None
            )
            
            # Set composite score based on recommendation
            if recommendation == Recommendation.STRONG_BUY:
                signal.composite_score = 0.8
            elif recommendation == Recommendation.BUY:
                signal.composite_score = 0.5
            elif recommendation == Recommendation.HOLD:
                signal.composite_score = 0.0
            elif recommendation == Recommendation.SELL:
                signal.composite_score = -0.5
            elif recommendation == Recommendation.STRONG_SELL:
                signal.composite_score = -0.8
            
            signals.append(signal)
        
        self.signals = signals
        return signals
    
    def run_backtest(self, commission_rate: float = 0.001, slippage: float = 0.0005) -> BacktestResult:
        """
        Run the backtest simulation
        """
        if not self.data or not self.signals:
            raise ValueError("No data or signals loaded for backtesting")
        
        # Initialize portfolio
        cash = self.initial_capital
        position = 0  # Number of assets held
        position_value = 0  # Value of position in dollars
        portfolio_values = [self.initial_capital]
        trade_history = []
        returns = []
        
        # Align data and signals by timestamp
        data_idx = 0
        signal_idx = 0
        
        while data_idx < len(self.data) and signal_idx < len(self.signals):
            data_point = self.data[data_idx]
            signal = self.signals[signal_idx]
            
            # Move forward until timestamps align (or close enough)
            if data_point.timestamp < signal.timestamp:
                data_idx += 1
                continue
            elif signal.timestamp < data_point.timestamp:
                signal_idx += 1
                continue
            
            # Execute trading logic based on signal
            current_price = data_point.price
            recommendation = signal.recommendation
            
            # Calculate current portfolio value
            total_value = cash + (position * current_price)
            
            # Execute trade based on signal
            if recommendation in [Recommendation.STRONG_BUY, Recommendation.BUY] and position <= 0:
                # Enter long position
                shares_to_buy = cash / current_price
                cost = shares_to_buy * current_price
                transaction_cost = cost * commission_rate
                actual_cost = cost + transaction_cost
                
                if actual_cost <= cash:
                    position += shares_to_buy
                    cash -= actual_cost
                    
                    trade_history.append({
                        'timestamp': data_point.timestamp,
                        'action': 'BUY',
                        'price': current_price,
                        'shares': shares_to_buy,
                        'cost': actual_cost,
                        'portfolio_value': total_value
                    })
            
            elif recommendation in [Recommendation.STRONG_SELL, Recommendation.SELL] and position > 0:
                # Exit long position
                revenue = position * current_price
                transaction_cost = revenue * commission_rate
                actual_revenue = revenue - transaction_cost
                
                cash += actual_revenue
                position = 0
                
                trade_history.append({
                    'timestamp': data_point.timestamp,
                    'action': 'SELL',
                    'price': current_price,
                    'shares': position,
                    'revenue': actual_revenue,
                    'portfolio_value': total_value
                })
            
            # Record portfolio value
            portfolio_values.append(cash + (position * current_price))
            
            # Calculate daily return if possible
            if len(portfolio_values) > 1:
                daily_return = (portfolio_values[-1] - portfolio_values[-2]) / portfolio_values[-2]
                returns.append(daily_return)
            
            # Move to next data point
            data_idx += 1
            signal_idx += 1
        
        # Calculate final portfolio value (liquidate any remaining position)
        final_value = cash + (position * self.data[-1].price)
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # Calculate performance metrics
        if len(returns) > 1:
            avg_daily_return = np.mean(returns)
            volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
            sharpe_ratio = calculate_sharpe_ratio(returns)
            
            # Calculate drawdowns
            running_max = portfolio_values[0]
            drawdowns = []
            for value in portfolio_values:
                if value > running_max:
                    running_max = value
                drawdown = (value - running_max) / running_max
                drawdowns.append(drawdown)
            max_drawdown = min(drawdowns) if drawdowns else 0
        else:
            avg_daily_return = 0
            volatility = 0
            sharpe_ratio = 0
            max_drawdown = 0
        
        # Count trades
        winning_trades = 0
        losing_trades = 0
        avg_win = 0
        avg_loss = 0
        
        trade_pnl = []
        for i in range(1, len(trade_history)):
            if trade_history[i]['action'] == 'SELL' and i > 0:
                # Calculate P&L for this trade cycle
                buy_idx = i - 1
                if trade_history[buy_idx]['action'] == 'BUY':
                    buy_price = trade_history[buy_idx]['price']
                    sell_price = trade_history[i]['price']
                    pnl = (sell_price - buy_price) / buy_price
                    trade_pnl.append(pnl)
        
        if trade_pnl:
            winning_trades = len([pnl for pnl in trade_pnl if pnl > 0])
            losing_trades = len([pnl for pnl in trade_pnl if pnl < 0])
            
            wins = [pnl for pnl in trade_pnl if pnl > 0]
            losses = [pnl for pnl in trade_pnl if pnl < 0]
            
            avg_win = np.mean(wins) if wins else 0
            avg_loss = np.mean(losses) if losses else 0
        
        win_rate = winning_trades / len(trade_pnl) if trade_pnl else 0
        
        # Calculate annualized return
        years = (self.data[-1].timestamp - self.data[0].timestamp).days / 365.25
        annualized_return = (final_value / self.initial_capital) ** (1 / years) - 1 if years > 0 else 0
        
        # Create backtest result
        self.results = BacktestResult(
            strategy_name="Enhanced Trading System Strategy",
            start_date=self.data[0].timestamp,
            end_date=self.data[-1].timestamp,
            initial_capital=self.initial_capital,
            final_capital=final_value,
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            trades_executed=len(trade_history),
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_win=avg_win,
            avg_loss=avg_loss
        )
        
        self.trades = trade_history
        
        return self.results
    
    def generate_report(self) -> str:
        """
        Generate a detailed backtest report
        """
        if not self.results:
            return "No backtest results available. Run backtest first."
        
        report = f"""
BACKTEST RESULTS REPORT
=======================
Strategy: {self.results.strategy_name}
Period: {self.results.start_date.strftime('%Y-%m-%d')} to {self.results.end_date.strftime('%Y-%m-%d')}
Initial Capital: ${self.results.initial_capital:,.2f}
Final Capital: ${self.results.final_capital:,.2f}

PERFORMANCE METRICS
===================
Total Return: {self.results.total_return:.2%}
Annualized Return: {self.results.annualized_return:.2%}
Volatility (Ann.): {self.results.volatility:.2%}
Sharpe Ratio: {self.results.sharpe_ratio:.2f}
Max Drawdown: {self.results.max_drawdown:.2%}
Win Rate: {self.results.win_rate:.2%}
Trades Executed: {self.results.trades_executed}
Winning Trades: {self.results.winning_trades}
Losing Trades: {self.results.losing_trades}
Avg Win: {self.results.avg_win:.2%}
Avg Loss: {self.results.avg_loss:.2%}

SUMMARY
=======
The strategy resulted in a ${self.results.final_capital - self.results.initial_capital:,.2f} 
change in portfolio value over the test period.
"""
        return report
    
    def plot_results(self, show_plot: bool = True):
        """
        Plot backtest results (requires matplotlib)
        """
        try:
            import matplotlib.pyplot as plt
            
            if not self.data or not self.signals:
                print("No data available for plotting")
                return
            
            # Align data points for plotting
            timestamps = []
            portfolio_values = [self.initial_capital]
            prices = []
            
            # This is simplified - in a real implementation you'd track portfolio value at each step
            # For now, we'll just plot the raw price data
            for dp in self.data:
                timestamps.append(dp.timestamp)
                prices.append(dp.price)
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Plot price
            ax1.plot(timestamps, prices, label='Asset Price', color='blue')
            ax1.set_title('Asset Price Over Time')
            ax1.set_ylabel('Price ($)')
            ax1.legend()
            ax1.grid(True)
            
            # Plot portfolio value if we have it
            if len(portfolio_values) == len(timestamps):
                ax2.plot(timestamps, portfolio_values, label='Portfolio Value', color='green')
            ax2.set_title('Portfolio Value Over Time')
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Value ($)')
            ax2.legend()
            ax2.grid(True)
            
            plt.tight_layout()
            
            if show_plot:
                plt.show()
            else:
                plt.savefig('backtest_results.png')
                print("Backtest results saved to backtest_results.png")
                
        except ImportError:
            print("Matplotlib not available. Install with: pip install matplotlib")
        except Exception as e:
            print(f"Error plotting results: {e}")


def create_sample_strategy(data_point: HistoricalDataPoint) -> Recommendation:
    """
    Sample trading strategy based on technical indicators
    This is a simple example - real strategies would be more sophisticated
    """
    indicators = data_point.indicators
    
    # Extract indicator values
    rsi = indicators.get('rsi', 50)
    price = data_point.price
    
    # Simple RSI-based strategy
    if rsi < 30:  # Oversold
        return Recommendation.BUY
    elif rsi > 70:  # Overbought
        return Recommendation.SELL
    else:
        return Recommendation.HOLD


def create_advanced_strategy(data_point: HistoricalDataPoint) -> Recommendation:
    """
    More advanced strategy combining multiple indicators
    """
    indicators = data_point.indicators
    
    # Extract key indicators
    rsi = indicators.get('rsi', 50)
    macd = indicators.get('macd', 0)
    bb_pos = indicators.get('bb_position', 0.5)  # Position within Bollinger Bands (0-1)
    ma_trend = indicators.get('ma_trend', 0)  # -1 for downtrend, 1 for uptrend
    momentum = indicators.get('momentum', 0)
    
    # Calculate composite signal
    rsi_signal = 0
    if rsi < 30:
        rsi_signal = 1  # Strong buy signal
    elif rsi < 40:
        rsi_signal = 0.5  # Moderate buy signal
    elif rsi > 70:
        rsi_signal = -1  # Strong sell signal
    elif rsi > 60:
        rsi_signal = -0.5  # Moderate sell signal
    
    # MACD signal
    macd_signal = 1 if macd > 0.01 else -1 if macd < -0.01 else 0
    
    # Bollinger Bands signal
    bb_signal = 0
    if bb_pos < 0.1:  # Below lower band
        bb_signal = 1
    elif bb_pos > 0.9:  # Above upper band
        bb_signal = -1
    
    # Moving average trend
    trend_signal = ma_trend
    
    # Combine signals with weights
    composite_score = (
        0.3 * rsi_signal +
        0.2 * macd_signal +
        0.2 * bb_signal +
        0.3 * trend_signal
    )
    
    # Convert to recommendation
    if composite_score >= 0.6:
        return Recommendation.STRONG_BUY
    elif composite_score >= 0.2:
        return Recommendation.BUY
    elif composite_score >= -0.2:
        return Recommendation.HOLD
    elif composite_score >= -0.6:
        return Recommendation.SELL
    else:
        return Recommendation.STRONG_SELL


def simulate_indicator_calculation(historical_data: List[HistoricalDataPoint]) -> List[HistoricalDataPoint]:
    """
    Simulate the calculation of technical indicators for historical data
    This would normally be done by the main trading system
    """
    import random
    
    processed_data = []
    
    for i, data_point in enumerate(historical_data):
        # Calculate indicators based on previous prices
        if i < 14:  # Need at least 14 points for RSI
            # Use random values for early points
            indicators = {
                'rsi': random.uniform(30, 70),
                'macd': random.uniform(-0.1, 0.1),
                'bb_position': random.uniform(0.2, 0.8),
                'ma_trend': random.choice([-1, 0, 1]),
                'momentum': random.uniform(-0.05, 0.05)
            }
        else:
            # Calculate actual indicators (simplified versions)
            # Get previous 14 closing prices
            recent_prices = [dp.price for dp in historical_data[max(0, i-14):i+1]]
            
            # Calculate RSI (simplified)
            if len(recent_prices) > 1:
                deltas = [recent_prices[j] - recent_prices[j-1] for j in range(1, len(recent_prices))]
                gains = [d if d > 0 else 0 for d in deltas]
                losses = [-d if d < 0 else 0 for d in deltas]
                
                avg_gain = sum(gains[-14:]) / 14
                avg_loss = sum(losses[-14:]) / 14 if sum(losses[-14:]) > 0 else 0.01
                
                rs = avg_gain / avg_loss if avg_loss != 0 else 100
                rsi = 100 - (100 / (1 + rs))
            else:
                rsi = 50
            
            # Simplified MACD
            macd = (data_point.price - np.mean([dp.price for dp in historical_data[max(0, i-12):i+1]])) * 0.1
            
            # Bollinger Band position
            ma_20 = np.mean([dp.price for dp in historical_data[max(0, i-19):i+1]])
            std_20 = np.std([dp.price for dp in historical_data[max(0, i-19):i+1]])
            upper_band = ma_20 + 2 * std_20
            lower_band = ma_20 - 2 * std_20
            
            if upper_band == lower_band:
                bb_pos = 0.5
            else:
                bb_pos = (data_point.price - lower_band) / (upper_band - lower_band)
                bb_pos = max(0, min(1, bb_pos))  # Clamp to [0, 1]
            
            # Moving average trend
            if i >= 20:
                ma_5 = np.mean([dp.price for dp in historical_data[i-4:i+1]])
                ma_20 = np.mean([dp.price for dp in historical_data[i-19:i+1]])
                ma_trend = 1 if ma_5 > ma_20 else -1
            else:
                ma_trend = 0
            
            # Momentum
            if i >= 10:
                momentum = (data_point.price - historical_data[i-10].price) / historical_data[i-10].price
            else:
                momentum = 0
            
            indicators = {
                'rsi': rsi,
                'macd': macd,
                'bb_position': bb_pos,
                'ma_trend': ma_trend,
                'momentum': momentum
            }
        
        # Create new data point with indicators
        updated_point = HistoricalDataPoint(
            symbol=data_point.symbol,
            timestamp=data_point.timestamp,
            price=data_point.price,
            volume=data_point.volume,
            indicators=indicators,
            signal=data_point.signal,
            actual_return=data_point.actual_return
        )
        processed_data.append(updated_point)
    
    return processed_data


# Example usage function
async def run_sample_backtest():
    """
    Run a sample backtest to demonstrate functionality
    """
    import random
    from datetime import timedelta
    
    # Generate sample historical data
    print("Generating sample historical data...")
    
    start_date = datetime.now() - timedelta(days=365)  # 1 year of data
    dates = [start_date + timedelta(days=i) for i in range(365)]
    
    # Generate somewhat realistic price data with trends and volatility
    prices = [10000]  # Starting price
    for i in range(1, len(dates)):
        # Random walk with slight upward bias
        change_percent = random.normalvariate(0.001, 0.02)  # Mean 0.1%, std 2%
        new_price = prices[-1] * (1 + change_percent)
        prices.append(new_price)
    
    # Create historical data points
    historical_data = []
    for i, date in enumerate(dates):
        data_point = HistoricalDataPoint(
            symbol="BTCUSDT",
            timestamp=date,
            price=prices[i],
            volume=random.uniform(1000, 10000),
            indicators={}  # Will be calculated
        )
        historical_data.append(data_point)
    
    # Calculate indicators for the historical data
    print("Calculating technical indicators...")
    historical_data_with_indicators = simulate_indicator_calculation(historical_data)
    
    # Create backtester instance
    backtester = Backtester(initial_capital=10000.0)
    
    # Load the data
    backtester.load_historical_data(historical_data_with_indicators)
    
    # Apply the advanced strategy
    print("Applying trading strategy...")
    signals = backtester.apply_strategy(create_advanced_strategy)
    
    # Run the backtest
    print("Running backtest...")
    results = backtester.run_backtest()
    
    # Generate and print report
    report = backtester.generate_report()
    print(report)
    
    # Optionally plot results
    # backtester.plot_results(show_plot=False)  # Set to True to show plot
    
    return results


if __name__ == "__main__":
    # Run the sample backtest
    asyncio.run(run_sample_backtest())