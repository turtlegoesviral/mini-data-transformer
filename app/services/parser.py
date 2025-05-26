"""
Parser service for handling pipeline configurations.
"""

import json
from typing import Dict, Union

import yaml

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ParserError(Exception):
    """Base exception for parser errors."""

    pass


class PipelineValidationError(ParserError):
    """Raised when pipeline validation fails."""

    pass


class Parser:
    """Parser service for handling pipeline configurations."""

    @staticmethod
    def parse_pipeline(pipeline: Union[str, Dict]) -> Dict:
        """
        Parse transformation pipeline configuration.

        Args:
            pipeline: Pipeline configuration as string (JSON/YAML) or dict

        Returns:
            Parsed pipeline configuration

        Raises:
            PipelineValidationError: If pipeline configuration is invalid
        """
        try:
            # Try parsing as YAML first
            return yaml.safe_load(pipeline)
        except yaml.YAMLError:
            try:
                # Try parsing as JSON
                return json.loads(pipeline)
            except json.JSONDecodeError as e:
                raise PipelineValidationError(f"Invalid pipeline configuration: {str(e)}")

    @staticmethod
    def validate_pipeline(pipeline: Dict) -> None:
        """
        Validate pipeline configuration.

        Args:
            pipeline: Pipeline configuration

        Raises:
            PipelineValidationError: If pipeline configuration is invalid
        """
        if "transformations" not in pipeline:
            raise PipelineValidationError("Pipeline must contain 'transformations' key")

        if not isinstance(pipeline["transformations"], list):
            raise PipelineValidationError("'transformations' must be a list")

        for step in pipeline["transformations"]:
            if not isinstance(step, dict):
                raise PipelineValidationError("Each transformation step must be a dictionary")

            if "name" not in step:
                raise PipelineValidationError("Each transformation step must have a 'name'")

            if "params" not in step:
                raise PipelineValidationError("Each transformation step must have 'params'")

            if not isinstance(step["params"], dict):
                raise PipelineValidationError("'params' must be a dictionary")
