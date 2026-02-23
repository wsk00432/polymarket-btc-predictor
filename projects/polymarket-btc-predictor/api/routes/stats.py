"""
Statistics API Routes
"""

from flask import Blueprint, jsonify
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

stats_bp = Blueprint('stats', __name__)

PREDICTIONS_DIR = '/root/clawd/projects/polymarket-btc-predictor/predictions'
OUTCOMES_PATH = '/root/clawd/projects/polymarket-btc-predictor/prediction_outcomes.json'

@stats_bp.route('', methods=['GET'])
def get_all_stats():
    """Get comprehensive statistics"""
    try:
        return jsonify({
            'overview': get_overview_stats(),
            'accuracy': get_accuracy_stats(),
            'predictions': get_prediction_stats(),
            'market': get_market_stats()
        })
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@stats_bp.route('/overview', methods=['GET'])
def get_overview():
    """Get overview statistics"""
    try:
        return jsonify(get_overview_stats())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@stats_bp.route('/accuracy', methods=['GET'])
def get_accuracy():
    """Get accuracy statistics"""
    try:
        return jsonify(get_accuracy_stats())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_overview_stats():
    """Calculate overview statistics"""
    predictions_count = 0
    outcomes_count = 0
    digests_count = 0
    
    # Count predictions
    if os.path.exists(PREDICTIONS_DIR):
        predictions_count = len([f for f in os.listdir(PREDICTIONS_DIR) if f.startswith('btc_pred_')])
    
    # Count outcomes
    if os.path.exists(OUTCOMES_PATH):
        with open(OUTCOMES_PATH, 'r') as f:
            outcomes_data = json.load(f)
            outcomes_count = len(outcomes_data)
    
    # Count digests
    digests_dir = '/root/clawd/projects/polymarket-btc-predictor/digests'
    if os.path.exists(digests_dir):
        digests_count = len([f for f in os.listdir(digests_dir) if f.endswith('.json')])
    
    return {
        'total_predictions': predictions_count,
        'total_outcomes': outcomes_count,
        'total_digests': digests_count,
        'system_uptime': 'N/A',  # Would need process tracking
        'last_updated': datetime.now().isoformat()
    }

def get_accuracy_stats():
    """Calculate accuracy statistics"""
    if not os.path.exists(OUTCOMES_PATH):
        return {
            'total_evaluated': 0,
            'correct': 0,
            'accuracy': 0.0,
            'by_direction': {}
        }
    
    with open(OUTCOMES_PATH, 'r') as f:
        all_outcomes = json.load(f)
    
    total_evaluated = 0
    correct = 0
    by_direction = {'UP': {'total': 0, 'correct': 0}, 'DOWN': {'total': 0, 'correct': 0}}
    
    for data in all_outcomes.values():
        if data.get('actual_outcome'):
            total_evaluated += 1
            predicted = data['prediction']['prediction']
            actual = data['actual_outcome']['direction']
            
            if predicted == actual:
                correct += 1
                if predicted in by_direction:
                    by_direction[predicted]['correct'] += 1
            
            if predicted in by_direction:
                by_direction[predicted]['total'] += 1
    
    accuracy = (correct / total_evaluated * 100) if total_evaluated > 0 else 0
    
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

def get_prediction_stats():
    """Calculate prediction statistics"""
    if not os.path.exists(PREDICTIONS_DIR):
        return {
            'total': 0,
            'by_direction': {},
            'avg_confidence': 0.0
        }
    
    predictions = []
    for filename in os.listdir(PREDICTIONS_DIR):
        if filename.startswith('btc_pred_'):
            filepath = os.path.join(PREDICTIONS_DIR, filename)
            try:
                with open(filepath, 'r') as f:
                    predictions.append(json.load(f))
            except:
                continue
    
    if not predictions:
        return {
            'total': 0,
            'by_direction': {},
            'avg_confidence': 0.0
        }
    
    # By direction
    by_direction = {'UP': 0, 'DOWN': 0, 'HOLD': 0}
    confidences = []
    
    for pred in predictions:
        direction = pred.get('prediction', 'HOLD')
        if direction in by_direction:
            by_direction[direction] += 1
        
        confidences.append(pred.get('confidence', 0))
    
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    return {
        'total': len(predictions),
        'by_direction': by_direction,
        'avg_confidence': avg_confidence
    }

def get_market_stats():
    """Get market statistics from recent predictions"""
    if not os.path.exists(PREDICTIONS_DIR):
        return {
            'current_price': 0,
            'price_change_24h': 0,
            'high_24h': 0,
            'low_24h': 0
        }
    
    prices = []
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    for filename in os.listdir(PREDICTIONS_DIR):
        if filename.startswith('btc_pred_'):
            filepath = os.path.join(PREDICTIONS_DIR, filename)
            try:
                with open(filepath, 'r') as f:
                    pred = json.load(f)
                
                pred_time = datetime.fromisoformat(pred['timestamp'])
                if pred_time >= cutoff_time:
                    price = pred.get('current_price', 0)
                    if price > 0:
                        prices.append(price)
            except:
                continue
    
    if not prices:
        return {
            'current_price': 0,
            'price_change_24h': 0,
            'high_24h': 0,
            'low_24h': 0
        }
    
    current_price = prices[0]
    old_price = prices[-1] if len(prices) > 1 else prices[0]
    price_change = ((current_price - old_price) / old_price * 100) if old_price > 0 else 0
    
    return {
        'current_price': current_price,
        'price_change_24h': price_change,
        'high_24h': max(prices),
        'low_24h': min(prices),
        'volatility': (max(prices) - min(prices)) / sum(prices) * len(prices) if prices else 0
    }
