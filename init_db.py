#!/usr/bin/env python3
"""Initialize the SQLite database for the binance-oi-spike-radar app."""

import sqlite3
import os

# Initialize the alerts database
alerts_db_path = '/root/clawd/binance-oi-spike-radar-clone/data/alerts.sqlite3'
conn = sqlite3.connect(alerts_db_path)
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

print("Database initialized successfully.")