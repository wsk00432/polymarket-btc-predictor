#!/usr/bin/env python3
"""Fix the path issue in the binance-oi-spike-radar app."""

import os

# Define the project root
project_root = '/root/clawd/binance-oi-spike-radar-clone'

# Read the original config file
with open(f'{project_root}/src/config.py', 'r') as f:
    config_content = f.read()

# Update paths to be absolute
updated_config = config_content.replace(
    'os.path.join(os.path.dirname(__file__), "..", "data", "alerts.sqlite3")',
    '"/root/clawd/binance-oi-spike-radar-clone/data/alerts.sqlite3"'
).replace(
    'os.path.join(os.path.dirname(__file__), "..", "token_metadata.sqlite3")',
    '"/root/clawd/binance-oi-spike-radar-clone/token_metadata.sqlite3"'
).replace(
    'os.path.join(os.path.dirname(__file__), "..", "data", "config.json")',
    '"/root/clawd/binance-oi-spike-radar-clone/data/config.json"'
)

# Write the updated config
with open(f'{project_root}/src/config.py', 'w') as f:
    f.write(updated_config)

print("Fixed paths in config.py")