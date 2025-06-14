#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QOC - Quanta of Code Tool Command Line Interface
Usage: python -m qoc <command> [options]
"""

import os
import json
import csv
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any

from .analyzer import QOCAnalyzer
from .models import QOCResult


def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        prog='qoc',
        description='🚀 QOC - Quanta of Code Analysis Tool\n\nAnalyze real code contribution, programming style-independent contribution measurement',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Supported programming languages:
  • Python (.py)
  • JavaScript/TypeScript (.js, .jsx, .ts, .tsx)  
  • Java (.java)
  • C++ (.cpp, .cc, .cxx, .hpp, .h, .hxx)

Examples:
  qoc analyze file.py                    # Analyze single file
  qoc analyze ./src -r                   # Recursively analyze directory
  qoc analyze ./src -r -d               # Show detailed information
  qoc analyze ./src -o report.json      # Output to file
  qoc compare old.py new.py              # Compare two files
  qoc demo                               # Run demo
        '''
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='QOC 1.0.0'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze Quanta of Code (QOC)',
        description='Analyze code contribution using Abstract Syntax Tree (AST) analysis'
    )
    analyze_parser.add_argument(
        'path',
        help='File or directory path to analyze'
    )
    analyze_parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Recursively analyze subdirectories'
    )
    analyze_parser.add_argument(
        '-d', '--detailed',
        action='store_true',
        help='Show detailed AST node statistics'
    )
    analyze_parser.add_argument(
        '-o', '--output',
        help='Output results to file'
    )
    analyze_parser.add_argument(
        '--format',
        choices=['console', 'json', 'csv'],
        default='console',
        help='Output format (default: console)'
    )
    
    # Compare command
    compare_parser = subparsers.add_parser(
        'compare',
        help='Compare QOC differences between two files',
        description='Compare code complexity between two files'
    )
    compare_parser.add_argument(
        'file1',
        help='First file to compare'
    )
    compare_parser.add_argument(
        'file2',
        help='Second file to compare'
    )
    
    # Demo command
    demo_parser = subparsers.add_parser(
        'demo',
        help='Demonstrate QOC functionality',
        description='Analyze code files to showcase QOC tool capabilities'
    )
    
    return parser


def analyze_command(args):
    """Handle analyze command"""
    # Check if path exists
    if not os.path.exists(args.path):
        print(f"❌ Error: Path does not exist: {args.path}")
        return 1
    
    analyzer = QOCAnalyzer()
    
    if os.path.isfile(args.path):
        # Analyze single file
        result = analyzer.analyze_file(args.path)
        if result:
            results = [result]
        else:
            print("❌ Analysis failed")
            return 1
    else:
        # Analyze directory
        results = analyzer.analyze_directory(args.path, args.recursive)
        if not results:
            print("⚠️  No supported files found")
            return 1
    
    if args.format == 'console':
        if len(results) == 1:
            analyzer.print_result(results[0], args.detailed)
        else:
            analyzer.print_summary(results)
            if args.detailed:
                print("\n🔍 Detailed Results:")
                for result in results:
                    print(f"\n{'='*60}")
                    analyzer.print_result(result, args.detailed)
    
    elif args.format == 'json':
        output_data = {
            'summary': {
                'total_files': len(results),
                'total_qoc': sum(r.total_qoc for r in results),
                'total_loc': sum(r.loc for r in results),  # Lines of Code (including empty lines)
                'total_sloc': sum(r.sloc for r in results),  # Source Lines of Code (excluding empty lines)
                'total_nodes': sum(r.ast_nodes for r in results)
            },
            'files': []
        }
        
        for result in results:
            file_data = {
                'filepath': result.filepath,
                'language': result.language,
                'qoc': result.total_qoc,
                'loc': result.loc,  # Lines of Code
                'sloc': result.sloc,  # Source Lines of Code
                'ast_nodes': result.ast_nodes
            }
            
            if args.detailed and result.node_stats:
                file_data['node_stats'] = {}
                for node_type, node_info in result.node_stats.items():
                    file_data['node_stats'][node_type] = {
                        'count': node_info.count,
                        'weight': node_info.weight,
                        'total_weight': node_info.total_weight
                    }
            
            output_data['files'].append(file_data)
        
        json_output = json.dumps(output_data, indent=2, ensure_ascii=False)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"✅ Results saved to: {args.output}")
        else:
            print(json_output)
    
    elif args.format == 'csv':
        if args.output:
            with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Filename', 'Language', 'QOC', 'AST Nodes', 'LOC', 'SLOC', 'QOC/SLOC Ratio'])
                
                for result in results:
                    ratio = result.total_qoc / result.sloc if result.sloc > 0 else 0
                    writer.writerow([
                        result.filepath,
                        result.language,
                        f"{result.total_qoc:.1f}",
                        result.ast_nodes,
                        result.loc,
                        result.sloc,
                        f"{ratio:.2f}"
                    ])
            print(f"✅ CSV results saved to: {args.output}")
        else:
            print("❌ CSV format requires output file (-o)")
            return 1
    
    return 0


def compare_command(args):
    """Handle compare command"""
    # Check if files exist
    if not os.path.exists(args.file1):
        print(f"❌ Error: File does not exist: {args.file1}")
        return 1
    
    if not os.path.exists(args.file2):
        print(f"❌ Error: File does not exist: {args.file2}")
        return 1
    
    analyzer = QOCAnalyzer()
    
    result1 = analyzer.analyze_file(args.file1)
    result2 = analyzer.analyze_file(args.file2)
    
    if not result1 or not result2:
        print("❌ Analysis failed")
        return 1
    
    # Calculate differences
    qoc_diff = result2.total_qoc - result1.total_qoc
    sloc_diff = result2.sloc - result1.sloc
    loc_diff = result2.loc - result1.loc
    nodes_diff = result2.ast_nodes - result1.ast_nodes
    
    # Display comparison results
    print("\n📊 File Comparison Results")
    print("=" * 60)
    print(f"{'Metric':<25} {'File 1':<15} {'File 2':<15} {'Difference':<15}")
    print("=" * 60)
    print(f"{'File Path':<25} {str(result1.filepath):<15} {str(result2.filepath):<15} {'-':<15}")
    print(f"{'QOC':<25} {result1.total_qoc:<15.1f} {result2.total_qoc:<15.1f} {qoc_diff:<+15.1f}")
    print(f"{'LOC':<25} {result1.loc:<15} {result2.loc:<15} {loc_diff:<+15}")
    print(f"{'SLOC':<25} {result1.sloc:<15} {result2.sloc:<15} {sloc_diff:<+15}")
    print(f"{'AST Nodes':<25} {result1.ast_nodes:<15} {result2.ast_nodes:<15} {nodes_diff:<+15}")
    
    # Calculate efficiency ratios
    ratio1 = result1.total_qoc / result1.sloc if result1.sloc > 0 else 0
    ratio2 = result2.total_qoc / result2.sloc if result2.sloc > 0 else 0
    ratio_diff = ratio2 - ratio1
    
    print(f"{'Efficiency Ratio':<25} {ratio1:<15.2f} {ratio2:<15.2f} {ratio_diff:<+15.2f}")
    print("=" * 60)
    
    # Analysis conclusion
    print("\n🔍 Analysis Conclusion:")
    
    if qoc_diff > 0:
        conclusion = f"File 2's code complexity increased by {qoc_diff:.1f} QOC"
    elif qoc_diff < 0:
        conclusion = f"File 2's code complexity decreased by {abs(qoc_diff):.1f} QOC"
    else:
        conclusion = "Both files have similar code complexity"
    
    print(conclusion)
    return 0


def demo_command(args):
    """Handle demo command"""
    print("🚀 QOC Demo\n")
    print("Demonstrating QOC analysis capabilities...\n")
    
    analyzer = QOCAnalyzer()
    
    # Check if src directory exists
    src_path = "src"
    if not os.path.exists(src_path):
        print("⚠️  src directory not found. Using current directory instead.")
        src_path = "."
    
    print(f"📁 Analyzing {src_path} directory...")
    results = analyzer.analyze_directory(src_path, recursive=True)
    
    if not results:
        print("⚠️  No supported files found.")
        return 1
    
    print(f"✅ Found {len(results)} files\n")
    
    # Display file analysis results in table format
    print("📊 File Analysis Results:")
    print("=" * 80)
    print(f"{'File':<30} {'Lang':<10} {'QOC':<8} {'LOC':<6} {'SLOC':<6} {'AST':<6} {'Ratio':<6}")
    print("=" * 80)
    
    for result in results:
        # Truncate long file paths for better display
        filepath = result.filepath
        if len(filepath) > 34:
            filepath = "..." + filepath[-31:]
        
        ratio = result.total_qoc / result.sloc if result.sloc > 0 else 0
        
        print(f"{filepath:<30} {result.language:<10} {result.total_qoc:<8.1f} {result.loc:<6} {result.sloc:<6} {result.ast_nodes:<6} {ratio:<6.2f}")
    
    print("=" * 80)
    print()
    
    # Show summary
    analyzer.print_summary(results)
    
    print("\n📖 Try these commands:")
    print("  qoc analyze <file>          # Analyze single file")
    print("  qoc analyze <directory> -r  # Recursively analyze directory")
    print("  qoc compare <file1> <file2> # Compare two files")
    
    return 0


def load_config():
    """Load configuration file"""
    config_path = Path(__file__).parent.parent.parent / "config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Configuration file not found: {config_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in configuration file: {e}")
        return None


def main():
    """Main entry point"""
    parser = create_parser()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    args = parser.parse_args()
    
    # Execute the appropriate command
    try:
        if args.command == 'analyze':
            return analyze_command(args)
        elif args.command == 'compare':
            return compare_command(args)
        elif args.command == 'demo':
            return demo_command(args)
        else:
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        print("\n⚠️  Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 