---
name: code-analyzer
description: Analyzes code quality, complexity, and maintainability. Use when users need to assess code complexity, identify refactoring opportunities, measure cyclomatic complexity, evaluate function length and parameter counts, or detect code smells and anti-patterns. Supports multiple programming languages and provides actionable recommendations for improving code quality.
---

# Code Analyzer

## Overview
The code analyzer skill specializes in evaluating code quality and complexity metrics to identify areas that need refactoring or improvement. It provides detailed analysis of cyclomatic complexity, function length, parameter counts, and overall code maintainability.

## Usage
This skill works with structured data from code readers to analyze:

1. **Complexity Analysis**
   - Cyclomatic complexity measurement
   - Function length and nesting depth evaluation
   - Parameter count assessment
   - Code maintainability metrics

2. **Code Quality Assessment**
   - Identifying overly complex functions that should be refactored
   - Detecting functions with too many parameters (violating single responsibility)
   - Finding unusually long functions that are hard to maintain
   - Recognizing code smells and anti-patterns

3. **Standards and Best Practices**
   - Following clean code principles
   - Adhering to function complexity guidelines (typically < 10-15 complexity)
   - Parameter limits (< 5-7 parameters per function)
   - Function length recommendations (< 50-60 lines)

## Examples

### Basic Complexity Analysis
```python
# Analyze a function for complexity issues
analyze_complexity(function_data)
```

### Code Quality Report
```python
# Generate comprehensive code quality report
generate_quality_report(code_metrics)
```

### Refactoring Recommendations
```python
# Get specific recommendations for improvement
get_refactoring_recommendations(complex_functions)
```

## References
- See references/complexity-metrics.md for detailed complexity measurement guidelines
- See references/code-quality-standards.md for best practices and thresholds
- See references/refactoring-patterns.md for common refactoring approaches
