# Agentic Coding Template

Built for Claude Code.

## Structure
```
- README.md
- CLAUDE.md
- .claude
    - settings.json
    - commands/
        - design.md
        - execute.md
        - audit.md
        - ref.md
- docs
    - README.md
    - notes/
    - refs/
        - _example-architecture.md
    - spec/
        - _example-glossary.md
        - _example-returns.md
    - tasks/
      - README.md
      - _template.md
      - backlog/
      - todo/
      - next/
      - review/
      - done/
          - _example-amendment-tracker-names-the-actor.md
```

## Flow
1. `/design` a task, save into `./tasks/next`
   1. Can be broken into one `/design` session for product/business design and another separate `/design` session for architectural and technical planning.
2. `/execute` the task, move into `./tasks/review`.
   1. Can be broken down into multiple execution phases as part of the design phase (step 1 above).
3. `/review` the task, document the audit into the same task file.
   1. Then either fix in the same session if issues are minor, or repeat the flow (design -> execute) if issues justify this.

## Instructions
1. Populate or rewrite CLAUDE.md depending on the project.
   1. I suggest using Claude Code with `--system-prompt "-"` to disable the default Claude Code prompt. Works better IMO.
2. Document or design the business/product specification into `./docs/spec`.
   1. You could try using `/audit` or `/ref` for this purpose with existing products.
3. Document or design the system architecture and important technical aspects into `./docs/refs`.
   1. Use the helpful `/ref` command for documenting existing systems.
4. Use the design and development flow described above.

## Tips
1. Once Claude completes the `/audit`, ask it whether it reviewed everything, and if not, ask it to complete the audit, without compromises. Otherwise Claude is often lazy...
   1. Using Claude Code without default system instructions makes it less lasy, but it's still lasy.
2. Bigger tasks can be either split into phases in the same task file, or split into multiple tasks. Logically, bigger tasks need multiple separate `/execute` and `/audit` sessions to make sure everything is good.