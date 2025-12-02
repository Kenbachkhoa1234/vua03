#!/usr/bin/env python
import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from BE.app import app

# Vercel requires the app to be callable
if __name__ == "__main__":
    app.run()
