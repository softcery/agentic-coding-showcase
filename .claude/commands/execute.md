---
description: Execute a plan in full. Defer nothing without the user's approval.
---

Execute the plan: $ARGUMENTS. Execute all of it. Do not delegate. Do not defer a part unless the user agrees before you start.

1. Read the plan and the domain documents in `docs/spec/`.
2. Read the code that the plan touches.
3. If the plan is unclear, blocked or impossible, stop and ask one question.
4. Make a list of steps with the task tools.
5. Do the steps.
6. Read each change again. Run `make lint` and the tests. Fix bugs, code smells and departures from the docs.
7. Report the changed files and why, the plan items that are done or blocked, and the open checks. Write each outcome into the task `results`.
