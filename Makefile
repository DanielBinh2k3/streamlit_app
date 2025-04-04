.PHONY: setup install clean run lint format test help venv dev-install check lock

# Python interpreter to use
PYTHON ?= python
VENV = .venv
STREAMLIT_APP = src/streamlit_app/app.py

# Check if we're on Windows
ifeq ($(OS),Windows_NT)
	VENV_BIN = $(VENV)\Scripts
	PYTHON_VENV = $(VENV_BIN)\python
	ACTIVATE = $(VENV_BIN)\activate
else
	VENV_BIN = $(VENV)/bin
	PYTHON_VENV = $(VENV_BIN)/python
	ACTIVATE = $(VENV_BIN)/activate
endif

help:
	@echo "Available commands:"
	@echo "  make setup         - Install uv if not installed and create virtual environment"
	@echo "  make venv          - Create virtual environment using uv"
	@echo "  make install       - Install dependencies using uv"
	@echo "  make dev-install   - Install development dependencies"
	@echo "  make run           - Run the Streamlit application"
	@echo "  make test          - Run tests"
	@echo "  make lock          - Update the lockfile"
	@echo "  make check         - Check if lockfile is up-to-date"
	@echo "  make clean         - Remove build artifacts and virtual environment"
	@echo "  make help          - Show this help message"

setup:
	$(PYTHON) -m pip install uv
	uv venv $(VENV)
	uv sync

venv:
	uv venv $(VENV)

install: venv
	uv sync

dev-install: install
	uv sync --extra dev

# Lock dependencies
lock:
	uv lock

# Check if lockfile is up to date
check:
	uv lock --check

run:
	cd src/streamlit_app && streamlit run app.py

test:
	uv run pytest -v --cov=src tests/

# Use Unix-style commands that work in Git Bash on Windows
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .ruff_cache
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Default target
.DEFAULT_GOAL := help
