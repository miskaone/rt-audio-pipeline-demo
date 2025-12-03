.PHONY: help install test lint run clean format check

# Default target
help:
	@echo "Available targets:"
	@echo "  install - Install dependencies"
	@echo "  test    - Run test suite"
	@echo "  lint    - Run linting checks"
	@echo "  format  - Format code with black"
	@echo "  check   - Run formatting and linting checks"
	@echo "  run     - Run the development server"
	@echo "  clean   - Clean up temporary files"
	@echo ""

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -e .

# Run test suite
test:
	python -m pytest -v

# Run linting checks
lint:
	flake8 app tests
	black --check app tests

# Format code
format:
	black app tests

# Run formatting and linting checks
check: format lint

# Run development server
run:
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Clean up temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ 2>/dev/null || true
