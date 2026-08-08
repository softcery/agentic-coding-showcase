.PHONY: lint

# comment budget + slop scan. --strict fails on warnings. pre-commit hook runs same.
lint:
	python3 scripts/comment-budget.py
