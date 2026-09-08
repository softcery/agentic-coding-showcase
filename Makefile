.PHONY: lint

# comment budget + slop scan, then document schema. --strict fails warnings.
lint:
	python3 scripts/comment-budget.py
	uv run --with pyyaml python scripts/doc-lint.py
