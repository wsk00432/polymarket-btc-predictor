"""
Predictions API Routes
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, timedelta
import json
import os
import logging

logger = logging.getLogger(__name__)

predictions_bp = Blueprint('predictions', __name__)

PREDICTIONS_DIR = '/root/clawd/projects/polymarket-btc-predictor/predictions'

@predictions_bp.route('', methods=['GET'])
def get_predictions():
    """
    Get list of predictions
    
    Query params:
    - limit: Max number of predictions (default: 50)
    - hours: Filter by last N hours (default: 24)
    - direction: Filter by direction (UP/DOWN/HOLD)
    """
    limit = request.args.get('limit', 50, type=int)
    hours = request.args.get('hours', 24, type=int)
    direction = request.args.get('direction')
    
    try:
        predictions = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Get prediction files
        if os.path.exists(PREDICTIONS_DIR):
            for filename in sorted(os.listdir(PREDICTIONS_DIR), reverse=True):
                if not filename.startswith('btc_pred_'):
                    continue
                
                filepath = os.path.join(PREDICTIONS_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        pred = json.load(f)
                    
                    # Filter by time
                    pred_time = datetime.fromisoformat(pred['timestamp'])
                    if pred_time < cutoff_time:
                        continue
                    
                    # Filter by direction
                    if direction and pred.get('prediction') != direction:
                        continue
                    
                    predictions.append(pred)
                    
                    if len(predictions) >= limit:
                        break
                except Exception as e:
                    logger.error(f"Error loading {filename}: {e}")
                    continue
        
        return jsonify({
            'predictions': predictions,
            'count': len(predictions),
            'limit': limit,
            'hours': hours
        })
    
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        return jsonify({'error': str(e)}), 500

@predictions_bp.route('/latest', methods=['GET'])
def get_latest_prediction():
    """Get the most recent prediction"""
    try:
        predictions = []
        
        if os.path.exists(PREDICTIONS_DIR):
            for filename in sorted(os.listdir(PREDICTIONS_DIR), reverse=True):
                if filename.startswith('btc_pred_'):
                    filepath = os.path.join(PREDICTIONS_DIR, filename)
                    with open(filepath, 'r') as f:
                        predictions.append(json.load(f))
                    break
        
        if not predictions:
            return jsonify({'error': 'No predictions found'}), 404
        
        return jsonify(predictions[0])
    
    except Exception as e:
        logger.error(f"Error getting latest prediction: {e}")
        return jsonify({'error': str(e)}), 500

@predictions_bp.route('/<prediction_id>', methods=['GET'])
def get_prediction(prediction_id):
    """Get a specific prediction by ID"""
    try:
        filepath = os.path.join(PREDICTIONS_DIR, f'{prediction_id}.json')
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Prediction not found'}), 404
        
        with open(filepath, 'r') as f:
            prediction = json.load(f)
        
        return jsonify(prediction)
    
    except Exception as e:
        logger.error(f"Error getting prediction {prediction_id}: {e}")
        return jsonify({'error': str(e)}), 500

@predictions_bp.route('/generate', methods=['POST'])
def generate_prediction():
    """Generate a new prediction (triggers BTC predictor)"""
    try:
        from btc_predictor import BTCPredictor
        
        predictor = BTCPredictor()
        prediction = predictor.predict_next_movement()
        
        # Save prediction
        predictor.save_prediction(prediction)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        }), 201
    
    except Exception as e:
        logger.error(f"Error generating prediction: {e}")
        return jsonify({'error': str(e)}), 500
