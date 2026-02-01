#!/usr/bin/env python3
"""Test SQLite connection for the binance-oi-spike-radar app."""

import sqlite3
import os
import sys
sys.path.append('/root/clawd/binance-oi-spike-radar-clone')

from src.config import ALERT_STORE_PATH

print(f"Alert store path: {ALERT_STORE_PATH}")
print(f"Absolute path: {os.path.abspath(ALERT_STORE_PATH)}")
print(f"Directory exists: {os.path.exists(os.path.dirname(ALERT_STORE_PATH))}")
print(f"File exists before: {os.path.exists(ALERT_STORE_PATH)}")

try:
    # Test the connection like the app does
    conn = sqlite3.connect(ALERT_STORE_PATH)
    print("SQLite connection successful!")
    
    # Create table like in alert_store.py
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            ts REAL NOT NULL,
            payload TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_ts ON alerts(ts)")
    conn.commit()
    conn.close()
    
    print("Table creation successful!")
    print(f"File exists after: {os.path.exists(ALERT_STORE_PATH)}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()