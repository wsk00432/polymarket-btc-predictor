"""
Digests API Routes
"""

from flask import Blueprint, jsonify, request, send_file
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

digests_bp = Blueprint('digests', __name__)

DIGESTS_DIR = '/root/clawd/projects/polymarket-btc-predictor/digests'

@digests_bp.route('', methods=['GET'])
def get_digests():
    """
    Get list of digests
    
    Query params:
    - type: Filter by digest type (4h/daily/weekly/monthly)
    - limit: Max number of digests (default: 20)
    """
    digest_type = request.args.get('type')
    limit = request.args.get('limit', 20, type=int)
    
    try:
        if not os.path.exists(DIGESTS_DIR):
            return jsonify({'digests': [], 'count': 0})
        
        digests = []
        
        for filename in sorted(os.listdir(DIGESTS_DIR), reverse=True):
            if not filename.endswith('.json'):
                continue
            
            # Filter by type
            if digest_type and not filename.startswith(f'{digest_type}_'):
                continue
            
            filepath = os.path.join(DIGESTS_DIR, filename)
            try:
                with open(filepath, 'r') as f:
                    digest = json.load(f)
                digests.append(digest)
                
                if len(digests) >= limit:
                    break
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
                continue
        
        return jsonify({
            'digests': digests,
            'count': len(digests)
        })
    
    except Exception as e:
        logger.error(f"Error getting digests: {e}")
        return jsonify({'error': str(e)}), 500

@digests_bp.route('/latest', methods=['GET'])
def get_latest_digest():
    """Get the most recent digest"""
    try:
        if not os.path.exists(DIGESTS_DIR):
            return jsonify({'error': 'No digests found'}), 404
        
        latest = None
        latest_time = None
        
        for filename in os.listdir(DIGESTS_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(DIGESTS_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        digest = json.load(f)
                    
                    gen_time = datetime.fromisoformat(digest['generated_at'])
                    if latest_time is None or gen_time > latest_time:
                        latest = digest
                        latest_time = gen_time
                except Exception as e:
                    logger.error(f"Error loading {filename}: {e}")
                    continue
        
        if not latest:
            return jsonify({'error': 'No digests found'}), 404
        
        return jsonify(latest)
    
    except Exception as e:
        logger.error(f"Error getting latest digest: {e}")
        return jsonify({'error': str(e)}), 500

@digests_bp.route('/generate', methods=['POST'])
def generate_digest():
    """Generate a new digest"""
    try:
        from digest_generator import DigestGenerator
        
        data = request.get_json() or {}
        digest_type = data.get('type', '4h')
        
        generator = DigestGenerator()
        filepath = generator.generate_and_save(digest_type)
        
        with open(filepath, 'r') as f:
            digest = json.load(f)
        
        return jsonify({
            'success': True,
            'digest': digest,
            'filepath': filepath
        }), 201
    
    except Exception as e:
        logger.error(f"Error generating digest: {e}")
        return jsonify({'error': str(e)}), 500

@digests_bp.route('/<digest_type>', methods=['GET'])
def get_digest_by_type(digest_type):
    """Get the most recent digest of a specific type"""
    try:
        if not os.path.exists(DIGESTS_DIR):
            return jsonify({'error': 'No digests found'}), 404
        
        latest = None
        latest_time = None
        
        for filename in os.listdir(DIGESTS_DIR):
            if filename.startswith(f'{digest_type}_') and filename.endswith('.json'):
                filepath = os.path.join(DIGESTS_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        digest = json.load(f)
                    
                    gen_time = datetime.fromisoformat(digest['generated_at'])
                    if latest_time is None or gen_time > latest_time:
                        latest = digest
                        latest_time = gen_time
                except Exception as e:
                    logger.error(f"Error loading {filename}: {e}")
                    continue
        
        if not latest:
            return jsonify({'error': f'No {digest_type} digests found'}), 404
        
        return jsonify(latest)
    
    except Exception as e:
        logger.error(f"Error getting {digest_type} digest: {e}")
        return jsonify({'error': str(e)}), 500
