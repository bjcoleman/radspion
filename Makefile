.PHONY: test style default

default: test style
	@echo "All checks passed!"

test:
	.venv/bin/pytest

style:
	.venv/bin/ruff check src tests
	.venv/bin/ruff format --check src tests
