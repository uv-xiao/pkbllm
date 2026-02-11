# Profiling

Hands-on learning is about “what happened and why”. Profiling is optional, but when you do it: capture enough context that another
person can interpret the trace.

## Tool selection

- `nsys`: timeline (CPU + CUDA), good for stalls, kernel launch patterns, comms
- `ncu`: kernel metrics, good for attention/GEMM micro-optimization questions
- `torch.profiler`: lowest-friction when Nsight is unavailable

## Nsight Systems (nsys) pattern

```bash
mkdir -p results/nsys
nsys profile -o results/nsys/run \
  --trace=cuda,nvtx,osrt \
  --cuda-memory-usage=true \
  --force-overwrite=true \
  python your_script.py {args...} |& tee results/nsys/stdout_stderr.log
```

Record in `reports/report.md`:

- what the timeline shows (prefill vs decode, kernel clusters, comms)
- any long gaps (CPU stalls, synchronization, memory alloc)

## Nsight Compute (ncu) pattern

Start small. Don’t profile an entire server.

```bash
mkdir -p results/ncu
ncu --set full --target-processes all -o results/ncu/run \
  python your_microbench.py {args...} |& tee results/ncu/stdout_stderr.log
```

Record:

- which kernels dominate,
- whether you’re compute-bound or memory-bound,
- and what changes when you vary batch/seq/KV length.

## Common pitfalls

- Profiling a whole server first (too much noise).
- Not pinning the run config (model, dtype, lengths).
- Comparing runs across different environments (different driver/toolkit).
