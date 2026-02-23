"""
Database Models for BTC Predictor
SQLite database schema and ORM-like access
"""

import sqlite3
import json
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

DATABASE_PATH = '/root/clawd/projects/polymarket-btc-predictor/database/predictions.db'

class Database:
    """Database connection and management"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                current_price REAL NOT NULL,
                indicators TEXT,
                sentiment_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create outcomes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outcomes (
                prediction_id TEXT PRIMARY KEY,
                prediction_data TEXT NOT NULL,
                actual_outcome TEXT,
                outcome_data TEXT,
                is_correct BOOLEAN,
                evaluated_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prediction_id) REFERENCES predictions(id)
            )
        ''')
        
        # Create digests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS digests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                digest_type TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                period_start TEXT,
                period_end TEXT,
                data TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create performance_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_prediction ON predictions(prediction)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_outcomes_evaluated ON outcomes(evaluated_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_digests_type ON digests(digest_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance_logs(timestamp)')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized at {self.db_path}")
    
    def save_prediction(self, prediction: Dict) -> str:
        """Save a prediction to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        pred_id = prediction['timestamp']
        
        cursor.execute('''
            INSERT OR REPLACE INTO predictions 
            (id, timestamp, prediction, confidence, current_price, indicators, sentiment_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            pred_id,
            prediction['timestamp'],
            prediction['prediction'],
            prediction['confidence'],
            prediction['current_price'],
            json.dumps(prediction.get('indicators', {})),
            json.dumps(prediction.get('sentiment_analysis'))
        ))
        
        conn.commit()
        conn.close()
        
        return pred_id
    
    def save_outcome(self, prediction_id: str, prediction_data: Dict, 
                     actual_outcome: Optional[Dict] = None, outcome_data: Optional[Dict] = None):
        """Save prediction outcome"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        is_correct = None
        if actual_outcome:
            is_correct = prediction_data['prediction'] == actual_outcome['direction']
        
        cursor.execute('''
            INSERT OR REPLACE INTO outcomes 
            (prediction_id, prediction_data, actual_outcome, outcome_data, is_correct, evaluated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            prediction_id,
            json.dumps(prediction_data),
            json.dumps(actual_outcome) if actual_outcome else None,
            json.dumps(outcome_data) if outcome_data else None,
            is_correct,
            datetime.now().isoformat() if actual_outcome else None
        ))
        
        conn.commit()
        conn.close()
    
    def get_predictions(self, limit: int = 50, hours: int = 24, 
                       direction: Optional[str] = None) -> List[Dict]:
        """Get predictions with filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        query = '''
            SELECT * FROM predictions 
            WHERE timestamp >= ?
        '''
        params = [cutoff_time]
        
        if direction:
            query += ' AND prediction = ?'
            params.append(direction)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_outcomes(self, limit: int = 100, evaluated: Optional[bool] = None) -> List[Dict]:
        """Get outcomes with filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM outcomes WHERE 1=1'
        params = []
        
        if evaluated is not None:
            if evaluated:
                query += ' AND actual_outcome IS NOT NULL'
            else:
                query += ' AND actual_outcome IS NULL'
        
        query += ' ORDER BY evaluated_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def save_digest(self, digest_type: str, data: Dict, 
                   period_start: Optional[str] = None, period_end: Optional[str] = None) -> int:
        """Save a digest"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO digests (digest_type, generated_at, period_start, period_end, data)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            digest_type,
            data.get('generated_at', datetime.now().isoformat()),
            period_start,
            period_end,
            json.dumps(data)
        ))
        
        digest_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return digest_id
    
    def log_performance(self, metric_name: str, metric_value: float, 
                       metadata: Optional[Dict] = None):
        """Log performance metric"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_logs (timestamp, metric_name, metric_value, metadata)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            metric_name,
            metric_value,
            json.dumps(metadata) if metadata else None
        ))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """Get comprehensive statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total predictions
        cursor.execute('SELECT COUNT(*) as count FROM predictions')
        stats['total_predictions'] = cursor.fetchone()['count']
        
        # Total outcomes
        cursor.execute('SELECT COUNT(*) as count FROM outcomes')
        stats['total_outcomes'] = cursor.fetchone()['count']
        
        # Evaluated outcomes
        cursor.execute('SELECT COUNT(*) as count FROM outcomes WHERE actual_outcome IS NOT NULL')
        stats['evaluated_outcomes'] = cursor.fetchone()['count']
        
        # Correct predictions
        cursor.execute('SELECT COUNT(*) as count FROM outcomes WHERE is_correct = 1')
        stats['correct_predictions'] = cursor.fetchone()['count']
        
        # Total digests
        cursor.execute('SELECT COUNT(*) as count FROM digests')
        stats['total_digests'] = cursor.fetchone()['count']
        
        conn.close()
        
        # Calculate accuracy
        if stats['evaluated_outcomes'] > 0:
            stats['accuracy'] = stats['correct_predictions'] / stats['evaluated_outcomes'] * 100
        else:
            stats['accuracy'] = 0.0
        
        return stats


# Import timedelta for Database class
from datetime import timedelta

# Singleton instance
_db_instance = None

def get_database() -> Database:
    """Get database singleton instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance

if __name__ == "__main__":
    # Test database initialization
    logging.basicConfig(level=logging.INFO)
    
    db = get_database()
    print(f"Database initialized at {db.db_path}")
    
    stats = db.get_stats()
    print(f"Stats: {stats}")
