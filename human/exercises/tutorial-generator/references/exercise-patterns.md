# Exercise patterns

## Pattern: “read → run → modify → verify”

1) Point to a file:line where the behavior is implemented.
2) Provide a runnable example that demonstrates the current behavior.
3) Ask the reader to change one knob or input and observe a predicted effect.
4) Define “what counts as correct” (expected output shape, timing trend, error removed, etc.).

## Pattern: “debug a common failure”

1) Show the exact error message and a minimal reproducer command.
2) Ask the reader to identify the first relevant import/callsite in the stack trace.
3) Ask for an unblock step (install, env var, path fix).
4) Provide a post-fix check command.

