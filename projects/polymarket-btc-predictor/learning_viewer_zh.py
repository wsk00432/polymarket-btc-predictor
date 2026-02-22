#!/usr/bin/env python3
"""
Learning Process Viewer for BTC Predictor (Chinese Version)
Provides visibility into the self-learning process and historical adjustments in Chinese
"""

import json
import os
from datetime import datetime
from typing import Dict, List
import pandas as pd

class LearningViewer:
    def __init__(self):
        self.prediction_outcomes_path = "/root/clawd/projects/polymarket-btc-predictor/prediction_outcomes.json"
        self.performance_log_path = "/root/clawd/projects/polymarket-btc-predictor/performance_log.json"
        self.strategy_config_path = "/root/clawd/projects/polymarket-btc-predictor/strategy_config.json"
    
    def load_prediction_outcomes(self) -> Dict:
        """Load prediction outcomes from file"""
        if os.path.exists(self.prediction_outcomes_path):
            with open(self.prediction_outcomes_path, 'r') as f:
                return json.load(f)
        else:
            return {}
    
    def load_performance_log(self) -> List[Dict]:
        """Load performance log from file"""
        if os.path.exists(self.performance_log_path):
            with open(self.performance_log_path, 'r') as f:
                return json.load(f)
        else:
            return []
    
    def load_strategy_config(self) -> Dict:
        """Load current strategy configuration"""
        if os.path.exists(self.strategy_config_path):
            with open(self.strategy_config_path, 'r') as f:
                return json.load(f)
        else:
            return {}
    
    def get_learning_summary(self) -> Dict:
        """Get a summary of the learning process"""
        outcomes = self.load_prediction_outcomes()
        performance_log = self.load_performance_log()
        current_strategy = self.load_strategy_config()
        
        # Calculate overall accuracy
        total_predictions = len(outcomes)
        evaluated_predictions = 0
        correct_predictions = 0
        
        for pred_id, data in outcomes.items():
            if data['actual_outcome'] is not None:
                evaluated_predictions += 1
                if data['prediction']['prediction'] == data['actual_outcome']['direction']:
                    correct_predictions += 1
        
        overall_accuracy = correct_predictions / evaluated_predictions if evaluated_predictions > 0 else 0
        
        # Get recent performance
        recent_logs = performance_log[-20:] if performance_log else []
        if recent_logs:
            recent_correct = sum(1 for log in recent_logs if log['analysis']['is_correct'])
            recent_accuracy = recent_correct / len(recent_logs)
        else:
            recent_accuracy = 0
        
        return {
            'total_predictions': total_predictions,
            'evaluated_predictions': evaluated_predictions,
            'correct_predictions': correct_predictions,
            'overall_accuracy': overall_accuracy,
            'recent_accuracy': recent_accuracy,
            'performance_log_count': len(performance_log),
            'current_strategy': current_strategy
        }
    
    def get_detailed_learning_history(self) -> List[Dict]:
        """Get detailed learning history"""
        performance_log = self.load_performance_log()
        
        detailed_history = []
        for record in performance_log[-10:]:  # Last 10 records
            detailed_record = {
                'timestamp': record['timestamp'],
                'predicted_direction': record['predicted_direction'],
                'predicted_confidence': record['predicted_confidence'],
                'actual_direction': record.get('actual_direction', '待评估'),
                'is_correct': record['analysis']['is_correct'],
                'accuracy_score': record['analysis']['accuracy_score'],
                'market_volatility': record['analysis']['market_volatility'],
                'error_type': record['analysis']['error_type'],
                'indicators': record['indicators'],
                'sentiment_analysis': record.get('sentiment_analysis', {}),
                'technical_analysis': record.get('technical_analysis', {})
            }
            detailed_history.append(detailed_record)
        
        return detailed_history
    
    def print_learning_dashboard(self):
        """Print a comprehensive learning dashboard in Chinese"""
        print("="*100)
        print("🤖 BTC预测系统自我学习仪表板")
        print("="*100)
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Learning Summary
        summary = self.get_learning_summary()
        print("📊 学习摘要:")
        print(f"   总预测次数: {summary['total_predictions']}")
        print(f"   已评估预测: {summary['evaluated_predictions']}")
        print(f"   正确预测数: {summary['correct_predictions']}")
        print(f"   总体准确率: {summary['overall_accuracy']:.3f} ({summary['overall_accuracy']*100:.1f}%)")
        print(f"   近期准确率 (最近20次): {summary['recent_accuracy']:.3f} ({summary['recent_accuracy']*100:.1f}%)")
        print(f"   性能日志数: {summary['performance_log_count']}")
        print()
        
        # Current Strategy
        if summary['current_strategy']:
            print("⚙️  当前策略配置:")
            if 'indicator_weights' in summary['current_strategy']:
                print("   技术指标权重:")
                for indicator, weight in summary['current_strategy']['indicator_weights'].items():
                    # Translate indicator names to Chinese
                    indicator_names = {
                        'rsi': '相对强弱指数(RSI)',
                        'macd': '平滑异同移动平均线(MACD)',
                        'ma_trend': '移动平均趋势',
                        'volume': '成交量分析',
                        'bollinger': '布林带分析'
                    }
                    indicator_cn = indicator_names.get(indicator, indicator)
                    print(f"     - {indicator_cn}: {weight:.3f}")
            if 'sentiment_weight' in summary['current_strategy']:
                print(f"   情绪分析权重: {summary['current_strategy']['sentiment_weight']:.3f}")
            if 'confidence_threshold' in summary['current_strategy']:
                print(f"   置信度阈值: {summary['current_strategy']['confidence_threshold']:.3f}")
            print()
        
        # Detailed Learning History
        detailed_history = self.get_detailed_learning_history()
        if detailed_history:
            print("📚 最近学习历史 (最近10次):")
            print("-" * 100)
            print(f"{'时间':<20} {'预测':<6} {'置信度':<6} {'实际':<6} {'正确':<7} {'错误类型':<15} {'波动率':<10}")
            print("-" * 100)
            
            for record in detailed_history:
                # Extract and format timestamp properly
                timestamp = record['timestamp']
                # Handle different timestamp formats
                if '.' in timestamp:
                    # Format: 2026-02-03T07:24:25.284676
                    clean_timestamp = timestamp.split('.')[0]  # Remove milliseconds
                    time_str = clean_timestamp.replace('T', ' ')  # Replace T with space
                else:
                    # Format: 2026-02-03T07:24:25
                    time_str = timestamp.replace('T', ' ')
                pred = record['predicted_direction']
                conf = f"{record['predicted_confidence']:.2f}"
                actual = record['actual_direction']
                correct = "✓" if record['is_correct'] else "✗"
                
                # Translate error types to Chinese
                error_types = {
                    'correct_prediction': '预测正确',
                    'missed_opportunity': '错失机会',
                    'false_signal': '错误信号',
                    'direction_inverted_UP_to_DOWN': '方向反转(涨→跌)',
                    'direction_inverted_DOWN_to_UP': '方向反转(跌→涨)',
                    'other_error': '其他错误'
                }
                error_type = error_types.get(record['error_type'], record['error_type'])
                
                vol = f"{abs(record['market_volatility']):.3f}"
                
                print(f"{time_str:<20} {pred:<6} {conf:<6} {actual:<6} {correct:<7} {error_type:<15} {vol:<10}")
            print()
        
        # Learning Insights
        print("💡 学习洞察:")
        if summary['recent_accuracy'] > summary['overall_accuracy']:
            print("   • 近期表现相比整体表现有所改善")
        elif summary['recent_accuracy'] < summary['overall_accuracy']:
            print("   • 近期表现有所下滑，系统可能正在适应新的市场条件")
        else:
            print("   • 表现稳定")
        
        if summary['current_strategy'] and 'confidence_threshold' in summary['current_strategy']:
            print(f"   • 当前置信度阈值设定为 {summary['current_strategy']['confidence_threshold']:.2f}")
        
        if summary['evaluated_predictions'] > 0:
            hold_accuracy = self._calculate_hold_accuracy()
            up_accuracy = self._calculate_direction_accuracy('UP')
            down_accuracy = self._calculate_direction_accuracy('DOWN')
            
            print(f"   • 方向特定准确率 - 观望: {hold_accuracy:.1f}%, 上涨: {up_accuracy:.1f}%, 下跌: {down_accuracy:.1f}%")
        print()
        
        # File Locations
        print("📁 学习数据文件:")
        print(f"   预测结果: {self.prediction_outcomes_path}")
        print(f"   性能日志: {self.performance_log_path}")
        print(f"   策略配置: {self.strategy_config_path}")
        print()
        
        print("="*100)
        print("💡 提示: 查看这些文件可了解详细的学习过程和历史调整")
        print("="*100)
    
    def _calculate_hold_accuracy(self) -> float:
        """Calculate accuracy specifically for HOLD predictions"""
        outcomes = self.load_prediction_outcomes()
        hold_predictions = 0
        hold_correct = 0
        
        for pred_id, data in outcomes.items():
            if data['actual_outcome'] is not None:
                if data['prediction']['prediction'] == 'HOLD':
                    hold_predictions += 1
                    # HOLD is considered correct if actual movement was minimal (<1%)
                    actual_change = data['actual_outcome'].get('price_change', 0)
                    if abs(actual_change) < 0.01:  # Less than 1% movement
                        hold_correct += 1
        
        return (hold_correct / hold_predictions * 100) if hold_predictions > 0 else 0
    
    def _calculate_direction_accuracy(self, direction: str) -> float:
        """Calculate accuracy for specific direction predictions"""
        outcomes = self.load_prediction_outcomes()
        dir_predictions = 0
        dir_correct = 0
        
        for pred_id, data in outcomes.items():
            if data['actual_outcome'] is not None:
                if data['prediction']['prediction'] == direction:
                    dir_predictions += 1
                    if data['actual_outcome']['direction'] == direction:
                        dir_correct += 1
        
        return (dir_correct / dir_predictions * 100) if dir_predictions > 0 else 0

def main():
    viewer = LearningViewer()
    viewer.print_learning_dashboard()

if __name__ == "__main__":
    main()