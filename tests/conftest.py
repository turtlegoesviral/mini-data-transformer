from pathlib import Path

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["John", "Jane", "Bob", "Alice", "Charlie"],
            "age": [25, 30, 35, 40, 45],
            "value": [100, 200, 300, 400, 500],
            "category": ["A", "B", "A", "C", "B"],
        }
    )


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a temporary CSV file for testing."""
    df = pd.DataFrame({"id": [1, 2, 3], "name": ["John", "Jane", "Bob"], "value": [100, 200, 300]})
    file_path = tmp_path / "test_data.csv"
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def sample_json_file(tmp_path):
    """Create a temporary JSON file for testing."""
    data = {
        "records": [
            {"id": 1, "name": "John", "value": 100},
            {"id": 2, "name": "Jane", "value": 200},
            {"id": 3, "name": "Bob", "value": 300},
        ]
    }
    file_path = tmp_path / "test_data.json"
    with open(file_path, "w") as f:
        import json

        json.dump(data, f)
    return file_path
