#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QOC - Quanta of Code Tool

AST-based code contribution measurement tool
Main entry point for the QOC application

Usage:
    python qoc.py <command> [options]
    
For detailed help:
    python -m qoc --help
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from qoc.cli import main

if __name__ == '__main__':
    main() 