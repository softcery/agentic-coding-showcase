#!/usr/bin/env -S uv run --with pyyaml python
"""Lint system documents and task documents. Exit 1 on any finding."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

SPEC_DIR = "docs/spec"
DOC_DIRS = (SPEC_DIR,)
TASK_DIR = "docs/tasks"
KEYS = ["domain", "purpose", "scope", "design", "rules", "limits", "issues", "references"]
TASK_KEYS = [
    "id",
    "title",
    "after",
    "purpose",
    "scope",
    "design",
    "acceptance",
    "steps",
    "limits",
    "results",
    "references",
]
PART_KEYS = {"part", "does", "cite"}
RATIONALE_KEYS = ["domain", "idea", "invariants", "decisions", "tests", "prior_art", "risks"]
RATIONALE_REQUIRED = {"domain", "idea", "decisions"}
# Required and optional keys of each item of a rationale list.
RATIONALE_ITEMS = {
    "decisions": ({"decision", "chosen", "rejected"}, {"sources"}),
    "tests": ({"test", "found"}, {"sources"}),
    "prior_art": ({"product", "confirms"}, {"warns", "sources"}),
    "risks": ({"risk", "effect"}, set()),
}
REJECTED_KEYS = {"option", "reason"}
FINDING_KEYS = {"text", "evidence"}
PROCEDURAL_MAX = 20
DESCRIPTIVE_MAX = 25
BANNED = re.compile(r"\b(should|would|may|might|could|e\.g\.|i\.e\.|etc\.?)\b", re.I)
SENTENCE = re.compile(r"(?<=[.!?])\s+")
YEAR = re.compile(r"\b(19|20)\d\d\b")


def main() -> None:
    root = Path.cwd()
    findings: list[str] = []
    for name in DOC_DIRS:
        folder = root / name
        if not folder.is_dir():
            findings.append(f"{folder}: document folder is absent, expected a directory")
            continue
        domains: dict[str, Path] = {}
        for path in sorted(folder.iterdir()):
            if path.name.startswith("."):
                continue
            if path.name.endswith(".rationale.yaml"):
                lint_rationale(path, findings)
            elif path.suffix == ".yaml":
                document = lint_document(path, findings)
                check_domain(path, (document or {}).get("domain"), domains, findings)
            else:
                findings.append(f"{path}: only .yaml files are permitted here")
    for path in sorted((root / TASK_DIR).rglob("*.yaml")):
        lint_task(path, findings)
    for line in findings:
        print(line)
    print(f"{len(findings)} findings")
    sys.exit(1 if findings else 0)


def lint_document(path: Path, out: list[str]) -> dict | None:
    data = load(path, out)
    if not data:
        return None
    if list(data) != KEYS:
        out.append(f"{path}: keys must be {', '.join(KEYS)} in order")
        return None
    if data["domain"] != path.stem and not path.stem.startswith("_"):
        out.append(f"{path}: domain must equal file stem")
    check_text(f"{path}: purpose", data["purpose"], DESCRIPTIVE_MAX, out, sentences=1)
    check_text(f"{path}: scope", data["scope"], DESCRIPTIVE_MAX, out, sentences=2)
    cited = check_design(path, data, out)
    check_rules(path, data, out)
    for i, limit in enumerate(data["limits"]):
        check_text(f"{path}: limits[{i}]", limit, DESCRIPTIVE_MAX, out)
    check_findings(path, "issues", data["issues"], out)
    refs = check_references(path, data["references"], out)
    for key in sorted(cited - refs):
        out.append(f"{path}: cite {key} not in references")
    for key in sorted(refs - cited):
        out.append(f"{path}: reference {key} not cited")
    return data


def lint_rationale(path: Path, out: list[str]) -> None:
    data = load(path, out)
    if not data:
        return
    keys = list(data)
    if keys != [key for key in RATIONALE_KEYS if key in data] or not RATIONALE_REQUIRED <= set(keys) or not set(keys) <= set(RATIONALE_KEYS):
        out.append(f"{path}: keys must be {', '.join(RATIONALE_KEYS)} in order, with domain, idea and decisions")
        return
    if data["domain"] != path.name.removesuffix(".rationale.yaml"):
        out.append(f"{path}: domain must equal file stem")
    for i, invariant in enumerate(data.get("invariants", [])):
        if not isinstance(invariant, str):
            out.append(f"{path}: invariants[{i}]: invariant must be a sentence, with no id")
    for key, (required, optional) in RATIONALE_ITEMS.items():
        for i, item in enumerate(data.get(key, [])):
            if not isinstance(item, dict) or not required <= set(item) <= required | optional:
                out.append(f"{path}: {key}[{i}]: keys must be {', '.join(sorted(required))}, optional {', '.join(sorted(optional)) or 'none'}")
            elif key == "decisions":
                for j, option in enumerate(item["rejected"]):
                    if not isinstance(option, dict) or set(option) != REJECTED_KEYS:
                        out.append(f"{path}: decisions[{i}].rejected[{j}]: keys must be option, reason")


def lint_task(path: Path, out: list[str]) -> None:
    data = load(path, out)
    if not data:
        return
    if list(data) != TASK_KEYS:
        out.append(f"{path}: keys must be {', '.join(TASK_KEYS)} in order")
        return
    if not path.stem.startswith("_") and not path.stem.startswith(str(data["id"]) + "-"):
        out.append(f"{path}: file stem must start with id")
    if not isinstance(data["after"], list):
        out.append(f"{path}: after must be a list")
    check_text(f"{path}: purpose", data["purpose"], DESCRIPTIVE_MAX, out, sentences=1)
    check_text(f"{path}: scope", data["scope"], DESCRIPTIVE_MAX, out, sentences=2)
    cited = check_design(path, data, out)
    for key, limit in (("acceptance", DESCRIPTIVE_MAX), ("steps", PROCEDURAL_MAX), ("limits", DESCRIPTIVE_MAX)):
        for i, text in enumerate(data[key]):
            check_text(f"{path}: {key}[{i}]", text, limit, out)
    check_findings(path, "results", data["results"], out)
    check_task_references(path, data, cited, out)


def check_domain(path: Path, domain: object, seen: dict[str, Path], out: list[str]) -> None:
    if not isinstance(domain, str):
        return
    if domain in seen:
        out.append(f"{path}: domain {domain} already declared by {seen[domain]}")
    seen[domain] = path


def check_design(path: Path, data: dict, out: list[str]) -> set[str]:
    cited: set[str] = set()
    for i, part in enumerate(data["design"]):
        where = f"{path}: design[{i}]"
        if not isinstance(part, dict) or not {"part", "does"} <= set(part) <= PART_KEYS:
            out.append(f"{where}: keys must be part, does, optional cite")
            continue
        check_text(f"{where} {part['part']}", part["does"], DESCRIPTIVE_MAX, out)
        cited |= set(part.get("cite", []))
    return cited


def check_rules(path: Path, data: dict, out: list[str]) -> None:
    for i, rule in enumerate(data["rules"]):
        where = f"{path}: rules[{i}]"
        if not isinstance(rule, str):
            out.append(f"{where}: rule must be a string")
            continue
        check_text(where, rule, PROCEDURAL_MAX, out)


def check_findings(path: Path, key: str, entries: list, out: list[str]) -> None:
    for i, entry in enumerate(entries):
        where = f"{path}: {key}[{i}]"
        if not isinstance(entry, dict) or "text" not in entry or not set(entry) <= FINDING_KEYS:
            out.append(f"{where}: keys must be text, optional evidence")
            continue
        check_text(where, entry["text"], DESCRIPTIVE_MAX, out)


def check_references(path: Path, refs: dict | None, out: list[str]) -> set[str]:
    for key, line in (refs or {}).items():
        if not isinstance(line, str) or not YEAR.search(line):
            out.append(f"{path}: reference {key} must have a four-digit year")
    return set(refs or {})


# cite resolves in own map or in domain document; own map holds keys the domain lacks
def check_task_references(path: Path, data: dict, cited: set[str], out: list[str]) -> None:
    own = check_references(path, data["references"], out)
    domain_path = domain_document(path, str(data["id"]))
    domain = yaml.safe_load(domain_path.read_text()) if domain_path.is_file() else None
    domain_refs = set((domain.get("references") if isinstance(domain, dict) else None) or {})
    for key in sorted(cited - own - domain_refs):
        out.append(f"{path}: cite {key} not in references or {domain_path.name}")
    for key in sorted(own - cited):
        out.append(f"{path}: reference {key} not cited")
    for key in sorted(own & domain_refs):
        out.append(f"{path}: reference {key} duplicates {domain_path.name}")


def domain_document(path: Path, task_id: str) -> Path:
    root = next((p.parent for p in path.parents if p.name == "docs"), path.parent)
    matches = [
        candidate
        for candidate in (root / SPEC_DIR).glob("*.yaml")
        if task_id == candidate.stem or task_id.startswith(candidate.stem + "-")
    ]
    default = root / SPEC_DIR / f"{task_id.split('-')[0]}.yaml"
    return max(matches, key=lambda p: len(p.stem), default=default)


def check_text(
    where: str, text: object, limit: int, out: list[str], sentences: int | None = None
) -> None:
    if not isinstance(text, str) or not text.strip():
        out.append(f"{where}: text must be a non-empty string")
        return
    parts = [s for s in SENTENCE.split(text.strip()) if s]
    if sentences is not None and len(parts) != sentences:
        out.append(f"{where}: {sentences} sentence(s) required, found {len(parts)}")
    for sentence in parts:
        words = len(sentence.split())
        if words > limit:
            out.append(f"{where}: {words} words, limit {limit}: {sentence[:60]}")
        if not sentence.rstrip().endswith("."):
            out.append(f"{where}: sentence must end with a full stop: {sentence[:60]}")
    for match in BANNED.finditer(text):
        out.append(f"{where}: banned word {match.group(0)}")


class UniqueKeyLoader(yaml.SafeLoader):
    """Refuses a repeated key in a map, which PyYAML takes as the last value."""

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict:
        keys = [self.construct_object(key, deep=deep) for key, _ in node.value]
        for key in {key for key in keys if keys.count(key) > 1}:
            raise yaml.constructor.ConstructorError(None, None, f"repeated key {key}", node.start_mark)
        return super().construct_mapping(node, deep)


def load(path: Path, out: list[str]) -> dict | None:
    try:
        data = yaml.load(path.read_text(), Loader=UniqueKeyLoader)
    except yaml.YAMLError as err:
        out.append(f"{path}: yaml error: {err}")
        return None
    if not isinstance(data, dict):
        out.append(f"{path}: top level must be a map")
        return None
    return data


if __name__ == "__main__":
    main()
