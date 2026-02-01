#!/usr/bin/env python3
"""
Final startup script for binance-oi-spike-radar that properly fixes the path issue.
"""

import os
import sys

# Ensure we're in the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, 'binance-oi-spike-radar-clone')
os.chdir(project_dir)

# Add the project root to Python path
sys.path.insert(0, project_dir)

# Force reimport of config with correct paths
import importlib
if 'src.config' in sys.modules:
    importlib.reload(sys.modules['src.config'])

# Now import the app state and update its configuration
from src.state import app_state
from src.config import default_config

# Ensure the app_state uses the correct configuration
fresh_config = default_config()
app_state.config = fresh_config.copy()

print("Starting binance-oi-spike-radar with corrected paths...")
print(f"ALERT_STORE_PATH: {app_state.config.get('ALERT_STORE_PATH')}")

import uvicorn
uvicorn.run("src.webapp:app", host="0.0.0.0", port=8000, reload=False)