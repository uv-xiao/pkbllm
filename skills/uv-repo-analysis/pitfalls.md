# Common pitfalls

- **Documenting the README instead of the code**: the “real” runtime loop is usually not in the README.
- **No file:line pointers**: without pointers, the report is not actionable.
- **Confusing prefill vs decode**: LLM performance work requires separating these phases.
- **Mixing wheel vs local clone**: record what you read and what you ran; they can differ.
- **Ignoring configuration surface**: many repos hide critical behavior behind env vars and CLI flags.
- **Missing commit/versions**: without a git SHA (and relevant package versions), “where is this in code?” becomes unanswerable.
- **Generic LLM boilerplate**: if you can’t point to the repo’s real KV-cache/scheduler/sampling code, don’t pretend.
- **No entrypoints**: failing to identify how to run (CLI/server/examples) forces the next engineer to rediscover basics.
- **Key components table too small**: <6 entries usually means you didn’t actually map the runtime.
