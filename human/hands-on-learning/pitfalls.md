# Common pitfalls

- **No commit SHA**: record the repo SHA (and any wheel version) or your results won’t be reproducible.
- **No minimal smoke**: don’t start with “full server benchmark”; first prove you can run *anything* end-to-end.
- **Unverifiable claims**: every claim in `reports/report.md` must link to evidence under `results/` (log snippet, trace, or metrics file).
- **Missing environment evidence**: “A100 + CUDA 12” without `nvidia-smi`/driver/tool versions is not evidence.
- **Changing multiple variables at once**: matrix rows should isolate one change (seq len, batch, dtype, kv mode) so you can interpret deltas.
- **No baselines**: “fast/slow” without a baseline (or a known-good config) is meaningless.
- **Mixing clone vs install**: record whether you ran local source or an installed wheel; they can differ.
- **Profiling too early**: profiling a failing run wastes time; capture the failure first, then unblock, then profile.
- **Overfitting to one run**: single datapoints lie; rerun critical measurements or capture variability.
- **Skipping unblock plan on failure**: if a run fails, the report must include the full error and a concrete unblock path.
