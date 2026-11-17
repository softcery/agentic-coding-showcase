---
description: Design a change with the user. One question at a time. No code.
---

Design with the user: $ARGUMENTS. Keep each turn short. Ask one question at a time.

1. State the request and the unknowns. Get the user's confirmation.
2. Read the domain documents in `docs/spec/` and the code that the change touches.
3. Use an existing mechanism before you add a new one.
4. Give 2 or more options. For each, give the mechanism, the layers it touches, the effect on other parts and how it fails. Wait for the user.
5. Select one option by correctness, simplicity and reuse. Give a one-line reason against each other option. Get the user's confirmation.
6. Make the selected option smaller: remove each concept, type or name that it does not need.
7. Ask the open questions, one at a time.
8. Give the final design and the smallest slice to build first.

Do not write code. Do not edit files. Wait for the user to approve.
