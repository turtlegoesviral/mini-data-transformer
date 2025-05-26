"""
Transformer service for executing transformation pipelines.
"""

import gc
import os
import time
from typing import Dict, List, Tuple, Union

import pandas as pd

from app.constants import ERROR_MESSAGES, LARGE_FILE_THRESHOLD
from app.core.registry import TransformationRegistry
from app.services.parser import Parser
from app.utils.progress import (MetricsCollector, ProgressTracker,
                                TransformationLogger)

# Optional Dask support
try:
    import dask.dataframe as dd

    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False


class Transformer:
    """Service for executing transformation pipelines with progress tracking."""

    def __init__(self):
        """Initialize the transformer service."""
        self.parser = Parser()
        self.registry = TransformationRegistry()

        # Initialize utilities
        self.metrics = MetricsCollector()
        self.logger = TransformationLogger()

    async def transform(self, pipeline: Dict) -> pd.DataFrame:
        """
        Transform data according to the provided pipeline.

        Args:
            pipeline: Transformation pipeline configuration

        Returns:
            Transformed DataFrame

        Raises:
            ValueError: If pipeline is invalid or transformation fails
        """
        start_time = time.time()
        self.metrics.reset()

        # Validate pipeline
        self.logger.log_validation()
        self.parser.validate_pipeline(pipeline)

        # Validate input path
        input_path = pipeline.get("input_path")
        if not input_path:
            raise ValueError(ERROR_MESSAGES["missing_params"].format("input_path"))

        # Get initial metrics
        initial_memory = self.metrics.snapshot_memory("start")

        # Determine engine based on file size
        file_size = os.path.getsize(input_path)
        is_large_file = file_size > LARGE_FILE_THRESHOLD

        if is_large_file and DASK_AVAILABLE:
            self.logger.log_info("engine_selection", "Large file detected, using Dask")
            engine = "dask"
            # Read with Dask
            try:
                data = dd.read_csv(input_path, low_memory=False, dtype_backend="numpy_nullable")
            except Exception as e:
                raise ValueError(f"Failed to read input file with Dask: {str(e)}")
        else:
            self.logger.log_info("engine_selection", "Using pandas")
            engine = "pandas"
            # Read with pandas
            try:
                data = pd.read_csv(input_path, low_memory=False, dtype_backend="numpy_nullable")
            except Exception as e:
                raise ValueError(f"Failed to read input file with pandas: {str(e)}")

        # Execute transformations with selected engine
        result = await self._execute_transformations(data, pipeline["transformations"], engine)

        # Final metrics
        final_memory = self.metrics.snapshot_memory("end")
        total_time = time.time() - start_time
        memory_delta = final_memory - initial_memory

        # Log completion
        self.logger.log_pipeline_complete(
            total_time=total_time,
            input_rows=len(data) if engine == "pandas" else None,
            output_rows=len(result) if engine == "pandas" else None,
            memory_delta=memory_delta,
        )

        return result

    async def _execute_transformations(
        self, data: Union[pd.DataFrame, dd.DataFrame], transformations: List[Dict], engine: str
    ) -> pd.DataFrame:
        """Execute a list of transformations in sequence."""
        total_steps = len(transformations)

        # Create progress tracker
        progress = ProgressTracker(desc="Transformation Pipeline", total=total_steps)

        try:
            result = data
            for i, step in enumerate(transformations):
                step_start = time.time()
                step_name = step["name"]

                progress.set_description(f"Step {i + 1}/{total_steps}: {step_name}")

                try:
                    transformation_cls = self.registry.get_transformation(step_name)
                    transformation = transformation_cls()

                    # Apply transformation
                    result = transformation.transform(result, step["params"])

                    # Track metrics
                    step_time = time.time() - step_start
                    self.metrics.record_transformation_time(step_name, step_time)

                    # Log step completion
                    self.logger.log_transformation_step(
                        step_name=step_name,
                        step_num=i + 1,
                        total_steps=total_steps,
                        duration=step_time,
                        rows=len(result) if engine == "pandas" else None,
                    )

                except Exception as e:
                    self.logger.log_error(step_name, str(e))
                    raise ValueError(f"Transformation '{step_name}' failed: {str(e)}")

                progress.update(1)

            # If using Dask, compute final result
            if engine == "dask" and isinstance(result, dd.DataFrame):
                result = result.compute()
                # Cleanup
                gc.collect()

            return result

        finally:
            progress.close()

    def get_metrics_summary(self) -> Dict:
        """Get a summary of transformation metrics."""
        return self.metrics.get_summary()
