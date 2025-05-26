"""
Transformation registry module for managing available transformations.
"""

from typing import Dict, Type

from app.transformations.base import BaseTransformation
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class TransformationRegistry:
    """Registry for managing available transformations."""

    _instance = None
    _transformations: Dict[str, Type[BaseTransformation]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TransformationRegistry, cls).__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, transformation_cls: Type[BaseTransformation]) -> Type[BaseTransformation]:
        """
        Register a transformation class.

        Args:
            transformation_cls: Transformation class to register

        Returns:
            The registered transformation class
        """
        instance = transformation_cls()
        cls._transformations[instance.name] = transformation_cls
        logger.info(f"Registered transformation: {instance.name}")
        return transformation_cls

    @classmethod
    def get_transformation(cls, name: str) -> Type[BaseTransformation]:
        """
        Get a transformation class by name.

        Args:
            name: Name of the transformation

        Returns:
            Transformation class

        Raises:
            KeyError: If transformation with given name is not found
        """
        if name not in cls._transformations:
            raise KeyError(f"Transformation '{name}' not found in registry")
        return cls._transformations[name]

    @classmethod
    def list_transformations(cls) -> Dict[str, Type[BaseTransformation]]:
        """
        List all registered transformations.

        Returns:
            Dictionary of transformation names and their classes
        """
        return cls._transformations.copy()
