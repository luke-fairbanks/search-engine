#!/usr/bin/env python3
"""
Load environment variables from .env file
"""
import os
from pathlib import Path

def load_env():
    """Load environment variables from .env file if it exists"""
    env_file = Path(__file__).parent / '.env'

    if env_file.exists():
        print(f"Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # Only set if not already in environment
                        if key not in os.environ:
                            os.environ[key] = value
                            print(f"  Set {key}")
    else:
        print(f"No .env file found (using system environment variables)")

if __name__ == '__main__':
    load_env()
