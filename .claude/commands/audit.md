---
description: Audit a system on all fronts. Catch everything that could be more correct, beautiful, ingenious, simple. Verdict only. No edits.
---

Audit the system: $ARGUMENTS. Hunt every place it could be more correct, beautiful, ingenious, simple — every friction that makes future work harder. Rulebook is floor, not ceiling. Read-only. You're the ingenious software architect with IQ of 180.

---

## Protocol

### 1. Restate

Scope. Files / surface. Confirm before §2.

### 2. Anchor

Read `CLAUDE.md`, `dictionary.yaml`, `./docs/refs/`, the domain document in `./docs/spec/`, every document touching the system. No document = flag.

### 3. Map terrain

`rmap`. Read load-bearing files end-to-end.

### 4. Floor

Every rule in the domain document: held or violated. Cite the rule id and the code line.

### 5. Beyond

Hunt past the rulebook.
Anything that could be more correct, more beautiful, more ingenious, more simple, or easier to live with.
Type that should carry the rule. Concept that should die. Reuse missed. Footgun reachable. Recipe one step too long.
Cite line. One-phrase better shape.

Uncovered surface → judge from `CLAUDE.md` first principles, flag the missing document.

### 6. Rank

- 🔴 Bug / divergence.
- 🟠 Architecture violation.
- 🟡 Smell / friction.
- 🟢 Note.

`path:line — finding. fix.`

### 7. Verdict

One paragraph. Clean, drifting, rotten. Highest-leverage fix.

---

Read-only. `/design` and `/execute` fix.
Cite or strike. Rulebook is floor. Praise dies.
A measured finding carries an evidence path. Write it into the task `results`.
