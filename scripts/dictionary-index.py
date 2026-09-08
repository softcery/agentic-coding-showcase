#!/usr/bin/env -S uv run --with pyyaml python
"""Print dictionary terms grouped by source."""

import sys
from pathlib import Path

import yaml


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "dictionary.yaml")
    data = yaml.safe_load(path.read_text())
    groups: dict[str, list[str]] = {key: [] for key in data["sources"]}
    for term, entry in data["terms"].items():
        key = entry["src"].split()[0]
        groups.setdefault(key, []).append(term)
    for key, terms in groups.items():
        if terms:
            print(f"- {key}: {', '.join(terms)}")


if __name__ == "__main__":
    main()
