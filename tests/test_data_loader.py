from pathlib import Path

import pandas as pd
import pytest


def test_load_csv_file(sample_csv_file):
    """Test loading data from a CSV file."""
    df = pd.read_csv(sample_csv_file)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert list(df.columns) == ["id", "name", "value"]
    assert df["id"].tolist() == [1, 2, 3]


def test_load_json_file(sample_json_file):
    """Test loading data from a JSON file."""
    import json

    with open(sample_json_file, "r") as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert "records" in data
    assert len(data["records"]) == 3
    assert data["records"][0]["id"] == 1


def test_missing_file():
    """Test handling of missing file."""
    with pytest.raises(FileNotFoundError):
        pd.read_csv("nonexistent_file.csv")
