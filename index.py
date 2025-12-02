#!/usr/bin/env python
import os
import sys

# Add the BE directory to the path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'BE'))

from app import app

# Vercel requires the app to be callable
if __name__ == "__main__":
    app.run()

