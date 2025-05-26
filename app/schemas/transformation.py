"""
Schemas for transformation API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class TransformationStepSchema(BaseModel):
    """Schema for a transformation step in API requests/responses."""

    name: str = Field(..., description="Name of the transformation")
    params: Dict[str, Any] = Field(default_factory=dict, description="Transformation parameters")

    @validator("name")
    def validate_name(cls, v):
        """Validate transformation name."""
        valid_names = {"uppercase", "map", "filter"}  # Add more as needed
        if v not in valid_names:
            raise ValueError(f"Invalid transformation name. Must be one of: {valid_names}")
        return v


class TransformationPipelineSchema(BaseModel):
    """Schema for transformation pipeline in API requests/responses."""

    file_path: str = Field(..., description="Path to the input CSV file")
    transformations: List[TransformationStepSchema] = Field(..., description="List of transformation steps")

    @validator("transformations")
    def validate_transformations(cls, v):
        """Validate transformations list."""
        if not v:
            raise ValueError("At least one transformation is required")
        return v

    @validator("file_path")
    def validate_file_path(cls, v):
        """Validate file path."""
        if not v or not v.strip():
            raise ValueError("File path is required")
        return v


class TransformationRequestSchema(BaseModel):
    """Schema for transformation request."""

    pipeline: TransformationPipelineSchema = Field(..., description="Transformation pipeline")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=1000, description="Items per page")
    engine: str = Field("dask", description="Processing engine to use")

    @validator("engine")
    def validate_engine(cls, v):
        """Validate processing engine."""
        valid_engines = {"pandas", "dask"}
        if v not in valid_engines:
            raise ValueError(f"Invalid engine. Must be one of: {valid_engines}")
        return v


class TransformationResponseSchema(BaseModel):
    """Schema for transformation response."""

    items: List[Dict[str, Any]] = Field(..., description="Transformed data items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    processing_time: float = Field(..., description="Processing time in seconds")
    engine: str = Field(..., description="Processing engine used")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
