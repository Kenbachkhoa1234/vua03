#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Get the absolute path to the BE directory
BE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BE')
sys.path.insert(0, BE_PATH)

# Import the Flask app
try:
    from app import app
except ImportError as e:
    print(f"Import Error: {e}")
    raise

# Export the app for Vercel
application = app

# For local development
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


