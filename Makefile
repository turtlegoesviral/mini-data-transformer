# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make dep      - Install dependencies"
	@echo "  make test     - Run tests"
	@echo "  make run      - Run the application"
	@echo "  make lint-fix - Fix linting issues using ruff and isort"

# Install dependencies
.PHONY: dep
dep:
	pip install uv
	uv pip install -r requirements.txt

# Run tests
.PHONY: test
test:
	pytest tests/ -v

# Run the application
.PHONY: run
run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Fix linting issues
.PHONY: lint-fix
lint-fix:
	ruff format . --line-length 120
	isort .