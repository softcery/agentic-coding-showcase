---
description: Audit a system. Find what can be more correct or simpler. Report only, no edits.
---

Audit the system: $ARGUMENTS. Do not edit code. `/design` and `/execute` make the fixes.

1. State the scope: the files and the surface. Get the user's confirmation.
2. Read `CLAUDE.md`, `docs/spec/architecture.yaml` and each domain document of the system. If the system has no document, record a finding.
3. Read the main files of the system from start to end.
4. For each rule in the domain document, state if the code keeps it. Quote the rule and give the code line.
5. Find what the rules do not cover: bugs, missed reuse, concepts to remove, rules that a type can hold, unsafe paths, extra steps.
6. Write each finding as `path:line: finding. fix.` Sort by severity: bug, architecture, friction, note.
7. Give the verdict in one paragraph: the state of the system and the fix with the most effect.
8. If a task file is in scope, write each finding into its `results`.
