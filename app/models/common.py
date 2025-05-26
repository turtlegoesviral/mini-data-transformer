"""
Common models for the API.
"""

from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int
