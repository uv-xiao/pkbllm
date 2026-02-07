# Serving (inference)

Inference and serving frameworks and systems.

## <TABLE>
<!-- PKBLLM_TABLE_START -->
| Path | Type | Description |
| --- | --- | --- |
| `llama-cpp/` | skill | Runs LLM inference on CPU, Apple Silicon, and consumer GPUs without NVIDIA hardware. Use for edge deployment, M1/M2/M3 Macs, AMD/Intel GPUs, or when CUDA is unavailable. Supports GGUF quantization (1.5-8 bit) for reduced memory and 4-10× speedup vs PyTorch on CPU. |
| `sglang/` | skill | Fast structured generation and serving for LLMs with RadixAttention prefix caching. Use for JSON/regex outputs, constrained decoding, agentic workflows with tool calls, or when you need 5× faster inference than vLLM with prefix sharing. Powers 300,000+ GPUs at xAI, AMD, NVIDIA, and LinkedIn. |
| `tensorrt-llm/` | skill | Optimizes LLM inference with NVIDIA TensorRT for maximum throughput and lowest latency. Use for production deployment on NVIDIA GPUs (A100/H100), when you need 10-100x faster inference than PyTorch, or for serving models with quantization (FP8/INT4), in-flight batching, and multi-GPU scaling. |
| `vllm/` | skill | Serves LLMs with high throughput using vLLM's PagedAttention and continuous batching. Use when deploying production LLM APIs, optimizing inference latency/throughput, or serving models with limited GPU memory. Supports OpenAI-compatible endpoints, quantization (GPTQ/AWQ/FP8), and tensor parallelism. |
<!-- PKBLLM_TABLE_END -->
