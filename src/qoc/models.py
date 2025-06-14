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
    lines_of_code: int
    node_stats: Optional[Dict[str, NodeInfo]] = None 