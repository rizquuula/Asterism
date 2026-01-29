---
name: code-reader
description: Reads and analyzes source code files to extract structural information. Use when users need to parse code files, extract function metadata, understand code organization, identify imports and dependencies, or prepare structured data for code analysis. Supports multiple programming languages and provides detailed code structure information.
---

# Code Reader

## Overview
The code reader skill specializes in parsing and analyzing source code files to extract meaningful structural information. It identifies key elements such as function definitions, class structures, imports, and code patterns to provide comprehensive code analysis data.

## Usage
This skill excels at:

1. **Code Structure Analysis**
   - Extracting function metadata (name, parameters, return types, line numbers)
   - Understanding code organization and structure
   - Identifying class hierarchies and relationships
   - Mapping import statements and dependencies

2. **Code Quality Assessment**
   - Identifying code smells or patterns that need attention
   - Analyzing function complexity indicators (length, nesting, parameters)
   - Reviewing code documentation and comments
   - Evaluating error handling patterns

3. **Data Preparation**
   - Preparing structured data for further analysis by other specialists
   - Creating comprehensive code structure reports
   - Organizing code metrics for quality assessment

## Examples

### Basic Code Reading
```python
# Parse a code file and extract structure
parse_functions(file_path)
```

### Function Details Extraction
```python
# Get detailed information about specific functions
get_function_details(function_name, file_data)
```

### Code Structure Report
```python
# Generate comprehensive code structure analysis
analyze_code_structure(source_code)
```

## References
- See references/parsing-patterns.md for language-specific parsing guidelines
- See references/code-structure-standards.md for structural analysis best practices
- See references/metadata-extraction.md for detailed extraction techniques
