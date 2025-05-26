"""
Base transformation module containing the abstract base class for all transformations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Set, Type, Union

import pandas as pd

from app.constants import ERROR_MESSAGES
from app.exceptions import (ColumnError, EngineError, ParameterError,
                            TransformationError)
from app.utils.logger import setup_logger

# Optional Dask support
try:
    import dask.dataframe as dd

    DASK_AVAILABLE = True
    DataFrame = Union[pd.DataFrame, dd.DataFrame]  # Type alias for export
except ImportError:
    DASK_AVAILABLE = False
    DataFrame = pd.DataFrame  # Type alias for export


logger = setup_logger(__name__)


class BaseTransformation(ABC):
    """Base class for all data transformations with engine support."""

    def __init__(self):
        """Initialize the transformation with a logger."""
        self.logger = setup_logger(f"{__name__}.{self.__class__.__name__}")

    def transform(self, data: DataFrame, params: Dict[str, Any]) -> DataFrame:
        """
        Transform the input data according to the provided parameters.
        Automatically routes to engine-specific implementation.

        Args:
            data: Input DataFrame (pandas or Dask)
            params: Dictionary of transformation parameters

        Returns:
            Transformed DataFrame (same type as input)

        Raises:
            TransformationError: If transformation fails
        """
        try:
            self.validate_params(params)

            if self.is_dask_dataframe(data):
                return self.transform_dask(data, params)
            else:
                return self.transform_pandas(data, params)
        except Exception as e:
            if not isinstance(e, TransformationError):
                raise TransformationError(f"Transformation failed: {str(e)}") from e
            raise

    def validate_columns_exist(self, data: Union[pd.DataFrame, "dd.DataFrame"], columns: List[str]) -> None:
        """
        Validate that all specified columns exist in the DataFrame.

        Args:
            data: Input DataFrame
            columns: List of column names to validate

        Raises:
            ColumnError: If any column is not found
        """
        missing_columns = [col for col in columns if col not in data.columns]
        if missing_columns:
            raise ColumnError(ERROR_MESSAGES["missing_columns"].format(", ".join(missing_columns)))

    def validate_required_params(self, params: Dict[str, Any], required_params: Set[str]) -> None:
        """
        Validate that all required parameters are present.

        Args:
            params: Dictionary of parameters
            required_params: Set of required parameter names

        Raises:
            ParameterError: If any required parameter is missing
        """
        missing_params = required_params - set(params.keys())
        if missing_params:
            raise ParameterError(ERROR_MESSAGES["missing_params"].format(missing_params))

    def validate_param_type(self, params: Dict[str, Any], param_name: str, expected_type: Type) -> None:
        """
        Validate that a parameter is of the expected type.

        Args:
            params: Dictionary of parameters
            param_name: Name of parameter to validate
            expected_type: Expected type of the parameter

        Raises:
            ParameterError: If parameter is not of expected type
        """
        if not isinstance(params[param_name], expected_type):
            raise ParameterError(ERROR_MESSAGES["invalid_param_type"].format(param_name, expected_type.__name__))

    @abstractmethod
    def transform_pandas(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """
        Pandas-specific transformation implementation.

        Args:
            data: Input pandas DataFrame
            params: Dictionary of transformation parameters

        Returns:
            Transformed pandas DataFrame
        """
        pass

    def transform_dask(self, data: "dd.DataFrame", params: Dict[str, Any]) -> "dd.DataFrame":
        """
        Dask-specific transformation implementation.
        By default, applies the transformation in parallel using Dask's map_partitions.

        Args:
            data: Input Dask DataFrame
            params: Dictionary of transformation parameters

        Returns:
            Transformed Dask DataFrame

        Raises:
            EngineError: If Dask is not available
        """
        if not DASK_AVAILABLE:
            raise EngineError(ERROR_MESSAGES["dask_not_available"])

        pass

    def is_dask_dataframe(self, data: Union[pd.DataFrame, "dd.DataFrame"]) -> bool:
        """Check if the data is a Dask DataFrame."""
        return DASK_AVAILABLE and isinstance(data, dd.DataFrame)

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the transformation."""
        pass

    def validate_params(self, params: Dict[str, Any]) -> None:
        """
        Validate transformation parameters.

        Args:
            params: Dictionary of transformation parameters

        Raises:
            ParameterError: If parameters are invalid
        """
        pass
