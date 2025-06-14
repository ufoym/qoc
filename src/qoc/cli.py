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


def print_result(result: QOCResult, detailed: bool = False):
    """打印分析结果"""
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


def print_summary(results: List[QOCResult]):
    """打印分析摘要"""
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


def print_warning(message: str):
    """打印警告信息"""
    print(f"⚠️  Warning: {message}")


def print_error(message: str):
    """打印错误信息"""
    print(f"❌ Error: {message}")


def print_success(message: str):
    """打印成功信息"""
    print(f"✅ {message}")


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
        print_error(f"Path does not exist: {args.path}")
        return 1
    
    try:
        analyzer = QOCAnalyzer()
        
        # Show warnings for failed language parsers
        failed_languages = analyzer.get_failed_languages()
        for lang, error in failed_languages:
            print_warning(f"Cannot initialize {lang} parser: {error}")
        
        if os.path.isfile(args.path):
            # Analyze single file
            result = analyzer.analyze_file(args.path)
            results = [result]
        else:
            # Analyze directory
            results = analyzer.analyze_directory(args.path, args.recursive)
            if not results:
                print_warning("No supported files found")
                return 1
        
        if args.format == 'console':
            if len(results) == 1:
                print_result(results[0], args.detailed)
            else:
                print_summary(results)
                if args.detailed:
                    print("\n🔍 Detailed Results:")
                    for result in results:
                        print(f"\n{'='*60}")
                        print_result(result, args.detailed)
        
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
                print_success(f"Results saved to: {args.output}")
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
                print_success(f"CSV results saved to: {args.output}")
            else:
                print_error("CSV format requires output file (-o)")
                return 1
        
        return 0
        
    except ImportError as e:
        print_error(str(e))
        return 1
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print_error(str(e))
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1


def compare_command(args):
    """Handle compare command"""
    # Check if files exist
    if not os.path.exists(args.file1):
        print_error(f"File does not exist: {args.file1}")
        return 1
    
    if not os.path.exists(args.file2):
        print_error(f"File does not exist: {args.file2}")
        return 1
    
    try:
        analyzer = QOCAnalyzer()
        
        # Show warnings for failed language parsers
        failed_languages = analyzer.get_failed_languages()
        for lang, error in failed_languages:
            print_warning(f"Cannot initialize {lang} parser: {error}")
        
        result1 = analyzer.analyze_file(args.file1)
        result2 = analyzer.analyze_file(args.file2)
        
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
        
    except ImportError as e:
        print_error(str(e))
        return 1
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print_error(str(e))
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1


def demo_command(args):
    """Handle demo command"""
    print("🚀 QOC Demo\n")
    print("Demonstrating QOC analysis capabilities...\n")
    
    try:
        analyzer = QOCAnalyzer()
        
        # Show warnings for failed language parsers
        failed_languages = analyzer.get_failed_languages()
        for lang, error in failed_languages:
            print_warning(f"Cannot initialize {lang} parser: {error}")
        
        # Check if src directory exists
        src_path = "src"
        if not os.path.exists(src_path):
            print_warning("src directory not found. Using current directory instead.")
            src_path = "."
        
        print(f"📁 Analyzing {src_path} directory...")
        results = analyzer.analyze_directory(src_path, recursive=True)
        
        if not results:
            print_warning("No supported files found.")
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
        print_summary(results)
        
        print("\n📖 Try these commands:")
        print("  qoc analyze <file>          # Analyze single file")
        print("  qoc analyze <directory> -r  # Recursively analyze directory")
        print("  qoc compare <file1> <file2> # Compare two files")
        
        return 0
        
    except ImportError as e:
        print_error(str(e))
        return 1
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print_error(str(e))
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1


def load_config():
    """Load configuration file"""
    config_path = Path(__file__).parent.parent.parent / "config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print_error(f"Configuration file not found: {config_path}")
        return None
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in configuration file: {e}")
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
        print_error(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 