"""Example file with various complexity levels for analysis."""


def simple_function(x, y):
    """A simple function with low complexity."""
    return x + y


def medium_complexity_function(data, threshold=10):
    """
    A function with medium complexity.

    This function demonstrates moderate complexity with some conditional logic.
    """
    result = []

    for item in data:
        if item > threshold:
            if item % 2 == 0:
                result.append(item * 2)
            else:
                result.append(item * 3)
        else:
            result.append(item)

    return result


def highly_complex_function(matrix, operations, filters=None, transformers=None, validators=None):
    """
    A highly complex function that violates many clean code principles.

    This function demonstrates:
    - Too many parameters (6+ parameters)
    - High cyclomatic complexity
    - Long function length
    - Nested conditionals
    - Multiple responsibilities
    """
    if not matrix:
        return []

    results = []

    for row_idx, row in enumerate(matrix):
        if row_idx % 2 == 0:  # Process even rows
            if operations.get('double', False):
                if filters and 'even_only' in filters:
                    if all(isinstance(x, (int, float)) for x in row):
                        if validators:
                            if all(validator(x) for x in row for validator in validators):
                                if transformers:
                                    transformed = []
                                    for x in row:
                                        for transformer in transformers:
                                            x = transformer(x)
                                        transformed.append(x)
                                    results.append(transformed)
                                else:
                                    results.append([x * 2 for x in row])
                        else:
                            results.append([x * 2 for x in row])
                    else:
                        results.append(row)
                else:
                    results.append([x * 2 for x in row])
            else:
                results.append(row)
        else:  # Process odd rows
            if operations.get('triple', False):
                results.append([x * 3 for x in row])
            else:
                results.append(row)

    # Final processing step
    if operations.get('sort', False):
        results.sort(key=lambda x: sum(x) if x else 0, reverse=True)

    if operations.get('flatten', False):
        results = [item for sublist in results for item in sublist]

    return results


def another_complex_function(a, b, c, d, e, f, g=True, h=None, i=42, j="default"):
    """
    Another complex function with many parameters and high complexity.

    This function demonstrates parameter explosion and complex logic.
    """
    if g and h is not None:
        if isinstance(a, list) and isinstance(b, dict):
            if c > 0 and d < 100:
                if e in ['option1', 'option2', 'option3']:
                    if f is not None:
                        if i > 0:
                            if len(j) > 0:
                                # Complex nested logic here
                                result = a.copy()
                                for key, value in b.items():
                                    if key.startswith('prefix_'):
                                        if value > c and value < d:
                                            if e == 'option1':
                                                result.append(value * 2)
                                            elif e == 'option2':
                                                result.append(value * 3)
                                            else:
                                                result.append(value * 4)
                                return result
    return []


def function_with_nested_loops(data, depth=3, multiplier=2):
    """Function with deeply nested loops."""
    result = []

    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            for k in range(j + 1, len(data)):
                if depth > 2:
                    for m in range(k + 1, len(data)):
                        if depth > 3:
                            for n in range(m + 1, len(data)):
                                # Deep nesting
                                if data[i] + data[j] + data[k] + data[m] + data[n] > 100:
                                    result.append((i, j, k, m, n))
                        else:
                            if data[i] + data[j] + data[k] + data[m] > 50:
                                result.append((i, j, k, m))
                else:
                    if data[i] + data[j] + data[k] > 25:
                        result.append((i, j, k))

    return result


def function_without_docstring(param1, param2, param3):
    # This function lacks proper documentation
    x = param1 + param2
    y = x * param3
    z = y / 2
    return z