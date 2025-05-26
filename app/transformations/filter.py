"""
Filter transformation module for filtering rows based on conditions.
"""

from typing import Any, Dict

import pandas as pd

from app.constants import ERROR_MESSAGES, OPERATORS
from app.exceptions import (ComparisonError, EngineError,
                            NumericConversionError, OperatorError)
from app.transformations.base import BaseTransformation, DataFrame

# Optional Dask support
try:
    import dask.dataframe as dd

    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False


class FilterTransformation(BaseTransformation):
    """Filter rows based on column conditions."""

    @property
    def name(self) -> str:
        return "filter"

    def validate_params(self, params: Dict[str, Any]) -> None:
        """
        Validate filter parameters.

        Args:
            params: Dictionary containing:
                - column: Column name to filter on
                - operator: Comparison operator
                - value: Value to compare against

        Raises:
            ParameterError: If parameters are invalid
            OperatorError: If operator is invalid
        """
        required_params = {"column", "operator", "value"}
        self.validate_required_params(params, required_params)

        if params["operator"] not in OPERATORS:
            raise OperatorError(ERROR_MESSAGES["invalid_operator"].format(set(OPERATORS.keys())))

    def transform_pandas(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """
        Filter rows based on column conditions using pandas.

        Args:
            data: Input pandas DataFrame
            params: Dictionary containing:
                - column: Column name to filter on
                - operator: Comparison operator ('>', '<', '==', '>=', '<=', '!=')
                - value: Value to compare against

        Returns:
            Filtered pandas DataFrame

        Raises:
            ColumnError: If column is not found
            NumericConversionError: If numeric conversion fails
            ComparisonError: If comparison fails
        """
        column = params["column"]
        operator = params["operator"]
        value = params["value"]

        self.validate_columns_exist(data, [column])

        # Create a copy to avoid modifying the original data
        data_copy = data.copy()

        # Try to convert column to numeric if comparing with numeric value
        if isinstance(value, (int, float)):
            try:
                # Convert column to numeric, coercing errors to NaN
                data_copy[column] = pd.to_numeric(data_copy[column], errors="coerce")
                self.logger.info(f"Converted column '{column}' to numeric for comparison")
            except Exception as e:
                raise NumericConversionError(ERROR_MESSAGES["numeric_conversion_failed"].format(column, str(e)))

        try:
            mask = OPERATORS[operator](data_copy[column], value)
            # Drop rows with NaN values that resulted from conversion
            if isinstance(value, (int, float)):
                mask = mask & data_copy[column].notna()
            return data_copy[mask]
        except TypeError as e:
            raise ComparisonError(ERROR_MESSAGES["comparison_failed"].format(column, value, str(e)))
        except Exception as e:
            raise ComparisonError(ERROR_MESSAGES["filter_error"].format(str(e)))

    def transform_dask(self, data: "dd.DataFrame", params: Dict[str, Any]) -> "dd.DataFrame":
        """
        Filter rows based on column conditions using native Dask operations.

        Args:
            data: Input Dask DataFrame
            params: Dictionary containing:
                - column: Column name to filter on
                - operator: Comparison operator ('>', '<', '==', '>=', '<=', '!=')
                - value: Value to compare against

        Returns:
            Filtered Dask DataFrame

        Raises:
            ColumnError: If column is not found
            NumericConversionError: If numeric conversion fails
            ComparisonError: If comparison fails
        """
        if not DASK_AVAILABLE:
            raise EngineError(ERROR_MESSAGES["dask_not_available"])

        column = params["column"]
        operator = params["operator"]
        value = params["value"]

        self.validate_columns_exist(data, [column])

        # Try to convert column to numeric if comparing with numeric value
        if isinstance(value, (int, float)):
            try:
                # Convert column to numeric, coercing errors to NaN
                data = data.assign(**{column: dd.to_numeric(data[column], errors="coerce")})
                self.logger.info(f"Converted column '{column}' to numeric for comparison")
            except Exception as e:
                raise NumericConversionError(ERROR_MESSAGES["numeric_conversion_failed"].format(column, str(e)))

        try:
            mask = OPERATORS[operator](data[column], value)
            # Drop rows with NaN values that resulted from conversion
            if isinstance(value, (int, float)):
                mask = mask & data[column].notnull()  # Use notnull() for Dask compatibility
            return data[mask]
        except TypeError as e:
            raise ComparisonError(ERROR_MESSAGES["comparison_failed"].format(column, value, str(e)))
        except Exception as e:
            raise ComparisonError(ERROR_MESSAGES["filter_error"].format(str(e)))
