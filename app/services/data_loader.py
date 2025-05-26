"""
Data loader service for handling file loading and format validation.
"""

import json
from pathlib import Path
from typing import Dict, List, Union

import pandas as pd

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class DataLoader:
    """Service for loading and validating data files."""

    SUPPORTED_FORMATS = {".csv": "csv", ".json": "json", ".xlsx": "excel", ".xls": "excel", ".parquet": "parquet"}

    @classmethod
    def load_file(cls, file_path: Union[str, Path]) -> Union[pd.DataFrame, Dict, List]:
        """
        Load data from a file with format validation.

        Args:
            file_path: Path to the file to load

        Returns:
            Loaded data as DataFrame or dict/list for JSON

        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file does not exist
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_format = file_path.suffix.lower()
        if file_format not in cls.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported file format: {file_format}. Supported formats: {list(cls.SUPPORTED_FORMATS.keys())}"
            )

        try:
            if file_format == ".json":
                with open(file_path, "r") as f:
                    return json.load(f)
            else:
                return pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Failed to load file {file_path}: {str(e)}")
