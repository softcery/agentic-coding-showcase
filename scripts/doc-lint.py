#!/usr/bin/env -S uv run --with pyyaml python
"""Lint system documents, task documents and the dictionary. Exit 1 on any finding."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

DOC_DIRS = ("docs/spec", "docs/refs")
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
RULE_KEYS = {"id", "text"}
FINDING_KEYS = {"text", "evidence"}
PROCEDURAL_MAX = 20
DESCRIPTIVE_MAX = 25
# evidence path shape. set it to the project's own, for example records/<hash>/<run>
EVIDENCE = re.compile(r"^[\w.][\w./-]*$")
BANNED = re.compile(r"\b(should|would|may|might|could|e\.g\.|i\.e\.|etc\.?)\b", re.I)
RULE_ID = re.compile(r"^[A-Z]+\d+$")
NUMBER = re.compile(r"\d")
SENTENCE = re.compile(r"(?<=[.!?])\s+")
YEAR = re.compile(r"\b(19|20)\d\d\b")


def main() -> None:
    root = Path.cwd()
    findings: list[str] = []
    lint_dictionary(root / "dictionary.yaml", findings)
    domains: dict[str, Path] = {}
    for name in DOC_DIRS:
        folder = root / name
        if not folder.is_dir():
            findings.append(f"{folder}: document folder is absent, expected a directory")
            continue
        for path in sorted(folder.iterdir()):
            if path.name.startswith("."):
                continue
            if path.suffix == ".yaml":
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


def lint_dictionary(path: Path, out: list[str]) -> None:
    data = load(path, out)
    if not data:
        return
    sources = data.get("sources", {})
    seen_project = False
    for term, entry in data.get("terms", {}).items():
        where = f"{path}: {term}"
        if set(entry) != {"def", "src"}:
            out.append(f"{where}: keys must be def, src")
            continue
        key = entry["src"].split()[0]
        if key not in sources:
            out.append(f"{where}: src {key} not in sources")
        if key == "project":
            seen_project = True
        elif seen_project:
            out.append(f"{where}: sourced term after a project term")
        check_text(where, entry["def"], DESCRIPTIVE_MAX, out, stop=False)


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
    seen: set[str] = set()
    for i, rule in enumerate(data["rules"]):
        where = f"{path}: rules[{i}]"
        if not isinstance(rule, dict) or set(rule) != RULE_KEYS:
            out.append(f"{where}: keys must be id, text")
            continue
        rule_id = str(rule["id"])
        if not RULE_ID.match(rule_id):
            out.append(f"{where}: id must match letters then digits, for example R1")
        if rule_id in seen:
            out.append(f"{where}: id {rule_id} is not unique in the file")
        seen.add(rule_id)
        check_text(f"{where} {rule_id}", rule["text"], PROCEDURAL_MAX, out)


def check_findings(path: Path, key: str, entries: list, out: list[str]) -> None:
    for i, entry in enumerate(entries):
        where = f"{path}: {key}[{i}]"
        if not isinstance(entry, dict) or "text" not in entry or not set(entry) <= FINDING_KEYS:
            out.append(f"{where}: keys must be text, optional evidence")
            continue
        check_text(where, entry["text"], DESCRIPTIVE_MAX, out)
        evidence = entry.get("evidence")
        if evidence is None and NUMBER.search(entry["text"]):
            out.append(f"{where}: text has a number, evidence required")
        if evidence is not None and not EVIDENCE.match(str(evidence)):
            out.append(f"{where}: evidence must be a repository path")


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
        for name in DOC_DIRS
        for candidate in (root / name).glob("*.yaml")
        if task_id == candidate.stem or task_id.startswith(candidate.stem + "-")
    ]
    default = root / DOC_DIRS[0] / f"{task_id.split('-')[0]}.yaml"
    return max(matches, key=lambda p: len(p.stem), default=default)


def check_text(
    where: str, text: object, limit: int, out: list[str], sentences: int | None = None, stop: bool = True
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
        if stop and not sentence.rstrip().endswith("."):
            out.append(f"{where}: sentence must end with a full stop: {sentence[:60]}")
    for match in BANNED.finditer(text):
        out.append(f"{where}: banned word {match.group(0)}")


def load(path: Path, out: list[str]) -> dict | None:
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as err:
        out.append(f"{path}: yaml error: {err}")
        return None
    if not isinstance(data, dict):
        out.append(f"{path}: top level must be a map")
        return None
    return data


if __name__ == "__main__":
    main()
