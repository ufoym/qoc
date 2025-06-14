# QOC (Quanta of Code) - Code Contribution Measurement Tool

An AST-based code contribution measurement tool that provides more accurate code assessment than traditional line counting.

## What is QOC?

QOC (Quanta of Code) is a metric for measuring code contribution based on Abstract Syntax Tree (AST) analysis. It quantifies the actual contribution of meaningful code by assigning weights to different syntactic elements, filtering out formatting noise and focusing on substantial code contributions. Compared to traditional Lines of Code (LOC) counting, it offers the following advantages:

- **Measures actual code contribution**: Ignores blank lines, comments, code formatting and other non-contributory elements
- **Reflects real programming workload**: Based on syntactic structure rather than simple line counting
- **Language independence**: Unified measurement standard applicable to different programming languages

## Core Philosophy

Traditional Lines of Code (LOC) metrics have the following problems:

1. **Easily interfered by programming habits**: Line breaks, blank lines, comments, etc. do not affect actual code contribution
2. **Cannot distinguish code contribution**: Simple assignments and complex algorithms may have the same line count
3. **Not good at detecting refactoring**: Code block movements generate a lot of false changes

QOC solves these problems by:
- Parsing source code into Abstract Syntax Tree (AST)
- Assigning weights to different types of AST nodes based on their code contribution
- Calculating weighted sum as total code contribution (QOC value)

## Supported Programming Languages

### 🟢 Full Support (Tree-sitter AST-based analysis)

| Language | File Extensions | AST Parser | Weight Configuration |
|----------|----------------|------------|---------------------|
| **Python** | `.py` | ✅ Python + Tree-sitter | ✅ Complete |
| **JavaScript/TypeScript** | `.js`, `.jsx`, `.ts`, `.tsx` | ✅ Tree-sitter | ✅ Complete |
| **Java** | `.java` | ✅ Tree-sitter | ✅ Complete |
| **C++** | `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hxx`, `.h` | ✅ Tree-sitter | ✅ Complete |

## Features

- ✅ **Multi-language AST Analysis** - Supports Python, JavaScript, Java, C++, etc.
- ✅ **Tree-sitter Based** - High-performance, accurate syntax parsing
- ✅ **Smart Weight System** - Configurable node weights reflecting code contribution
- ✅ **Multiple Analysis Modes** - Single file, batch directory analysis
- ✅ **Detailed Statistical Reports** - AST node statistics, weight contribution analysis
- ✅ **Multiple Output Formats** - Console beautified output, JSON, CSV
- ✅ **File Comparison Feature** - Compare code contribution differences between two files
- ✅ **Language Distribution Statistics** - Statistical analysis for multi-language projects

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/ufoym/qoc
cd qoc
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start
```bash
python -m qoc demo
```

### Analyze Single File
```bash
# Basic analysis
python -m qoc analyze file.py

# Detailed analysis (show AST node statistics)
python -m qoc analyze file.java -d

# Multi-language support
python -m qoc analyze Calculator.java -d
python -m qoc analyze main.cpp -d
python -m qoc analyze app.js -d
```

### Analyze Entire Project
```bash
# Analyze current directory
python -m qoc analyze .

# Recursively analyze all subdirectories
python -m qoc analyze ./src --recursive

# Analyze multi-language projects
python -m qoc analyze . -r  # Automatically recognizes all supported languages
```

### File Comparison
```bash
python -m qoc compare old_version.py new_version.py
```

### Different Output Formats
```bash
# JSON format output
python -m qoc analyze file.py --format json

# CSV format output
python -m qoc analyze . -r --format csv

# Save to file
python -m qoc analyze . -r -o report.json --format json
```

## Practical Application Examples

### QOC Comparison Across Different Languages

```bash
# Java class: 33 lines → 363.0 QOC (ratio: 11.00)
python -m qoc analyze Calculator.java

# JavaScript class: 43 lines → 561.5 QOC (ratio: 13.06)
python -m qoc analyze Calculator.js

# C++ class: 59 lines → 885.0 QOC (ratio: 15.00)
python -m qoc analyze Calculator.cpp
```

### Large-scale Project Analysis
```bash
# Analyze entire project (example output)
python -m qoc analyze . -r

Total files: 931
Total code contribution: 2,325,852.4
Total lines of code: 251,546
Average efficiency ratio: 9.25

Language distribution:
- Python: 922 files (99.9%)
- JavaScript: 1 file (0.0%)
- Java: 1 file (0.0%) 
- C++: 1 file (0.0%)
```

## Weight Configuration

The tool uses `config.json` to configure weights for different AST nodes:

```json
{
  "languages": {
    "python": {
      "node_weights": {
        "function_definition": 10,    // High weight for function definitions
        "class_definition": 15,       // Highest weight for class definitions
        "if_statement": 3,            // Medium weight for conditional statements
        "for_statement": 4,           // Medium weight for loop statements
        "identifier": 0.5,            // Low weight for identifiers
        ...
      }
    }
  }
}
```

## Project Structure

```
qoc/
├── src/
│   └── qoc/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Command line entry
│       ├── models.py            # Data models
│       ├── analyzer.py          # Core analyzer
│       └── cli.py               # Command line interface
├── examples/                    # Example files
├── config.json                  # Configuration file
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## Technical Implementation

### AST Parsing Technology Stack
- **Tree-sitter**: High-performance incremental parsing library
- **Multi-language Support**: Language-specific parsers
- **Unified API**: Consistent node access interface

### Weight Calculation Algorithm
1. **Parsing Phase**: Parse source code into AST
2. **Traversal Phase**: Depth-first traversal of all nodes
3. **Weight Mapping**: Calculate weights based on node contribution configuration
4. **Accumulation**: Calculate total code contribution (QOC value)

## Comparison with Traditional LOC

| Metric | Traditional LOC | QOC |
|--------|-----------------|-----|
| **Code Style Independence** | ❌ Affected by formatting | ✅ Ignores formatting |
| **Code Contribution Measurement** | ❌ Simple line counting | ✅ Weighted based on actual contribution |
| **Language Consistency** | ❌ Different standards per language | ✅ Unified measurement standard |
| **Refactoring Detection** | ❌ High false positive rate | ✅ Focuses on actual code changes |
| **Measurement Accuracy** | ❌ Easily deceived | ✅ Reflects real code contribution |

## Development Guide

### Development Environment Setup
```bash
git clone https://github.com/ufoym/qoc
cd qoc
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Tests
```bash
python -m pytest tests/
```

### Add New Language Support
1. Add language configuration in `config.json`
2. Update parser initialization in `analyzer.py`
3. Add corresponding tree-sitter language package

## Contributing

Contributions and suggestions are welcome! Please follow these steps:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

## Citation

If you use QOC in your research, please cite:

```bibtex
@software{qoc2024,
title={QOC: AST-based Code Contribution Measurement Tool},
author={Ming},
year={2024},
url={https://github.com/ufoym/qoc}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- 🎉 Initial release
- ✅ Support for Python, JavaScript, Java, C++
- ✅ Tree-sitter based AST analysis
- ✅ Multiple output formats (Console, JSON, CSV)
- ✅ File comparison functionality
- ✅ Modular architecture design

---

**QOC** - Measure code contribution, not just lines. 