"""
Transform endpoint for data transformation operations.
"""

import math
import os
import time

import numpy as np
import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, Query

from app.models.common import PaginatedResponse
from app.services.parser import Parser
from app.services.transformer import Transformer
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


@router.post("/transform", response_model=PaginatedResponse)
async def transform_data(
    pipeline: str = Form(...),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=1000, description="Items per page"),
):
    """
    Transform data according to the provided pipeline.

    Args:
        pipeline: JSON/YAML string containing transformation pipeline with file path
        page: Page number (starts from 1)
        size: Number of items per page

    Returns:
        Paginated transformed data with performance metrics
    """
    start_time = time.time()
    logger.info(f"Starting transformation for pipeline: {pipeline}")

    try:
        # Parse input
        parse_start = time.time()
        parser = Parser()

        try:
            # Parse pipeline first to validate it
            pipeline_data = parser.parse_pipeline(pipeline)
            logger.info(f"Pipeline parsed: {len(pipeline_data.get('transformations', []))} transformations")

            # Validate input path
            input_path = pipeline_data.get("input_path")
            if not input_path:
                raise ValueError("Input path is required in pipeline configuration")

            if not os.path.exists(input_path):
                raise ValueError(f"Input path does not exist: {input_path}")

        except Exception as e:
            logger.error(f"Parsing failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Parsing error: {str(e)}")

        parse_time = time.time() - parse_start
        logger.info(f"Parsing completed in {parse_time:.2f}s")

        # Transform data
        transform_start = time.time()

        try:
            transformer = Transformer()
            result = await transformer.transform(pipeline_data)
            logger.info(f"Transformation completed: {result.shape[0]:,} rows x {result.shape[1]} columns")

        except Exception as e:
            logger.error(f"Transformation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Transformation error: {str(e)}")

        transform_time = time.time() - transform_start
        logger.info(f"Transformation completed in {transform_time:.2f}s")

        # Get transformation metrics
        metrics = transformer.get_metrics_summary()

        # Convert to JSON and apply pagination
        json_start = time.time()

        # Handle special values at DataFrame level
        result = result.replace([np.inf, -np.inf], None)
        result = result.where(pd.notna(result), None)

        # Calculate pagination on DataFrame
        total = len(result)
        pages = math.ceil(total / size)
        start_idx = (page - 1) * size
        end_idx = start_idx + size

        # Only convert the paginated slice to JSON
        paginated_df = result.iloc[start_idx:end_idx]
        records = paginated_df.to_dict(orient="records")

        json_time = time.time() - json_start
        total_time = time.time() - start_time
        logger.info(f"Total processing time: {total_time:.2f}s")
        logger.info(f"📊 Performance breakdown:")
        logger.info(f"   📋 Parse: {parse_time:.2f}s ({parse_time / total_time * 100:.1f}%)")
        logger.info(f"   🔄 Transform: {transform_time:.2f}s ({transform_time / total_time * 100:.1f}%)")
        logger.info(f"   📄 JSON: {json_time:.2f}s ({json_time / total_time * 100:.1f}%)")

        # Add performance metadata to response
        response_data = PaginatedResponse(items=records, total=total, page=page, size=size, pages=pages)

        # Add metrics as metadata
        logger.info(f"📈 Transformation metrics: {metrics}")

        return response_data

    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"💥 Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
