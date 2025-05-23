#!/bin/env python3
from report import models 
from report import *
import os

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode, host='localhost', port=5000)
