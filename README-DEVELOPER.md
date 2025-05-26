# Developer Guide - Mini Data Transformer

This guide provides detailed instructions for developers who want to set up, run, and contribute to the Mini Data Transformer project.

## Prerequisites

- **Python**: 3.11 or higher
- **Docker**: For containerized deployment (optional)

## Project Structure

```
mini-data-transformer/
├── app/                          # Main application package
│   ├── api/                      # API endpoints and routing
│   │   └── v1/                   # API version 1
│   │       ├── auth.py           # Authentication endpoints
│   │       └── transform.py      # Transformation endpoints
│   ├── core/                     # Core business logic
│   │   ├── auth.py               # Authentication core logic
│   │   └── registry.py           # Transformation registry
│   ├── models/                   # Data models
│   ├── schemas/                  # Pydantic schemas for API
│   ├── services/                 # Business services
│   │   ├── data_loader.py        # Data loading utilities
│   │   ├── parser.py             # Pipeline parsing
│   │   └── transformer.py        # Main transformation engine
│   ├── transformations/          # Transformation implementations
│   │   ├── base.py               # Base transformation class
│   │   ├── filter.py             # Filter transformation
│   │   ├── map.py                # Map/rename transformation
│   │   └── uppercase.py          # Uppercase transformation
│   ├── utils/                    # Utility modules
│   │   ├── logger.py             # Logging utilities
│   │   └── progress.py           # Progress tracking
│   ├── constants.py              # Application constants
│   ├── exceptions.py             # Custom exceptions
│   └── main.py                   # FastAPI application entry point
├── config/                       # Configuration files
│   └── settings.py               # Application settings
├── data/                         # Sample data files
├── tests/                        # Test suite
├── docker-compose.yml            # Docker composition
├── Dockerfile                    # Container definition
├── Makefile                      # Development commands
├── requirements.txt              # Python dependencies
└── test_transform.py             # API usage example
```

## Development Setup

### 1. Environment Setup

**Clone the repository:**
```bash
git clone <repository-url>
cd mini-data-transformer
```

**Set up virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

**Using Make (recommended):**
```bash
make dep
```

**Manual installation:**
```bash
pip install uv
uv pip install -r requirements.txt
```

### 3. Run the Application

**Development server with auto-reload:**
```bash
make run
```

**Manual startup:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The application will start on `http://localhost:8000`

## Makefile Commands

The project includes a Makefile with common development tasks:

```bash
# Show available commands
make help

# Install dependencies
make dep

# Run tests
make test

# Start the development server
make run

# Fix code formatting and imports
make lint-fix
```

## Docker Setup

### Development with Docker

**Build and run with docker-compose:**
```bash
docker-compose up --build
```

**Run in detached mode:**
```bash
docker-compose up -d
```

**Stop the services:**
```bash
docker-compose down
```

### Docker Features

- **Hot reload**: Code changes are reflected immediately
- **Volume mapping**: Local code is mounted into the container
- **Health checks**: Built-in health monitoring
- **Data persistence**: Data directory is mapped for file access

## Testing

### Running Tests

**Run all tests:**
```bash
make test
```

**Run specific test file:**
```bash
pytest tests/test_transformations.py -v
```

**Run with coverage:**
```bash
pytest tests/ --cov=app --cov-report=html
```

### Test Structure

- `tests/conftest.py` - Test configuration and fixtures
- `tests/test_transformations.py` - Transformation logic tests
- `tests/test_data_loader.py` - Data loading tests
- `tests/test_validation.py` - Validation tests

### API Testing

Use the provided `test_transform.py` for end-to-end API testing:

```bash
# Ensure the server is running first
make run

# In another terminal
python test_transform.py
```

## Code Quality

### Linting and Formatting

**Auto-fix formatting issues:**
```bash
make lint-fix
```

**Manual commands:**
```bash
# Format code with ruff
ruff format . --line-length 120

# Sort imports with isort
isort .

# Check for linting issues
ruff check .
```

### Code Standards

- **Line length**: Maximum 120 characters
- **Import sorting**: Automated with isort
- **Type hints**: Encouraged for all functions
- **Docstrings**: Required for all public methods
- **Error handling**: Use custom exceptions from `app.exceptions`

## Architecture Overview

### Core Components

1. **API Layer** (`app/api/`): FastAPI routers and endpoints
2. **Service Layer** (`app/services/`): Business logic and data processing
3. **Core Layer** (`app/core/`): Authentication and transformation registry
4. **Models Layer** (`app/models/`): Data models and schemas
5. **Transformations** (`app/transformations/`): Pluggable transformation implementations

### Key Design Patterns

- **Registry Pattern**: For managing available transformations
- **Strategy Pattern**: For different processing engines (pandas/Dask)
- **Factory Pattern**: For creating transformation instances
- **Observer Pattern**: For progress tracking

## Adding New Transformations

### 1. Create Transformation Class

Create a new file in `app/transformations/`:

```python
from typing import Any, Dict
import pandas as pd
from app.transformations.base import BaseTransformation

class MyTransformation(BaseTransformation):
    @property
    def name(self) -> str:
        return "my_transformation"
    
    def validate_params(self, params: Dict[str, Any]) -> None:
        # Validate transformation parameters
        self.validate_required_params(params, {"required_param"})
    
    def transform_pandas(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        # Implement pandas-specific transformation
        return data
    
    def transform_dask(self, data: "dd.DataFrame", params: Dict[str, Any]) -> "dd.DataFrame":
        # Implement Dask-specific transformation (optional)
        return data
```

### 2. Register Transformation

Add the transformation to the registry in `app/main.py`:

```python
from app.transformations.my_transformation import MyTransformation

# In the lifespan function
TransformationRegistry.register(MyTransformation)
```

### 3. Update Schema Validation

Add the new transformation name to `app/schemas/transformation.py`:

```python
def validate_name(cls, v):
    valid_names = {"uppercase", "map", "filter", "my_transformation"}
    # ...
```

### 4. Add Tests

Create tests in `tests/test_transformations.py`:

```python
def test_my_transformation(sample_dataframe):
    transformer = MyTransformation()
    params = {"required_param": "value"}
    
    result = transformer.transform_pandas(sample_dataframe, params)
    # Add assertions
```

## Configuration

### Environment Variables

The application supports configuration through environment variables:

- `ENVIRONMENT`: Development/production mode
- `PYTHONPATH`: Python path configuration
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Settings

Configuration is managed in `config/settings.py`:

- API metadata (title, version, description)
- CORS settings
- Database configuration (if applicable)
- Processing engine preferences

## Performance Optimization

### Engine Selection

The system automatically chooses the appropriate processing engine:

- **Pandas**: For smaller datasets (< 50MB)
- **Dask**: For larger datasets requiring distributed processing

### Memory Management

- Streaming data processing for large files
- Pagination to limit memory usage
- Garbage collection between transformations
- Progress tracking to monitor resource usage

## Debugging

### Logging

The application uses structured logging:

```python
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
logger.info("Processing started", extra={"rows": 1000})
```

### Development Tools

- **FastAPI automatic docs**: `http://localhost:8000/docs`
- **Health check endpoint**: `http://localhost:8000/api/v1/heartbeat`
- **Detailed error responses**: Full stack traces in development mode

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure PYTHONPATH is set correctly
2. **Port conflicts**: Change port in docker-compose.yml or Makefile
3. **Permission errors**: Check file permissions in data directory
4. **Memory issues**: Use Dask engine for large datasets

### Error Codes

- `400`: Bad request (invalid pipeline, missing parameters)
- `401`: Unauthorized (invalid or missing authentication)
- `404`: Not found (file not found, endpoint not found)
- `500`: Internal server error (transformation failures, system errors)

## Contributing

### Development Workflow

1. Create a feature branch
2. Make changes and add tests
3. Run the test suite: `make test`
4. Fix formatting: `make lint-fix`
5. Submit a pull request

### Code Review Checklist

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Error handling is appropriate
- [ ] Performance impact is considered

## Deployment

### Production Considerations

- Use environment variables for configuration
- Set up proper logging and monitoring
- Configure CORS for your domain
- Use a production WSGI server (e.g., Gunicorn)
- Set up SSL/TLS termination
- Configure authentication with secure secrets

### Docker Production

```dockerfile
# Use multi-stage build for smaller image
FROM python:3.11-slim AS production

# Copy only necessary files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY config/ ./config/

# Run with Gunicorn
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

## Support

For issues and questions:

1. Check the logs: `docker-compose logs app`
2. Review the API documentation: `http://localhost:8000/docs`
3. Run the test suite to verify setup: `make test`
4. Check this developer guide for common solutions
