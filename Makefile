.PHONY: test style default acceptance

default: test style
	@echo "All checks passed!"

test:
	.venv/bin/pytest

acceptance:
	.venv/bin/pytest tests/acceptance --no-cov

style:
	.venv/bin/ruff check src tests
	.venv/bin/ruff format --check src tests
