#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QOC Data Models
Defines the data structures for QOC analysis results
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class NodeInfo:
    """AST Node Information"""
    node_type: str
    weight: float
    count: int = 0
    
    def __post_init__(self):
        self.total_weight = self.weight * self.count


@dataclass
class QOCResult:
    """QOC analysis result"""
    filepath: str
    language: str
    total_qoc: float
    ast_nodes: int
    sloc: int  # Source Lines of Code (excluding empty lines and comments)
    loc: int = 0  # Lines of Code (including empty lines and comments)
    node_stats: Optional[Dict[str, NodeInfo]] = None 