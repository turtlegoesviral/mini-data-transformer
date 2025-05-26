"""
Custom exceptions for the application.
"""


class TransformationError(Exception):
    """Base exception for transformation errors."""

    pass


class ValidationError(TransformationError):
    """Exception for validation errors."""

    pass


class ColumnError(ValidationError):
    """Exception for column-related errors."""

    pass


class ParameterError(ValidationError):
    """Exception for parameter-related errors."""

    pass


class OperatorError(ValidationError):
    """Exception for operator-related errors."""

    pass


class EngineError(TransformationError):
    """Exception for engine-related errors."""

    pass


class NumericConversionError(TransformationError):
    """Exception for numeric conversion errors."""

    pass


class ComparisonError(TransformationError):
    """Exception for comparison errors."""

    pass
