"""
Uppercase transformation module for converting string columns to uppercase.
"""

from typing import Any, Dict, List

import pandas as pd

from app.transformations.base import BaseTransformation, DataFrame

# Optional Dask support
try:
    import dask.dataframe as dd

    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False


class UppercaseTransformation(BaseTransformation):
    """Convert string columns to uppercase."""

    @property
    def name(self) -> str:
        return "uppercase"

    def validate_params(self, params: Dict[str, Any]) -> None:
        """
        Validate uppercase parameters.

        Args:
            params: Dictionary containing:
                - columns: List of column names to convert to uppercase

        Raises:
            ValueError: If parameters are invalid
        """
        self.validate_required_params(params, {"columns"})
        self.validate_param_type(params, "columns", list)

    def transform_pandas(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert specified string columns to uppercase using pandas.

        Args:
            data: Input pandas DataFrame
            params: Dictionary containing:
                - columns: List of column names to convert to uppercase

        Returns:
            pandas DataFrame with uppercase columns
        """
        columns = params["columns"]
        self.validate_columns_exist(data, columns)

        result = data.copy()
        for column in columns:
            result[column] = result[column].astype(str).str.upper()
        return result

    def transform_dask(self, data: "dd.DataFrame", params: Dict[str, Any]) -> "dd.DataFrame":
        """
        Convert specified string columns to uppercase using native Dask operations.

        Args:
            data: Input Dask DataFrame
            params: Dictionary containing:
                - columns: List of column names to convert to uppercase

        Returns:
            Dask DataFrame with uppercase columns
        """
        if not DASK_AVAILABLE:
            raise RuntimeError("Dask is not available but Dask DataFrame was provided")

        columns = params["columns"]
        self.validate_columns_exist(data, columns)

        # Create a copy and transform columns using Dask operations
        result = data.copy()
        for column in columns:
            # Dask supports string operations in a similar way to pandas
            result[column] = result[column].astype(str).str.upper()
        return result

    # Keeping the old transform method for backwards compatibility
    def transform(self, data: DataFrame, params: Dict[str, Any]) -> DataFrame:
        """
        Transform method for backwards compatibility.
        Routes to appropriate engine-specific implementation.
        """
        return super().transform(data, params)
