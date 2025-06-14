#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QOC - Quanta of Code Tool Command Line Interface
Usage: python -m qoc analyze <path> [options]
"""

import os
import json
import csv
from pathlib import Path
from typing import List, Dict, Any
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .analyzer import QOCAnalyzer
from .models import QOCResult

console = Console()

@click.group()
@click.version_option(version="1.0.0", prog_name="QOC")
def main():
    """🚀 QOC - Quanta of Code Analysis Tool
    
    Analyze real code contribution, programming style-independent contribution measurement
    
    Supported programming languages:
    - Python (.py)
    - JavaScript/TypeScript (.js, .jsx, .ts, .tsx)  
    - Java (.java)
    - C++ (.cpp, .cc, .cxx, .hpp, .h, .hxx)
    """
    pass

@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('-r', '--recursive', is_flag=True, help='Recursively analyze subdirectories')
@click.option('-d', '--detailed', is_flag=True, help='Show detailed AST node statistics')
@click.option('-o', '--output', type=click.Path(), help='Output results to file')
@click.option('--format', type=click.Choice(['console', 'json', 'csv']), default='console', help='Output format')
def analyze(path: str, recursive: bool, detailed: bool, output: str, format: str):
    """Analyze Quanta of Code (QOC)
    
    PATH: File or directory path to analyze
    
    Examples:
    qoc analyze file.py                    # Analyze single file
    qoc analyze ./src -r                   # Recursively analyze directory
    qoc analyze ./src -r -d               # Show detailed information
    qoc analyze ./src -o report.json      # Output to file
    """
    
    analyzer = QOCAnalyzer()
    
    if os.path.isfile(path):
        # Analyze single file
        result = analyzer.analyze_file(path)
        if result:
            results = [result]
        else:
            console.print("[red]Analysis failed[/red]")
            return
    else:
        # Analyze directory
        results = analyzer.analyze_directory(path, recursive)
        if not results:
            console.print("[yellow]No supported files found[/yellow]")
            return
    
    if format == 'console':
        if len(results) == 1:
            analyzer.print_result(results[0], detailed)
        else:
            analyzer.print_summary(results)
            if detailed:
                console.print("\n[bold]Detailed Results:[/bold]")
                for result in results:
                    console.print(f"\n[dim]{'='*60}[/dim]")
                    analyzer.print_result(result, detailed)
    
    elif format == 'json':
        output_data = {
            'summary': {
                'total_files': len(results),
                'total_qoc': sum(r.total_qoc for r in results),
                'total_lines': sum(r.lines_of_code for r in results),
                'total_nodes': sum(r.ast_nodes for r in results)
            },
            'files': []
        }
        
        for result in results:
            file_data = {
                'filepath': result.filepath,
                'language': result.language,
                'qoc': result.total_qoc,
                'lines_of_code': result.lines_of_code,
                'ast_nodes': result.ast_nodes
            }
            
            if detailed and result.node_stats:
                file_data['node_stats'] = {}
                for node_type, node_info in result.node_stats.items():
                    file_data['node_stats'][node_type] = {
                        'count': node_info.count,
                        'weight': node_info.weight,
                        'total_weight': node_info.total_weight
                    }
            
            output_data['files'].append(file_data)
        
        json_output = json.dumps(output_data, indent=2, ensure_ascii=False)
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            console.print(f"[green]Results saved to: {output}[/green]")
        else:
            console.print(json_output)
    
    elif format == 'csv':
        if output:
            with open(output, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Filename', 'Language', 'QOC', 'AST Nodes', 'Lines of Code', 'QOC/LOC Ratio'])
                
                for result in results:
                    ratio = result.total_qoc / result.lines_of_code if result.lines_of_code > 0 else 0
                    writer.writerow([
                        result.filepath,
                        result.language,
                        f"{result.total_qoc:.1f}",
                        result.ast_nodes,
                        result.lines_of_code,
                        f"{ratio:.2f}"
                    ])
            console.print(f"[green]CSV results saved to: {output}[/green]")
        else:
            console.print("[red]CSV format requires output file (-o)[/red]")

@main.command()
@click.argument('file1', type=click.Path(exists=True))
@click.argument('file2', type=click.Path(exists=True))
def compare(file1: str, file2: str):
    """Compare QOC differences between two files
    
    Examples:
    qoc compare old_version.py new_version.py
    """
    
    analyzer = QOCAnalyzer()
    
    result1 = analyzer.analyze_file(file1)
    result2 = analyzer.analyze_file(file2)
    
    if not result1 or not result2:
        console.print("[red]Analysis failed[/red]")
        return
    
    # Calculate differences
    qoc_diff = result2.total_qoc - result1.total_qoc
    lines_diff = result2.lines_of_code - result1.lines_of_code
    nodes_diff = result2.ast_nodes - result1.ast_nodes
    
    # Create comparison table
    table = Table(title="File Comparison Results")
    table.add_column("Metric", style="cyan")
    table.add_column("File 1", style="green")
    table.add_column("File 2", style="blue")
    table.add_column("Difference", style="yellow")
    
    table.add_row(
        "File Path",
        str(result1.filepath),
        str(result2.filepath),
        "-"
    )
    
    table.add_row(
        "Quanta of Code (QOC)",
        f"{result1.total_qoc:.1f}",
        f"{result2.total_qoc:.1f}",
        f"{qoc_diff:+.1f}"
    )
    
    table.add_row(
        "Lines of Code",
        str(result1.lines_of_code),
        str(result2.lines_of_code),
        f"{lines_diff:+d}"
    )
    
    table.add_row(
        "AST Node Count",
        str(result1.ast_nodes),
        str(result2.ast_nodes),
        f"{nodes_diff:+d}"
    )
    
    # Calculate efficiency ratios
    ratio1 = result1.total_qoc / result1.lines_of_code if result1.lines_of_code > 0 else 0
    ratio2 = result2.total_qoc / result2.lines_of_code if result2.lines_of_code > 0 else 0
    ratio_diff = ratio2 - ratio1
    
    table.add_row(
        "Efficiency Ratio",
        f"{ratio1:.2f}",
        f"{ratio2:.2f}",
        f"{ratio_diff:+.2f}"
    )
    
    console.print(table)
    
    # Analysis conclusion
    console.print("\n[bold]Analysis Conclusion:[/bold]")
    
    if qoc_diff > 0:
        conclusion = f"File 2's code complexity increased by {qoc_diff:.1f} QOC"
    elif qoc_diff < 0:
        conclusion = f"File 2's code complexity decreased by {abs(qoc_diff):.1f} QOC"
    else:
        conclusion = "Both files have similar code complexity"
    
    console.print(conclusion)

@main.command()
def demo():
    """Demonstrate QOC functionality
    
    Analyze example files in current directory to showcase QOC tool capabilities
    """
    
    console.print(
        "[bold blue]🚀 QOC Demo Mode[/bold blue]\n\n"
        "This is a demonstration mode that shows how QOC analyzes code contribution across different programming languages.\n"
    )
    
    panel = Panel(
        title="Welcome to QOC",
        border_style="bright_blue",
        renderable="QOC analyzes Abstract Syntax Trees (AST) to provide\nmore accurate code contribution assessment than traditional line counting.\n\nSupports Python, JavaScript, Java, C++, and more languages."
    )
    console.print(panel)
    
    analyzer = QOCAnalyzer()
    
    # Find example files in current directory
    current_dir = Path(".")
    example_files = []
    
    for pattern in ["*.py", "*.js", "*.java", "*.cpp"]:
        example_files.extend(current_dir.glob(pattern))
    
    if not example_files:
        console.print("\n[yellow]No example files found in current directory.[/yellow]")
        console.print("\n[bold]Try creating some example files or run:[/bold]")
        console.print("  qoc analyze <file_path>")
        console.print("  qoc analyze <directory> -r")
        console.print("  qoc compare <file1> <file2>")
        return
    
    console.print(f"\n[bold green]Found {len(example_files)} example files:[/bold green]")
    
    results = []
    for file_path in example_files[:5]:  # Analyze first 5 files
        result = analyzer.analyze_file(str(file_path))
        if result:
            results.append(result)
            console.print(f"✅ {file_path.name}")
    
    if results:
        console.print(f"\n[bold cyan]Analysis Complete![/bold cyan]")
        analyzer.print_summary(results)
        
        console.print(f"\n[bold]📖 Next Steps:[/bold]")
        console.print("""
[bold cyan]QOC - Quanta of Code Tool[/bold cyan]

Basic Commands:
qoc analyze <file>          # Analyze single file
qoc analyze <directory> -r  # Recursively analyze directory
qoc compare <file1> <file2> # Compare two files
""")

def load_config():
    """Load configuration file"""
    config_path = Path(__file__).parent.parent.parent / "config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Error: Configuration file not found: {config_path}[/red]")
        return None
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON in configuration file: {e}[/red]")
        return None

if __name__ == '__main__':
    main() 