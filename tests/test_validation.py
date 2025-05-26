import numpy as np
import pandas as pd
import pytest


def test_required_columns(sample_dataframe):
    """Test validation of required columns."""
    required_cols = ["id", "name", "age"]
    missing_cols = [col for col in required_cols if col not in sample_dataframe.columns]
    assert len(missing_cols) == 0


def test_data_types(sample_dataframe):
    """Test validation of data types."""
    assert sample_dataframe["id"].dtype in ["int64", "int32"]
    assert sample_dataframe["name"].dtype == "object"
    assert sample_dataframe["age"].dtype in ["int64", "int32"]
    assert sample_dataframe["value"].dtype in ["int64", "int32", "float64"]


def test_null_values(sample_dataframe):
    """Test validation of null values."""
    assert sample_dataframe.isnull().sum().sum() == 0


def test_value_ranges(sample_dataframe):
    """Test validation of value ranges."""
    assert sample_dataframe["age"].min() >= 0
    assert sample_dataframe["age"].max() <= 120
    assert sample_dataframe["value"].min() >= 0


def test_unique_constraints(sample_dataframe):
    """Test validation of unique constraints."""
    assert sample_dataframe["id"].is_unique


def test_string_length(sample_dataframe):
    """Test validation of string lengths."""
    assert all(len(str(name)) <= 50 for name in sample_dataframe["name"])


def test_categorical_values(sample_dataframe):
    """Test validation of categorical values."""
    valid_categories = ["A", "B", "C"]
    assert all(cat in valid_categories for cat in sample_dataframe["category"])
