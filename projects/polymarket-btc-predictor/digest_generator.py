#!/usr/bin/env python3
"""
Digest Generator for BTC Predictor
Generates periodic summaries (4H/Daily/Weekly/Monthly) of predictions and performance
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DigestGenerator:
    """
    Generates periodic digests of BTC predictions and system performance
    """
    
    def __init__(self, predictions_dir: str = "/root/clawd/projects/polymarket-btc-predictor/predictions"):
        self.predictions_dir = predictions_dir
        self.output_dir = "/root/clawd/projects/polymarket-btc-predictor/digests"
        self.templates_dir = "/root/clawd/projects/polymarket-btc-predictor/digest_templates"
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("Digest Generator initialized")
    
    def load_predictions(self, hours: int = 24) -> List[Dict]:
        """
        Load predictions from the last N hours
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            List of prediction dictionaries
        """
        predictions = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        try:
            # Get all prediction files
            pred_files = Path(self.predictions_dir).glob("btc_pred_*.json")
            
            for pred_file in pred_files:
                try:
                    with open(pred_file, 'r') as f:
                        pred_data = json.load(f)
                    
                    # Parse timestamp
                    pred_time = datetime.fromisoformat(pred_data['timestamp'].replace('Z', '+00:00'))
                    
                    # Filter by time
                    if pred_time.replace(tzinfo=None) >= cutoff_time:
                        predictions.append(pred_data)
                except Exception as e:
                    logger.error(f"Error loading {pred_file}: {e}")
                    continue
            
            # Sort by timestamp
            predictions.sort(key=lambda x: x['timestamp'], reverse=True)
            logger.info(f"Loaded {len(predictions)} predictions from last {hours} hours")
            
        except Exception as e:
            logger.error(f"Error loading predictions: {e}")
        
        return predictions
    
    def calculate_statistics(self, predictions: List[Dict]) -> Dict:
        """
        Calculate statistics from predictions
        
        Args:
            predictions: List of prediction dictionaries
        
        Returns:
            Dictionary with statistical metrics
        """
        if not predictions:
            return {
                'total_predictions': 0,
                'avg_confidence': 0.0,
                'prediction_distribution': {'UP': 0, 'DOWN': 0, 'HOLD': 0},
                'avg_price': 0.0,
                'price_change': 0.0,
                'high_price': 0.0,
                'low_price': 0.0
            }
        
        # Calculate metrics
        total = len(predictions)
        confidences = [p.get('confidence', 0) for p in predictions]
        prices = [p.get('current_price', 0) for p in predictions]
        
        # Prediction distribution
        distribution = {'UP': 0, 'DOWN': 0, 'HOLD': 0}
        for pred in predictions:
            direction = pred.get('prediction', 'HOLD')
            if direction in distribution:
                distribution[direction] += 1
        
        # Price statistics
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        avg_price = sum(prices) / len(prices) if prices else 0
        high_price = max(prices) if prices else 0
        low_price = min(prices) if prices else 0
        price_change = ((prices[0] - prices[-1]) / prices[-1] * 100) if len(prices) > 1 else 0
        
        return {
            'total_predictions': total,
            'avg_confidence': avg_confidence,
            'prediction_distribution': distribution,
            'avg_price': avg_price,
            'high_price': high_price,
            'low_price': low_price,
            'price_change': price_change,
            'start_price': prices[-1] if prices else 0,
            'end_price': prices[0] if prices else 0
        }
    
    def load_outcomes(self) -> Dict:
        """Load prediction outcomes for accuracy calculation"""
        outcomes_path = "/root/clawd/projects/polymarket-btc-predictor/prediction_outcomes.json"
        
        try:
            if os.path.exists(outcomes_path):
                with open(outcomes_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading outcomes: {e}")
        
        return {}
    
    def calculate_accuracy(self, outcomes: Dict, hours: int = 24) -> Dict:
        """
        Calculate accuracy metrics from outcomes
        
        Args:
            outcomes: Dictionary of prediction outcomes
            hours: Time window in hours
        
        Returns:
            Dictionary with accuracy metrics
        """
        if not outcomes:
            return {
                'total_evaluated': 0,
                'correct': 0,
                'accuracy': 0.0,
                'by_direction': {}
            }
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        total_evaluated = 0
        correct = 0
        by_direction = {'UP': {'total': 0, 'correct': 0}, 
                       'DOWN': {'total': 0, 'correct': 0}, 
                       'HOLD': {'total': 0, 'correct': 0}}
        
        for pred_id, data in outcomes.items():
            try:
                # Check if outcome exists
                if not data.get('actual_outcome'):
                    continue
                
                # Parse timestamp
                pred_time = datetime.fromisoformat(pred_id.replace('Z', '+00:00'))
                if pred_time.replace(tzinfo=None) < cutoff_time:
                    continue
                
                total_evaluated += 1
                
                # Check accuracy
                predicted = data['prediction']['prediction']
                actual = data['actual_outcome']['direction']
                
                if predicted == actual:
                    correct += 1
                    by_direction[predicted]['correct'] += 1
                
                by_direction[predicted]['total'] += 1
                
            except Exception as e:
                logger.error(f"Error processing outcome {pred_id}: {e}")
                continue
        
        # Calculate accuracy
        accuracy = (correct / total_evaluated * 100) if total_evaluated > 0 else 0
        
        # Calculate by-direction accuracy
        for direction in by_direction:
            if by_direction[direction]['total'] > 0:
                by_direction[direction]['accuracy'] = (
                    by_direction[direction]['correct'] / by_direction[direction]['total'] * 100
                )
            else:
                by_direction[direction]['accuracy'] = 0
        
        return {
            'total_evaluated': total_evaluated,
            'correct': correct,
            'accuracy': accuracy,
            'by_direction': by_direction
        }
    
    def generate_digest(self, digest_type: str = '4h') -> Dict:
        """
        Generate a digest of specified type
        
        Args:
            digest_type: Type of digest (4h, daily, weekly, monthly)
        
        Returns:
            Dictionary containing digest data
        """
        # Determine time window
        time_windows = {
            '4h': 4,
            'daily': 24,
            'weekly': 168,  # 7 days
            'monthly': 720  # 30 days
        }
        
        hours = time_windows.get(digest_type, 24)
        
        logger.info(f"Generating {digest_type} digest (last {hours} hours)...")
        
        # Load data
        predictions = self.load_predictions(hours)
        outcomes = self.load_outcomes()
        
        # Calculate metrics
        stats = self.calculate_statistics(predictions)
        accuracy = self.calculate_accuracy(outcomes, hours)
        
        # Generate digest
        digest = {
            'type': digest_type,
            'generated_at': datetime.now().isoformat(),
            'period': {
                'start': (datetime.now() - timedelta(hours=hours)).isoformat(),
                'end': datetime.now().isoformat(),
                'hours': hours
            },
            'predictions': stats,
            'accuracy': accuracy,
            'market': {
                'btc_price_current': stats['end_price'],
                'btc_price_change': stats['price_change'],
                'volatility': (stats['high_price'] - stats['low_price']) / stats['avg_price'] * 100 if stats['avg_price'] > 0 else 0
            },
            'insights': self.generate_insights(stats, accuracy)
        }
        
        logger.info(f"Generated {digest_type} digest: {stats['total_predictions']} predictions, {accuracy['accuracy']:.1f}% accuracy")
        
        return digest
    
    def generate_insights(self, stats: Dict, accuracy: Dict) -> List[str]:
        """
        Generate human-readable insights from statistics
        
        Args:
            stats: Prediction statistics
            accuracy: Accuracy metrics
        
        Returns:
            List of insight strings
        """
        insights = []
        
        # Price movement insight
        if abs(stats['price_change']) > 2:
            direction = "上涨" if stats['price_change'] > 0 else "下跌"
            insights.append(f"BTC 价格在本周期内{direction}{abs(stats['price_change']):.2f}%")
        
        # Prediction distribution insight
        dist = stats['prediction_distribution']
        total = stats['total_predictions']
        if total > 0:
            most_common = max(dist, key=dist.get)
            percentage = dist[most_common] / total * 100
            insights.append(f"预测方向以{most_common}为主 ({percentage:.1f}%)")
        
        # Accuracy insight
        if accuracy['total_evaluated'] > 0:
            if accuracy['accuracy'] > 60:
                insights.append(f"预测准确率优秀 ({accuracy['accuracy']:.1f}%)")
            elif accuracy['accuracy'] > 40:
                insights.append(f"预测准确率良好 ({accuracy['accuracy']:.1f}%)")
            else:
                insights.append(f"预测准确率有待提升 ({accuracy['accuracy']:.1f}%)")
        
        # Confidence insight
        if stats['avg_confidence'] > 0.6:
            insights.append(f"平均置信度高 ({stats['avg_confidence']:.3f})，市场信号明确")
        elif stats['avg_confidence'] < 0.3:
            insights.append(f"平均置信度低 ({stats['avg_confidence']:.3f})，市场震荡")
        
        # Volatility insight
        volatility = stats.get('high_price', 0) - stats.get('low_price', 0)
        if volatility > 0 and stats['avg_price'] > 0:
            vol_pct = volatility / stats['avg_price'] * 100
            if vol_pct > 5:
                insights.append(f"市场波动剧烈 ({vol_pct:.2f}%)")
            elif vol_pct < 2:
                insights.append(f"市场相对平稳 ({vol_pct:.2f}%)")
        
        return insights
    
    def save_digest(self, digest: Dict) -> str:
        """
        Save digest to file
        
        Args:
            digest: Digest dictionary
        
        Returns:
            Path to saved file
        """
        digest_type = digest['type']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{digest_type}_digest_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(digest, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved digest to {filepath}")
        return filepath
    
    def generate_and_save(self, digest_type: str = '4h') -> str:
        """
        Generate and save a digest
        
        Args:
            digest_type: Type of digest
        
        Returns:
            Path to saved file
        """
        digest = self.generate_digest(digest_type)
        filepath = self.save_digest(digest)
        return filepath
    
    def generate_all_digests(self) -> Dict[str, str]:
        """
        Generate all digest types
        
        Returns:
            Dictionary mapping digest type to file path
        """
        results = {}
        
        for digest_type in ['4h', 'daily', 'weekly', 'monthly']:
            try:
                filepath = self.generate_and_save(digest_type)
                results[digest_type] = filepath
            except Exception as e:
                logger.error(f"Error generating {digest_type} digest: {e}")
                results[digest_type] = None
        
        return results


def create_digest_generator() -> DigestGenerator:
    """Factory function to create digest generator"""
    return DigestGenerator()


if __name__ == "__main__":
    # Test the digest generator
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Digest Generator...")
    generator = DigestGenerator()
    
    # Generate 4h digest
    print("\nGenerating 4h digest...")
    digest_4h = generator.generate_and_save('4h')
    print(f"Saved to: {digest_4h}")
    
    # Generate daily digest
    print("\nGenerating daily digest...")
    digest_daily = generator.generate_and_save('daily')
    print(f"Saved to: {digest_daily}")
    
    print("\n✅ Digest generation test completed!")
