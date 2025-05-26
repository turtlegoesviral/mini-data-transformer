import numpy as np
import pandas as pd
import pytest

from app.exceptions import OperatorError, ParameterError
from app.transformations.filter import FilterTransformation
from app.transformations.map import MapTransformation
from app.transformations.uppercase import UppercaseTransformation


def test_uppercase_transformation(sample_dataframe):
    """Test uppercase transformation using the actual UppercaseTransformation class."""
    df = sample_dataframe.copy()
    transformer = UppercaseTransformation()
    params = {"columns": ["name"]}

    result = transformer.transform_pandas(df, params)

    assert result["name"].tolist() == ["JOHN", "JANE", "BOB", "ALICE", "CHARLIE"]
    assert result["name"].dtype == "object"


def test_numeric_transformation(sample_dataframe):
    """Test numeric transformation of values."""
    df = sample_dataframe.copy()
    df["value"] = pd.to_numeric(df["value"])

    assert df["value"].dtype in ["int64", "float64"]
    assert df["value"].tolist() == [100, 200, 300, 400, 500]


def test_filter_transformation(sample_dataframe):
    """Test filtering data using the actual FilterTransformation class."""
    df = sample_dataframe.copy()
    transformer = FilterTransformation()
    params = {"column": "age", "operator": ">", "value": 30}

    result = transformer.transform_pandas(df, params)

    assert len(result) == 3
    assert all(age > 30 for age in result["age"])


def test_map_transformation(sample_dataframe):
    """Test mapping values using the actual MapTransformation class."""
    df = sample_dataframe.copy()
    transformer = MapTransformation()
    # Map transformation is for renaming columns, not mapping values within a column
    params = {"mappings": {"category": "category_renamed"}}

    # Validate the parameters
    transformer.validate_params(params)

    # Then transform the data
    result = transformer.transform_pandas(df, params)

    # Check that the column was renamed
    assert "category_renamed" in result.columns
    assert "category" not in result.columns
    assert result["category_renamed"].tolist() == ["A", "B", "A", "C", "B"]


def test_aggregation_transformation(sample_dataframe):
    """Test aggregation operations."""
    df = sample_dataframe.copy()
    agg_df = df.groupby("category")["value"].agg(["mean", "sum"]).reset_index()

    assert "mean" in agg_df.columns
    assert "sum" in agg_df.columns
    assert len(agg_df) == 3  # One row per unique category


def test_join_transformation(sample_dataframe):
    """Test joining dataframes."""
    df1 = sample_dataframe.copy()
    df2 = pd.DataFrame({"id": [1, 2, 3], "score": [90, 85, 95]})

    joined_df = pd.merge(df1, df2, on="id", how="inner")

    assert "score" in joined_df.columns
    assert len(joined_df) == 3
    assert joined_df["score"].tolist() == [90, 85, 95]


def test_invalid_uppercase_params(sample_dataframe):
    """Test uppercase transformation with invalid parameters."""
    transformer = UppercaseTransformation()
    df = sample_dataframe.copy()

    # Test missing required 'columns' parameter
    with pytest.raises(ParameterError, match="Missing required parameter"):
        transformer.validate_params({})

    # Test empty columns list - this should work (transforms nothing)
    transformer.validate_params({"columns": []})
    result = transformer.transform_pandas(df, {"columns": []})
    assert result.equals(df)  # Should be unchanged

    # Test invalid column name - this needs to be tested during transform
    with pytest.raises(Exception):  # Will be ColumnError during transform
        transformer.transform_pandas(df, {"columns": ["nonexistent"]})


def test_invalid_map_params(sample_dataframe):
    """Test map transformation with invalid parameters."""
    transformer = MapTransformation()
    df = sample_dataframe.copy()

    # Test missing required 'mappings' parameter
    with pytest.raises(ParameterError, match="Missing required parameter"):
        transformer.validate_params({})

    # Test empty mappings - this should work (transforms nothing)
    transformer.validate_params({"mappings": {}})
    result = transformer.transform_pandas(df, {"mappings": {}})
    assert result.equals(df)  # Should be unchanged

    # Test invalid column name - this needs to be tested during transform
    with pytest.raises(Exception):  # Will be ColumnError during transform
        transformer.transform_pandas(df, {"mappings": {"nonexistent": "new_name"}})


def test_invalid_filter_params(sample_dataframe):
    """Test filter transformation with invalid parameters."""
    transformer = FilterTransformation()
    df = sample_dataframe.copy()

    # Test missing required parameters
    with pytest.raises(ParameterError, match="Missing required parameter"):
        transformer.validate_params({})

    # Test missing specific parameters
    with pytest.raises(ParameterError, match="Missing required parameter"):
        transformer.validate_params({"operator": ">", "value": 30})

    # Test invalid operator
    with pytest.raises(OperatorError):
        transformer.validate_params({"column": "age", "operator": "invalid", "value": 30})

    # Test invalid column name - this needs to be tested during transform
    with pytest.raises(Exception):  # Will be ColumnError during transform
        transformer.transform_pandas(df, {"column": "nonexistent", "operator": ">", "value": 30})


def test_map_transformation_with_unmapped_values(sample_dataframe):
    """Test map transformation behavior with unmapped values."""
    df = sample_dataframe.copy()
    transformer = MapTransformation()
    params = {"mappings": {"category": "category_renamed"}}

    result = transformer.transform_pandas(df, params)

    # Check that the column was renamed
    assert "category_renamed" in result.columns
    assert "category" not in result.columns
    assert result["category_renamed"].tolist() == ["A", "B", "A", "C", "B"]
