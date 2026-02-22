#!/usr/bin/env python3
"""
Simple Web API for BTC Predictor
Provides HTTP endpoints to access BTC price predictions
"""

from flask import Flask, jsonify, request
import json
import os
from datetime import datetime
from btc_predictor import BTCPredictor
from prediction_manager import PredictionManager

app = Flask(__name__)
predictor = BTCPredictor()
manager = PredictionManager()

@app.route('/')
def home():
    return jsonify({
        'service': 'BTC Price Movement Predictor API',
        'description': 'Predicts 15-minute Bitcoin price movements',
        'endpoints': {
            '/predict': 'Get latest BTC price movement prediction',
            '/history': 'Get prediction history',
            '/stats': 'Get accuracy statistics'
        }
    })

@app.route('/predict', methods=['GET'])
def get_prediction():
    """Get the latest BTC price movement prediction"""
    try:
        prediction = manager.make_prediction()  # Use manager for predictions
        return jsonify(prediction)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get prediction history"""
    try:
        history_dir = '/root/clawd/projects/polymarket-btc-predictor/predictions'
        if not os.path.exists(history_dir):
            return jsonify([])
        
        prediction_files = [f for f in os.listdir(history_dir) if f.startswith('btc_pred_')]
        prediction_files.sort(reverse=True)  # Most recent first
        
        # Return up to 10 most recent predictions
        recent_files = prediction_files[:10]
        history = []
        
        for filename in recent_files:
            filepath = os.path.join(history_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    history.append(data)
            except Exception as e:
                app.logger.error(f"Error reading prediction file {filename}: {e}")
        
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get prediction statistics"""
    try:
        stats = predictor.get_accuracy_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/record_outcome', methods=['POST'])
def record_outcome():
    """Record the actual outcome for a prediction"""
    try:
        data = request.get_json()
        
        required_fields = ['prediction_timestamp', 'actual_direction', 'actual_price_change', 'current_price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        success = manager.record_actual_outcome(
            data['prediction_timestamp'],
            data['actual_direction'],
            data['actual_price_change'],
            data['current_price']
        )
        
        if success:
            return jsonify({'status': 'success', 'message': 'Outcome recorded and analyzed'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to record outcome'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/performance', methods=['GET'])
def get_performance():
    """Get prediction performance metrics"""
    try:
        performance = manager.get_prediction_performance()
        return jsonify(performance)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/pending_evaluations', methods=['GET'])
def get_pending_evaluations():
    """Get predictions waiting for outcome evaluation"""
    try:
        pending = manager.get_pending_evaluations()
        return jsonify(pending)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'BTC Predictor API'
    })

if __name__ == '__main__':
    # Run the API server
    app.run(host='0.0.0.0', port=5000, debug=False)