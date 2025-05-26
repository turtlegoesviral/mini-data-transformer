"""
Map transformation module for renaming columns.
"""

from typing import Any, Dict

import pandas as pd

from app.transformations.base import BaseTransformation, DataFrame

# Optional Dask support
try:
    import dask.dataframe as dd

    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False


class MapTransformation(BaseTransformation):
    """Map/rename columns in the DataFrame."""

    @property
    def name(self) -> str:
        return "map"

    def validate_params(self, params: Dict[str, Any]) -> None:
        """
        Validate map parameters.

        Args:
            params: Dictionary containing:
                - mappings: Dictionary of old column names to new column names

        Raises:
            ValueError: If parameters are invalid
        """
        self.validate_required_params(params, {"mappings"})
        self.validate_param_type(params, "mappings", dict)

    def transform_pandas(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """
        Map/rename columns in the pandas DataFrame.

        Args:
            data: Input pandas DataFrame
            params: Dictionary containing:
                - mappings: Dictionary of old column names to new column names

        Returns:
            pandas DataFrame with renamed columns
        """
        mappings = params["mappings"]
        self.validate_columns_exist(data, list(mappings.keys()))

        return data.rename(columns=mappings)

    def transform_dask(self, data: "dd.DataFrame", params: Dict[str, Any]) -> "dd.DataFrame":
        """
        Map/rename columns in the Dask DataFrame using native Dask operations.

        Args:
            data: Input Dask DataFrame
            params: Dictionary containing:
                - mappings: Dictionary of old column names to new column names

        Returns:
            Dask DataFrame with renamed columns
        """
        if not DASK_AVAILABLE:
            raise RuntimeError("Dask is not available but Dask DataFrame was provided")

        mappings = params["mappings"]
        self.validate_columns_exist(data, list(mappings.keys()))

        # Dask DataFrames support rename just like pandas
        return data.rename(columns=mappings)

    # Keeping the old transform method for backwards compatibility
    def transform(self, data: DataFrame, params: Dict[str, Any]) -> DataFrame:
        """
        Transform method for backwards compatibility.
        Routes to appropriate engine-specific implementation.
        """
        return super().transform(data, params)
