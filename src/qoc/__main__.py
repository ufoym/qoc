#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QOC package main entry file
Supports python -m qoc invocation
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from .cli import main

if __name__ == '__main__':
    main() 