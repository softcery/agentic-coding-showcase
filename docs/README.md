# Docs

- `spec/` one YAML system document per domain, product and technical alike
- `refs/` the overarching documents, `architecture.yaml` and `documentation.yaml`
- `tasks/` one YAML document per task, the work board
- `notes/` free markdown, no schema

`refs/documentation.yaml` states the schema and the rules. `spec/_example-api.yaml`
and `spec/_example-returns.yaml` are the reference files. `make lint` runs
`scripts/doc-lint.py` over `spec/`, `refs/`, `tasks/` and `dictionary.yaml`.
