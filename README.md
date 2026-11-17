# Agentic Coding Template

Built for Claude Code.

## Structure
```
- README.md
- CLAUDE.md            instructions, style, rules
- Makefile
- scripts
    - comment-budget.py
    - doc-lint.py
- .claude
    - settings.json
    - commands/
        - design.md
        - execute.md
        - audit.md
        - ref.md
        - deslop.md
- docs
    - README.md
    - issues/
    - spec/
        - _example-api.yaml
        - _example-returns.yaml
        - documentation.yaml
    - tasks/
        - README.md
        - _example.yaml
        - backlog/
        - next/
        - progress/
        - done/
```

## Flow
1. `/design` a task with the user. Save it into `docs/tasks/next/`.
2. `/execute` the task. Move it into `docs/tasks/progress/`.
3. `/audit` the work. Write the findings into the same task file.
4. Fix small findings in the same session. For a large finding, open a new task.
5. Move the task into `docs/tasks/done/`.

Split a large task into phases in one file, or into several files linked by `after`.

## Documents
- One YAML file per domain. Eight keys: domain, purpose, scope, design, rules, limits, issues, references.
- `docs/spec/` holds one system document per domain, product and technical alike. The architecture and the documentation rules are domains too.
- `docs/spec/<domain>.rationale.yaml` holds the idea, invariants and decisions of a domain, each decision with its rejected options.
- `docs/issues/` holds free markdown: `.rfc.md`, `.audit.md`, `.issue.md`.
- One YAML file per task. Eleven keys, `docs/tasks/_example.yaml` gives the order.
- `docs/spec/documentation.yaml` states the schema and the rules.
- A rule has no id. Another document states the rule in its own words.

## Lint
- `make lint` runs `scripts/comment-budget.py` and `scripts/doc-lint.py`.
- Comment budget: file warn 15 %, fail 20 % of characters. Blocks warn over 2 lines, fail over 4. Tree warn 13 %, fail 15 %. Covers py, ts, tsx, js, jsx, rs and md.
- Document lint: schema, key order, sentence length, banned modals, citation keys, rationale keys, repeated YAML keys.
- `--strict` fails on a warning. The repository ships no pre-commit hook. Add one that runs `make lint`.
- `/deslop` rewrites docs to the style. Facts, numbers, sources and code stay unchanged.

## Setup
1. Write CLAUDE.md for the project. Fill the `<project>` block.
2. Run Claude Code with `--system-prompt "-"` to drop the default prompt.
3. Add the project linters to `make lint`, for example ruff, eslint, clippy. One target serves the hook and the agents.
4. Write one system document per domain into `docs/spec/`. Use `/ref` on an existing product or on existing code.
5. Write `docs/spec/architecture.yaml`. It spans the domains and names the seams.
6. Work through the flow above.

## Notes
- After `/audit`, ask the model whether it reviewed the whole scope. It stops early.
- A large task needs several `/execute` and `/audit` sessions.
- Two agents on one repo need separate branches or separate worktrees.
