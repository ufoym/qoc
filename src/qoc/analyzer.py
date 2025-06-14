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
from typing import Dict, Any, List, Tuple, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

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


class QOCAnalyzer:
    """QOC (Quanta of Code) Analyzer"""
    
    def __init__(self, config_path: str = None):
        self.console = Console()
        
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
                self.console.print(f"[yellow]Warning: Cannot initialize {lang_name} parser: {e}[/yellow]")
    
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
    
    def _traverse_ast(self, node: Node, language: str, node_stats: Dict[str, NodeInfo]) -> None:
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
            self.console.print(f"[red]Error: File does not exist {filepath}[/red]")
            return None
        
        # Determine programming language
        language = self._get_language_from_extension(filepath)
        if not language:
            self.console.print(f"[yellow]Warning: Unsupported file type {filepath}[/yellow]")
            return None
        
        if language not in self.parsers:
            self.console.print(f"[yellow]Warning: {language} parser not initialized[/yellow]")
            return None
        
        # Read file content
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                source_code = f.read()
        except Exception as e:
            self.console.print(f"[red]Error: Cannot read file {filepath}: {e}[/red]")
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
            self.console.print(f"[red]Error analyzing file {filepath}: {e}[/red]")
            return None
    
    def analyze_directory(self, directory: str, recursive: bool = False) -> List[QOCResult]:
        """Analyze all supported files in directory"""
        results = []
        
        directory_path = Path(directory)
        if not directory_path.exists():
            self.console.print(f"[red]Error: Directory does not exist {directory}[/red]")
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
        self.console.print(f"\n[bold green]📄 File:[/bold green] {result.filepath}")
        self.console.print(f"[bold blue]🔤 Language:[/bold blue] {result.language}")
        self.console.print(f"[bold cyan]📏 LOC:[/bold cyan] {result.loc}")
        self.console.print(f"[bold cyan]📏 SLOC:[/bold cyan] {result.sloc}")
        
        qoc_sloc_ratio = result.total_qoc / result.sloc if result.sloc > 0 else 0
        
        self.console.print(f"[bold magenta]⚡ Quanta of Code (QOC):[/bold magenta] {result.total_qoc:.1f}")
        self.console.print(f"[bold yellow]🌳 AST Nodes:[/bold yellow] {result.ast_nodes}")
        self.console.print(f"[bold red]📊 Efficiency Ratio (QOC/SLOC):[/bold red] {qoc_sloc_ratio:.2f}")
        
        if detailed and result.node_stats:
            self.console.print("\n[bold]🔍 Detailed AST Node Analysis:[/bold]")
            
            table = Table()
            table.add_column("Node Type", style="cyan")
            table.add_column("Count", style="magenta", justify="right")
            table.add_column("Weight", style="green", justify="right")
            table.add_column("Total Weight", style="yellow", justify="right")
            table.add_column("Percentage", style="blue", justify="right")
            
            # Sort nodes by total weight (descending)
            sorted_nodes = sorted(result.node_stats.items(), 
                                key=lambda x: x[1].total_weight, reverse=True)
            
            for node_type, node_info in sorted_nodes:
                percentage = (node_info.total_weight / result.total_qoc * 100) if result.total_qoc > 0 else 0
                table.add_row(
                    node_type,
                    str(node_info.count),
                    f"{node_info.weight:.1f}",
                    f"{node_info.total_weight:.1f}",
                    f"{percentage:.1f}%"
                )
            
            self.console.print(table)
    
    def print_summary(self, results: List[QOCResult]):
        """Print analysis summary"""
        if not results:
            self.console.print("[yellow]No analysis results to display[/yellow]")
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
        
        # Create summary panel
        summary_text = f"""
[bold cyan]Total Files:[/bold cyan] {total_files:,}
[bold magenta]Total QOC:[/bold magenta] {total_qoc:,.1f}
[bold blue]Total LOC:[/bold blue] {total_loc:,}
[bold green]Total SLOC:[/bold green] {total_sloc:,}
[bold yellow]Total AST Nodes:[/bold yellow] {total_ast_nodes:,}
[bold red]Average Efficiency Ratio:[/bold red] {total_qoc/total_sloc:.2f}
        """
        
        panel = Panel(
            summary_text.strip(),
            title="📊 QOC Analysis Summary",
            border_style="bright_blue"
        )
        self.console.print(panel)
        
        # Language distribution
        if len(language_stats) > 1:
            self.console.print("\n[bold]🌍 Language Distribution:[/bold]")
            
            lang_table = Table()
            lang_table.add_column("Language", style="cyan")
            lang_table.add_column("Files", style="magenta", justify="right")
            lang_table.add_column("QOC", style="yellow", justify="right")
            lang_table.add_column("LOC", style="blue", justify="right")
            lang_table.add_column("SLOC", style="green", justify="right")
            lang_table.add_column("Percentage", style="red", justify="right")
            
            for lang, stats in sorted(language_stats.items(), key=lambda x: x[1]['count'], reverse=True):
                percentage = (stats['count'] / total_files) * 100
                lang_table.add_row(
                    lang.capitalize(),
                    str(stats['count']),
                    f"{stats['qoc']:.1f}",
                    str(stats['loc']),
                    str(stats['sloc']),
                    f"{percentage:.1f}%"
                )
            
            self.console.print(lang_table) 