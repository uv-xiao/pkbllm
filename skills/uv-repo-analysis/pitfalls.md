# Common pitfalls

- **Documenting the README instead of the code**: the “real” runtime loop is usually not in the README.
- **No file:line pointers**: without pointers, the report is not actionable.
- **Confusing prefill vs decode**: LLM performance work requires separating these phases.
- **Mixing wheel vs local clone**: record what you read and what you ran; they can differ.
- **Ignoring configuration surface**: many repos hide critical behavior behind env vars and CLI flags.
