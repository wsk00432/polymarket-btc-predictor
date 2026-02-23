"""
Outcomes API Routes
"""

from flask import Blueprint, jsonify, request
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

outcomes_bp = Blueprint('outcomes', __name__)

OUTCOMES_PATH = '/root/clawd/projects/polymarket-btc-predictor/prediction_outcomes.json'

@outcomes_bp.route('', methods=['GET'])
def get_outcomes():
    """
    Get prediction outcomes
    
    Query params:
    - limit: Max number of outcomes (default: 100)
    - evaluated: Filter by evaluated status (true/false)
    - correct: Filter by correctness (true/false)
    """
    limit = request.args.get('limit', 100, type=int)
    evaluated = request.args.get('evaluated')
    correct = request.args.get('correct')
    
    try:
        if not os.path.exists(OUTCOMES_PATH):
            return jsonify({'outcomes': [], 'count': 0})
        
        with open(OUTCOMES_PATH, 'r') as f:
            all_outcomes = json.load(f)
        
        outcomes = []
        for pred_id, data in all_outcomes.items():
            # Filter by evaluated status
            if evaluated is not None:
                is_evaluated = bool(data.get('actual_outcome'))
                if evaluated == 'true' and not is_evaluated:
                    continue
                if evaluated == 'false' and is_evaluated:
                    continue
            
            # Filter by correctness
            if correct is not None and data.get('actual_outcome'):
                is_correct = data['prediction']['prediction'] == data['actual_outcome']['direction']
                if correct == 'true' and not is_correct:
                    continue
                if correct == 'false' and is_correct:
                    continue
            
            outcomes.append({
                'id': pred_id,
                **data
            })
            
            if len(outcomes) >= limit:
                break
        
        return jsonify({
            'outcomes': outcomes,
            'count': len(outcomes),
            'total': len(all_outcomes)
        })
    
    except Exception as e:
        logger.error(f"Error getting outcomes: {e}")
        return jsonify({'error': str(e)}), 500

@outcomes_bp.route('/stats', methods=['GET'])
def get_outcome_stats():
    """Get outcome statistics"""
    try:
        if not os.path.exists(OUTCOMES_PATH):
            return jsonify({
                'total': 0,
                'evaluated': 0,
                'correct': 0,
                'accuracy': 0.0
            })
        
        with open(OUTCOMES_PATH, 'r') as f:
            all_outcomes = json.load(f)
        
        total = len(all_outcomes)
        evaluated = 0
        correct = 0
        by_direction = {'UP': {'total': 0, 'correct': 0}, 'DOWN': {'total': 0, 'correct': 0}}
        
        for data in all_outcomes.values():
            if data.get('actual_outcome'):
                evaluated += 1
                predicted = data['prediction']['prediction']
                actual = data['actual_outcome']['direction']
                
                if predicted == actual:
                    correct += 1
                    if predicted in by_direction:
                        by_direction[predicted]['correct'] += 1
                
                if predicted in by_direction:
                    by_direction[predicted]['total'] += 1
        
        accuracy = (correct / evaluated * 100) if evaluated > 0 else 0
        
        # Calculate direction-specific accuracy
        for direction in by_direction:
            if by_direction[direction]['total'] > 0:
                by_direction[direction]['accuracy'] = (
                    by_direction[direction]['correct'] / by_direction[direction]['total'] * 100
                )
            else:
                by_direction[direction]['accuracy'] = 0
        
        return jsonify({
            'total': total,
            'evaluated': evaluated,
            'correct': correct,
            'accuracy': accuracy,
            'by_direction': by_direction
        })
    
    except Exception as e:
        logger.error(f"Error getting outcome stats: {e}")
        return jsonify({'error': str(e)}), 500

@outcomes_bp.route('/<prediction_id>', methods=['GET'])
def get_outcome(prediction_id):
    """Get a specific outcome by prediction ID"""
    try:
        if not os.path.exists(OUTCOMES_PATH):
            return jsonify({'error': 'Outcomes file not found'}), 404
        
        with open(OUTCOMES_PATH, 'r') as f:
            all_outcomes = json.load(f)
        
        if prediction_id not in all_outcomes:
            return jsonify({'error': 'Outcome not found'}), 404
        
        return jsonify(all_outcomes[prediction_id])
    
    except Exception as e:
        logger.error(f"Error getting outcome {prediction_id}: {e}")
        return jsonify({'error': str(e)}), 500
