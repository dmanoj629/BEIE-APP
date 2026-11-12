.PHONY: help check test lint run run-app clean

help:
	@echo "BEIE — Bharat Economic Intelligence Engine"
	@echo "Commands:"
	@echo "  make check      - Run linter and tests"
	@echo "  make test       - Run all pytest suites"
	@echo "  make lint       - Run ruff linter"
	@echo "  make run-app    - Launch Streamlit application"

check: lint test

lint:
	python -m ruff check .

test:
	python -m pytest tests/ -v

run-app:
	python -m streamlit run app/streamlit_app.py --server.port=8501
