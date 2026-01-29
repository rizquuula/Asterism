"""Utility functions - mix of good and bad practices."""


def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)


def process_data_v1(data, config):  # Too many parameters, complex logic
    """Version 1 - poorly designed function."""
    result = []
    for item in data:
        if config.get("filter_enabled", False):
            if config.get("min_value", 0) <= item <= config.get("max_value", 100):
                if config.get("transform_enabled", False):
                    if config.get("transform_type") == "square":
                        result.append(item**2)
                    elif config.get("transform_type") == "cube":
                        result.append(item**3)
                    elif config.get("transform_type") == "sqrt":
                        result.append(item**0.5)
                    else:
                        result.append(item)
                else:
                    result.append(item)
        else:
            result.append(item)
    return result


def process_data_v2(data, filter_config=None, transform_config=None):
    """
    Version 2 - better designed function with extracted logic.

    This version is more maintainable with smaller functions.
    """
    if filter_config and filter_config.get("enabled", False):
        data = _apply_filter(data, filter_config)

    if transform_config and transform_config.get("enabled", False):
        data = _apply_transform(data, transform_config)

    return data


def _apply_filter(data, config):
    """Apply filtering logic."""
    min_val = config.get("min_value", 0)
    max_val = config.get("max_value", 100)
    return [x for x in data if min_val <= x <= max_val]


def _apply_transform(data, config):
    """Apply transformation logic."""
    transform_type = config.get("type", "none")

    if transform_type == "square":
        return [x**2 for x in data]
    elif transform_type == "cube":
        return [x**3 for x in data]
    elif transform_type == "sqrt":
        return [x**0.5 for x in data]
    else:
        return data


# Missing docstring example
def undocumented_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                return x + y + z
            else:
                return x + y
        else:
            return x
    else:
        return 0


def very_long_function_that_does_many_things(a, b, c, d, e, f, g, h, i, j):
    """
    This function is way too long and does too many things.
    It violates the Single Responsibility Principle.
    """
    # Input validation (should be separate function)
    if not all(isinstance(x, (int, float)) for x in [a, b, c, d, e, f, g, h, i, j]):
        raise ValueError("All parameters must be numbers")

    # Calculation 1 (should be separate function)
    result1 = a + b + c

    # Calculation 2 (should be separate function)
    result2 = d * e * f

    # Calculation 3 (should be separate function)
    result3 = (g + h) / (i + j) if i + j != 0 else 0

    # More calculations...
    intermediate = result1 + result2
    final_result = intermediate * result3

    # Logging (should be separate concern)
    print(f"Calculation completed: {final_result}")

    # File I/O (should definitely be separate)
    with open("calculation_log.txt", "a") as f:
        f.write(f"{final_result}\n")

    # Return result
    return final_result
