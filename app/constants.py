"""
Constants used across the application.
"""

# File size constants
GB_IN_BYTES = 1024 * 1024 * 1024
LARGE_FILE_THRESHOLD = 2 * GB_IN_BYTES  # 2GB threshold for large files

# Transformation operators
OPERATORS = {
    ">": lambda x, y: x > y,
    "<": lambda x, y: x < y,
    "==": lambda x, y: x == y,
    ">=": lambda x, y: x >= y,
    "<=": lambda x, y: x <= y,
    "!=": lambda x, y: x != y,
}

# Valid transformation names
VALID_TRANSFORMATIONS = {"uppercase", "map", "filter"}

# Valid processing engines
VALID_ENGINES = {"pandas", "dask"}

# Error messages
ERROR_MESSAGES = {
    "missing_columns": "Columns not found in data: {}",
    "missing_params": "Missing required parameters: {}",
    "invalid_param_type": "Parameter '{}' must be a {}",
    "invalid_operator": "Invalid operator. Must be one of: {}",
    "invalid_transformation": "Invalid transformation name. Must be one of: {}",
    "invalid_engine": "Invalid engine. Must be one of: {}",
    "dask_not_available": "Dask is not available but Dask DataFrame was provided",
    "numeric_conversion_failed": "Could not convert column '{}' to numeric: {}",
    "comparison_failed": "Cannot compare column '{}' with value '{}': {}",
    "filter_error": "Error filtering data: {}",
}
