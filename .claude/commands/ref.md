---
description: Distill a system into a YAML document under ./docs/refs/ or ./docs/spec/. Design and rules only. No code dumps, no plan refs, no obvious stuff.
---

Write the document for the system: $ARGUMENTS. One YAML file that locks the design, the rules and the limits. A document is a fence, not a tour. You're the ingenious software architect with IQ of 180.

---

## Protocol

### 1. Restate

Restate the system and its boundary. In / out. Confirm before §2.

### 2. Review documents

Read `./docs/refs/documentation.yaml`, `dictionary.yaml`, `./docs/spec/_example-api.yaml`, every overlapping document. No duplication. No contradiction. Extend an existing document or carve a fresh one. State the choice.

### 3. Map terrain

Map the system. Read load-bearing files only. Note: boundary, public surface, event and effect shape, who reads, who writes, who folds.

### 4. Distill design

One part per stage, in data flow order. Each `does` states what the part calculates and names its method. Signature level, not body level. Name concepts, not code symbols.

### 5. Distill rules

Each rule = one property held by types or one chokepoint. Give it an id, `R1` upward. "By convention" → move it to `limits`. A rule must answer: what breaks on violation.

### 6. Limits and issues

`limits` = cases the target system does not handle. `issues` = gaps between this design and the code. A number in an issue carries an `evidence` path. Check the path exists.

### 7. Cut

Kill: obvious-from-code, function-body restatement, plan and date and status refs, empty adjectives, examples that pin no rule. If the line prevents no mistake, cut it.

### 8. Write

`./docs/spec/<domain>.yaml` for one system, product or technical. `./docs/refs/<name>.yaml` for an overarching document that spans domains. Eight keys in order. `domain` matches the file stem. Every text field follows the CLAUDE.md style block and `dictionary.yaml`.

### 9. Check

Run `make lint`. Fix every finding. Never widen a sentence past the word limit.

### 10. Receipt

Document path. Parts, rules, limits, issues counted. Terms the dictionary lacks, proposed to the operator. Violations found in code, listed as follow-up tasks, not fixed here.

---

Fence not tour.
If it prevents no mistake, cut.
No plan refs, no dates, no statuses.
Unmeasured claim never lands in a document.
