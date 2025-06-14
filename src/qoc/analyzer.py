#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QOC - Quanta of Code Analyzer
AST-based code contribution analysis tool
Supports multiple programming languages: Python, JavaScript, Java, C++
Fully based on Tree-sitter AST parsing
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, TYPE_CHECKING

from .models import NodeInfo, QOCResult

# Tree-sitter imports
try:
    import tree_sitter_python as tspython
    import tree_sitter_javascript as tsjavascript  
    import tree_sitter_java as tsjava
    import tree_sitter_cpp as tscpp
    from tree_sitter import Parser, Language, Node
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    # For type checking when tree-sitter is not available
    if TYPE_CHECKING:
        from tree_sitter import Node


class QOCAnalyzer:
    """QOC (Quanta of Code) Analyzer"""
    
    def __init__(self, config_path: str = None):
        # Get configuration file path
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config.json"
        
        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Initialize language parsers
        self.languages = {}
        self.parsers = {}
        
        # Initialize supported languages
        self._init_languages()
    
    def _init_languages(self):
        """Initialize Tree-sitter language parsers"""
        if not TREE_SITTER_AVAILABLE:
            raise ImportError("Tree-sitter not available. Install tree-sitter packages.")
            
        language_configs = {
            'python': tspython,
            'javascript': tsjavascript,
            'java': tsjava,
            'cpp': tscpp
        }
        
        failed_languages = []
        for lang_name, lang_module in language_configs.items():
            try:
                # Create language object
                language = Language(lang_module.language())
                self.languages[lang_name] = language
                
                # Create parser
                parser = Parser(language=language)
                self.parsers[lang_name] = parser
                
            except Exception as e:
                failed_languages.append((lang_name, str(e)))
        
        # If some languages failed to initialize, we can still continue with the others
        # but raise a warning through the caller
        if failed_languages:
            self.failed_languages = failed_languages
        else:
            self.failed_languages = []
    
    def get_failed_languages(self) -> List[Tuple[str, str]]:
        """获取初始化失败的语言列表"""
        return getattr(self, 'failed_languages', [])
    
    def _get_language_from_extension(self, filepath: str) -> Optional[str]:
        """Determine programming language from file extension"""
        ext = Path(filepath).suffix.lower()
        
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'javascript',  # TypeScript uses JavaScript parser
            '.tsx': 'javascript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c++': 'cpp',
            '.hpp': 'cpp',
            '.h': 'cpp',
            '.hxx': 'cpp'
        }
        
        return extension_map.get(ext)
    
    def _get_file_lines(self, filepath: str) -> tuple[int, int]:
        """Calculate file lines - returns (loc, sloc)
        
        Returns:
            tuple: (LOC - lines including empty lines and comments, SLOC - source lines excluding empty lines)
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                loc = len(lines)  # Lines of Code (including empty lines and comments)
                # Only count non-empty lines for SLOC
                non_empty_lines = [line for line in lines if line.strip()]
                sloc = len(non_empty_lines)  # Source Lines of Code
                return loc, sloc
        except Exception as e:
            raise IOError(f"Cannot read file lines from {filepath}: {e}")
    
    def _traverse_ast(self, node, language: str, node_stats: Dict[str, NodeInfo]) -> None:
        """Recursively traverse AST nodes and calculate weights"""
        node_type = node.type
        
        # Get weight configuration for this language
        weights = self.config['languages'].get(language, {}).get('node_weights', {})
        weight = weights.get(node_type, 1.0)  # Default weight is 1.0
        
        if weight > 0:  # Only record nodes with weight
            if node_type in node_stats:
                node_stats[node_type].count += 1
                node_stats[node_type].total_weight += weight
            else:
                node_stats[node_type] = NodeInfo(
                    node_type=node_type,
                    weight=weight,
                    count=1
                )
        
        # Recursively process child nodes
        for child in node.children:
            self._traverse_ast(child, language, node_stats)
    
    def analyze_file(self, filepath: str) -> QOCResult:
        """Analyze QOC (Quanta of Code) of a single file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File does not exist: {filepath}")
        
        # Determine programming language
        language = self._get_language_from_extension(filepath)
        if not language:
            raise ValueError(f"Unsupported file type: {filepath}")
        
        if language not in self.parsers:
            raise RuntimeError(f"{language} parser not initialized")
        
        # Read file content
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                source_code = f.read()
        except Exception as e:
            raise IOError(f"Cannot read file {filepath}: {e}")
        
        # Get lines of code
        loc, sloc = self._get_file_lines(filepath)
        
        if not source_code.strip():
            # Handle empty files
            return QOCResult(
                filepath=filepath,
                language=language,
                total_qoc=0,  # Empty file has no QOC
                ast_nodes=0,
                sloc=sloc,  # Source Lines of Code
                loc=loc,  # Lines of Code
                node_stats={}
            )
        
        try:
            # Parse source code
            tree = self.parsers[language].parse(bytes(source_code, 'utf8'))
            
            if tree.root_node.has_error:
                # Handle syntax errors, return simple estimation based on line count
                return QOCResult(
                    filepath=filepath,
                    language=language,
                    total_qoc=sloc,
                    ast_nodes=0,
                    sloc=sloc,  # Source Lines of Code  
                    loc=loc,  # Lines of Code
                    node_stats={}
                )
            
            # Traverse AST and collect node information
            node_stats = {}
            self._traverse_ast(tree.root_node, language, node_stats)
            
            # Calculate total QOC
            total_qoc = sum(node_info.total_weight for node_info in node_stats.values())
            total_ast_nodes = sum(node_info.count for node_info in node_stats.values())
            
            return QOCResult(
                filepath=filepath,
                language=language,
                total_qoc=total_qoc,
                ast_nodes=total_ast_nodes,
                sloc=sloc,  # Source Lines of Code
                loc=loc,  # Lines of Code
                node_stats=node_stats
            )
            
        except Exception as e:
            raise RuntimeError(f"Error analyzing file {filepath}: {e}")
    
    def analyze_directory(self, directory: str, recursive: bool = False) -> List[QOCResult]:
        """Analyze all supported files in directory"""
        results = []
        
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory does not exist: {directory}")
        
        # Get all files
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in directory_path.glob(pattern):
            if file_path.is_file():
                # Check if file is supported
                language = self._get_language_from_extension(str(file_path))
                if language and language in self.parsers:
                    try:
                        result = self.analyze_file(str(file_path))
                        results.append(result)
                    except (ValueError, RuntimeError):
                        # Skip unsupported files silently
                        continue
                    except Exception:
                        # Skip files that can't be analyzed
                        continue
        
        return results 