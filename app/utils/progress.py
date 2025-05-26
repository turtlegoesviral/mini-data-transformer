"""
Progress tracking utilities for data transformation operations.
"""

import gc
import time
from typing import Dict, List, Optional

import psutil
from tqdm import tqdm

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ProgressTracker:
    """Helper class for tracking progress across different operations."""

    def __init__(self, desc: str = "Processing", total: int = 100):
        """
        Initialize progress tracker.

        Args:
            desc: Description for the progress bar
            total: Total number of items to process
        """
        self.desc = desc
        self.total = total
        self.start_time = time.time()
        self.pbar = tqdm(
            desc=desc, total=total, unit="items", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
        )

    def update(self, n: int = 1, desc: Optional[str] = None):
        """Update progress bar."""
        if desc:
            self.pbar.set_description(desc)
        self.pbar.update(n)

    def set_description(self, desc: str):
        """Set progress bar description."""
        self.pbar.set_description(desc)

    def close(self) -> float:
        """Close progress bar and return elapsed time."""
        elapsed = time.time() - self.start_time
        self.pbar.close()
        return elapsed


class MetricsCollector:
    """Class to collect and track transformation metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.reset()

    def reset(self):
        """Reset all metrics."""
        self.memory_usage_mb = 0
        self.processing_time_s = 0
        self.rows_processed = 0
        self.transformation_times = {}
        self.batch_metrics = []
        self.memory_snapshots = {}

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0

    def snapshot_memory(self, stage: str) -> float:
        """Take a memory snapshot at specific stage."""
        memory_mb = self.get_memory_usage()
        self.memory_snapshots[stage] = memory_mb
        return memory_mb

    def record_transformation_time(self, transformation_name: str, duration: float):
        """Record time taken for a specific transformation."""
        self.transformation_times[transformation_name] = duration

    def add_batch_metric(self, batch_info: Dict):
        """Add metrics for a processed batch."""
        self.batch_metrics.append(batch_info)

    def get_summary(self) -> Dict:
        """Get a summary of all collected metrics."""
        return {
            "memory_usage_mb": self.memory_usage_mb,
            "processing_time_s": self.processing_time_s,
            "rows_processed": self.rows_processed,
            "transformation_times": self.transformation_times,
            "batch_metrics": self.batch_metrics,
            "memory_snapshots": self.memory_snapshots,
        }


class TransformationLogger:
    """Minimal logger for transformation operations."""

    def __init__(self):
        """Initialize transformation logger."""
        self.logger = setup_logger(__name__)

    def log_pipeline_start(self, rows: int, columns: int, engine: str, chunk_size: int):
        """Log the start of pipeline processing."""
        self.logger.info(f"Processing {rows:,} rows with {engine} engine")

    def log_pipeline_complete(
        self, total_time: float, input_rows: Optional[int], output_rows: Optional[int], memory_delta: float
    ):
        """Log pipeline completion."""
        if input_rows is not None and output_rows is not None and input_rows > 0:
            retention = output_rows / input_rows * 100
            self.logger.info(f"Completed: {output_rows:,} rows ({retention:.1f}% retention) in {total_time:.2f}s")
        else:
            self.logger.info(f"Completed in {total_time:.2f}s")

    def log_transformation_step(
        self, step_name: str, step_num: int, total_steps: int, duration: float, rows: Optional[int]
    ):
        """Log individual transformation step - minimal logging."""
        pass  # Skip detailed step logging

    def log_chunk_processing(self, total_rows: int, num_chunks: int, chunk_size: int):
        """Log chunk processing information."""
        if num_chunks > 1:
            self.logger.info(f"Processing in {num_chunks} chunks")

    def log_error(self, operation: str, error: str):
        """Log transformation errors."""
        self.logger.error(f"Error in {operation}: {error}")

    def log_validation(self):
        """Log pipeline validation."""
        pass  # Skip validation logging

    def log_memory_cleanup(self):
        """Log memory cleanup operations."""
        gc.collect()  # Just do cleanup without logging

    def log_info(self, operation: str, message: str):
        """Log informational messages."""
        self.logger.info(f"{operation}: {message}")
