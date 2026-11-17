---
description: Write the YAML document of a system in docs/spec. Design, rules and limits only.
---

Write the document of the system: $ARGUMENTS. One YAML file that states the design, the rules and the limits. Write only what prevents a mistake.

1. State the system and its boundary: what is in and what is out. Get the user's confirmation.
2. Read `docs/spec/documentation.yaml`, `docs/spec/_example-api.yaml` and each document that overlaps. Extend a document or start a new one, and say which. Do not repeat or contradict a document.
3. Read the main files. Find the boundary, the public surface, the data shapes, and who reads and who writes.
4. design: one part per stage, in data flow order. Each `does` states what the part calculates and its method. Name concepts, not code symbols.
5. rules: each rule is one property that a type or one chokepoint holds. Each rule states what breaks if code does not keep it. Put a convention in `limits`.
6. limits: the cases the system does not handle. issues: the gaps between the design and the code.
7. Remove what the code shows clearly, plans, dates, statuses, empty adjectives and examples that pin no rule.
8. Write `docs/spec/<domain>.yaml`, with the eight keys in order. `domain` is the file stem.
9. Run `make lint` and fix each finding.
10. Report the path and the count of parts, rules, limits and issues. List each code violation as a follow-up task. Do not fix it here.
