# Docs

- `spec/` one YAML document per domain, product and technical alike. The architecture and the documentation rules are domains too. `<domain>.rationale.yaml` holds the rationale of a domain
- `tasks/` one YAML document per task, the work board
- `issues/` free markdown, no schema. The suffix gives the kind: `.rfc.md`, `.audit.md`, `.issue.md`

`spec/documentation.yaml` states the schema and the rules. `spec/_example-api.yaml`
and `spec/_example-returns.yaml` are the reference files. `make lint` runs
`scripts/doc-lint.py` over `spec/` and `tasks/`.
