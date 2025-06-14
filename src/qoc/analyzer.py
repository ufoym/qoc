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
            print("⚠️  Warning: Tree-sitter not available. Install tree-sitter packages.")
            return
            
        language_configs = {
            'python': tspython,
            'javascript': tsjavascript,
            'java': tsjava,
            'cpp': tscpp
        }
        
        for lang_name, lang_module in language_configs.items():
            try:
                # Create language object
                language = Language(lang_module.language())
                self.languages[lang_name] = language
                
                # Create parser
                parser = Parser(language=language)
                self.parsers[lang_name] = parser
                
            except Exception as e:
                print(f"⚠️  Warning: Cannot initialize {lang_name} parser: {e}")
    
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
        except Exception:
            return 0, 0
    
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
    
    def analyze_file(self, filepath: str) -> Optional[QOCResult]:
        """Analyze QOC (Quanta of Code) of a single file"""
        if not os.path.exists(filepath):
            print(f"❌ Error: File does not exist {filepath}")
            return None
        
        # Determine programming language
        language = self._get_language_from_extension(filepath)
        if not language:
            print(f"⚠️  Warning: Unsupported file type {filepath}")
            return None
        
        if language not in self.parsers:
            print(f"⚠️  Warning: {language} parser not initialized")
            return None
        
        # Read file content
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                source_code = f.read()
        except Exception as e:
            print(f"❌ Error: Cannot read file {filepath}: {e}")
            return None
        
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
            print(f"❌ Error analyzing file {filepath}: {e}")
            return None
    
    def analyze_directory(self, directory: str, recursive: bool = False) -> List[QOCResult]:
        """Analyze all supported files in directory"""
        results = []
        
        directory_path = Path(directory)
        if not directory_path.exists():
            print(f"❌ Error: Directory does not exist {directory}")
            return results
        
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
                    result = self.analyze_file(str(file_path))
                    if result:
                        results.append(result)
        
        return results
    
    def print_result(self, result: QOCResult, detailed: bool = False):
        """Print analysis result"""
        print(f"\n📄 File: {result.filepath}")
        print(f"🔤 Language: {result.language}")
        print(f"📏 LOC: {result.loc}")
        print(f"📏 SLOC: {result.sloc}")
        
        qoc_sloc_ratio = result.total_qoc / result.sloc if result.sloc > 0 else 0
        
        print(f"⚡ Quanta of Code (QOC): {result.total_qoc:.1f}")
        print(f"🌳 AST Nodes: {result.ast_nodes}")
        print(f"📊 Efficiency Ratio (QOC/SLOC): {qoc_sloc_ratio:.2f}")
        
        if detailed and result.node_stats:
            print("\n🔍 Detailed AST Node Analysis:")
            print("=" * 80)
            print(f"{'Node Type':<30} {'Count':<8} {'Weight':<8} {'Total Weight':<12} {'Percentage':<10}")
            print("=" * 80)
            
            # Sort nodes by total weight (descending)
            sorted_nodes = sorted(result.node_stats.items(), 
                                key=lambda x: x[1].total_weight, reverse=True)
            
            for node_type, node_info in sorted_nodes:
                percentage = (node_info.total_weight / result.total_qoc * 100) if result.total_qoc > 0 else 0
                print(f"{node_type:<30} {node_info.count:<8} {node_info.weight:<8.1f} {node_info.total_weight:<12.1f} {percentage:<10.1f}%")
    
    def print_summary(self, results: List[QOCResult]):
        """Print analysis summary"""
        if not results:
            print("⚠️  No analysis results to display")
            return
        
        total_files = len(results)
        total_qoc = sum(r.total_qoc for r in results)
        total_sloc = sum(r.sloc for r in results)  # Source Lines of Code
        total_loc = sum(r.loc for r in results)  # Lines of Code
        total_ast_nodes = sum(r.ast_nodes for r in results)
        
        # Language statistics
        language_stats = {}
        for result in results:
            lang = result.language
            if lang not in language_stats:
                language_stats[lang] = {'count': 0, 'qoc': 0, 'sloc': 0, 'loc': 0}
            language_stats[lang]['count'] += 1
            language_stats[lang]['qoc'] += result.total_qoc
            language_stats[lang]['sloc'] += result.sloc
            language_stats[lang]['loc'] += result.loc
        
        # Display summary
        print("=" * 80)
        print("📊 QOC Analysis Summary")
        print("=" * 80)
        print(f"Total Files: {total_files:,}")
        print(f"Total QOC: {total_qoc:,.1f}")
        print(f"Total LOC: {total_loc:,}")
        print(f"Total SLOC: {total_sloc:,}")
        print(f"Total AST Nodes: {total_ast_nodes:,}")
        print(f"Average Efficiency Ratio: {total_qoc/total_sloc:.2f}")
        print("=" * 80)
        
        # Language distribution
        if len(language_stats) > 1:
            print("\n🌍 Language Distribution:")
            print("=" * 80)
            print(f"{'Language':<12} {'Files':<8} {'QOC':<12} {'LOC':<8} {'SLOC':<8} {'Percentage':<10}")
            print("=" * 80)
            
            for lang, stats in sorted(language_stats.items(), key=lambda x: x[1]['count'], reverse=True):
                percentage = (stats['count'] / total_files) * 100
                print(f"{lang.capitalize():<12} {stats['count']:<8} {stats['qoc']:<12.1f} {stats['loc']:<8} {stats['sloc']:<8} {percentage:<10.1f}%")
            print("=" * 80) 