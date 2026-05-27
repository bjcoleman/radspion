.PHONY: test style default

default: test style
	@echo "All checks passed!"

test:
	pytest

style:
	ruff check src tests
	ruff format --check src tests
