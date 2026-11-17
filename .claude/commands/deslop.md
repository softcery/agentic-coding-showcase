---
description: Remove slop from docs. Style only. Facts, numbers and sources stay.
---

Remove slop from: $ARGUMENTS. If no scope is given, use all the docs of the project. Change the style only. Do not change, remove or check facts.

1. State the files in scope. Get the user's confirmation.
2. Rewrite each doc from start to end, to the style block of `CLAUDE.md`.
   - Remove drama, opinion, metaphor, story, hedging, filler and comments on the text itself.
   - Remove AI patterns: "not X, it is Y", adverbs, code that "wants", "every" or "always" with no number, short punchy closing lines.
   - Keep facts, numbers, units, sources, code, commands and paths exactly. Do not add a number or a detail that the source does not give.
   - Keep the same facts in about half the characters.
   - If the structure tells a story, restructure it as a list of facts.
   - Do not swap a word for a synonym to pass a check.
   - In a YAML document, keep the keys and their order. Rewrite only the text.
3. Give the characters before and after for each file. Add no comment.

Example:
- Before: "The half second is real and it is silent, which is the part a listener judges. So the agent speaks a held line the moment the call goes out, and the search runs under it."
- After: "The search has 0.5 s of silence. The agent speaks a held line at the tool call, and the search runs under it."
