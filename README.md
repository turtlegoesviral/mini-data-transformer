# Mini Data Transformer

A mini data transformation API built with FastAPI that provides a flexible pipeline system for processing CSV data.
The system supports various transformations including filtering, mapping, and text operations with engines:
    - pandas
    - Dask (for large file, configurable via LARGE_FILE_THRESHOLD)

## Features

- **Flexible Pipeline System**: Chain multiple transformations in a single request
- **Authentication**: Secure user registration and JWT token-based authentication
- **Dual Processing Engines**: Support for both pandas (single-machine) and Dask (distributed) processing
- **Built-in Transformations**:
  - **Uppercase**: Convert string columns to uppercase
  - **Map**: Rename/map column names
  - **Filter**: Filter rows based on column conditions with various operators
- **Pagination**: Efficient handling of large datasets with built-in pagination
- **Performance Monitoring**: Built-in metrics and progress tracking
- **RESTful API**: Clean API design with automatic OpenAPI documentation

## Quick Start

### Prerequisites
- Python 3.11+ env

### Installation & Setup

1. **Install dependencies:**
   ```bash
   make dep
   ```

2. **Start the application:**
   ```bash
   make run
   ```

The API will be available at `http://localhost:8000`

### API Documentation
Once the application is running, visit:
- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

## Usage Example

Here's a complete example of how to use the Mini Data Transformer API:

### 1. User Registration and Authentication

```python
import requests

# Register a new user
response = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    json={
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com"
    }
)

# Login to get authentication token
response = requests.post(
    "http://localhost:8000/api/v1/auth/token",
    data={"username": "testuser", "password": "testpass123"}
)
token_data = response.json()
auth_token = f"{token_data['token_type']} {token_data['access_token']}"
```

### 2. Data Transformation

```python
import json

# Define your transformation pipeline
pipeline = {
    "input_path": "data/observations.csv",
    "transformations": [
        {
            "name": "uppercase",
            "params": {
                "columns": ["PATIENT", "ENCOUNTER", "DESCRIPTION"]
            }
        },
        {
            "name": "map",
            "params": {
                "mappings": {"VALUE": "VALUE_NUMERIC"}
            }
        },
        {
            "name": "filter",
            "params": {
                "column": "VALUE_NUMERIC",
                "operator": "==",
                "value": 1
            }
        }
    ]
}

# Send transformation request
response = requests.post(
    "http://localhost:8000/api/v1/transform",
    data={"pipeline": json.dumps(pipeline)},
    headers={"Authorization": auth_token}
)

result = response.json()
print(f"Total items: {result['total']}")
print(f"First few items:")
for item in result["items"][:5]:
    print(item)
```

### 3. Sample Data Format

The system expects CSV files with headers. Example data structure:

```csv
DATE,PATIENT,ENCOUNTER,CODE,DESCRIPTION,VALUE,UNITS,TYPE
2019-08-01,1ff7f10f-a204-4bb1-aa72-dd763fa99482,52051c30-c6c3-45fe-b5da-a790f1680e91,8302-2,Body Height,82.7,cm,numeric
2019-08-01,1ff7f10f-a204-4bb1-aa72-dd763fa99482,52051c30-c6c3-45fe-b5da-a790f1680e91,72514-3,Pain severity,2.0,{score},numeric
```

## Available Transformations

### Uppercase Transformation
Converts specified string columns to uppercase.
```json
{
    "name": "uppercase",
    "params": {
        "columns": ["COLUMN1", "COLUMN2"]
    }
}
```

### Map Transformation
Renames columns in the dataset.
```json
{
    "name": "map",
    "params": {
        "mappings": {
            "old_column_name": "new_column_name",
            "VALUE": "VALUE_NUMERIC"
        }
    }
}
```

### Filter Transformation
Filters rows based on column conditions.
```json
{
    "name": "filter",
    "params": {
        "column": "age",
        "operator": ">",
        "value": 30
    }
}
```

**Supported operators**: `==`, `!=`, `>`, `<`, `>=`, `<=`

## Response Format

All transformation responses follow this structure:

```json
{
    "items": [/* array of transformed data records */],
    "total": 1000,
    "page": 1,
    "size": 10,
    "pages": 100,
    "processing_time": 2.34,
    "engine": "dask",
    "timestamp": "2025-05-27T10:30:00Z"
}
```

## Experimenting

The project includes a comprehensive test example in `test_transform.py` that demonstrates:
- User registration and authentication
- Pipeline configuration
- API interaction
- Error handling

Run the test:
```bash
python test_transform.py
```

## Performance

- **Automatic Engine Selection**: The system automatically chooses between pandas and Dask based on data size
- **Memory Efficient**: Uses streaming and pagination for large datasets
- **Parallel Processing**: Dask support for distributed computing
- **Progress Tracking**: Built-in progress monitoring for long-running operations