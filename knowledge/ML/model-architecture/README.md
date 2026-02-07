# Model architecture

Architectures and decoding techniques (including MoE and speculative decoding).

## <TABLE>
<!-- PKBLLM_TABLE_START -->
| Path | Type | Description |
| --- | --- | --- |
| `litgpt/` | skill | Implements and trains LLMs using Lightning AI's LitGPT with 20+ pretrained architectures (Llama, Gemma, Phi, Qwen, Mistral). Use when need clean model implementations, educational understanding of architectures, or production fine-tuning with LoRA/QLoRA. Single-file implementations, no abstraction layers. |
| `mamba/` | skill | State-space model with O(n) complexity vs Transformers' O(n²). 5× faster inference, million-token sequences, no KV cache. Selective SSM with hardware-aware design. Mamba-1 (d_state=16) and Mamba-2 (d_state=128, multi-head). Models 130M-2.8B on HuggingFace. |
| `moe-training/` | skill | Train Mixture of Experts (MoE) models using DeepSpeed or HuggingFace. Use when training large-scale models with limited compute (5× cost reduction vs dense models), implementing sparse architectures like Mixtral 8x7B or DeepSeek-V3, or scaling model capacity without proportional compute increase. Covers MoE architectures, routing mechanisms, load balancing, expert parallelism, and inference optimization. |
| `nanogpt/` | skill | Educational GPT implementation in ~300 lines. Reproduces GPT-2 (124M) on OpenWebText. Clean, hackable code for learning transformers. By Andrej Karpathy. Perfect for understanding GPT architecture from scratch. Train on Shakespeare (CPU) or OpenWebText (multi-GPU). |
| `rwkv/` | skill | RNN+Transformer hybrid with O(n) inference. Linear time, infinite context, no KV cache. Train like GPT (parallel), infer like RNN (sequential). Linux Foundation AI project. Production at Windows, Office, NeMo. RWKV-7 (March 2025). Models up to 14B parameters. |
| `speculative-decoding/` | skill | Accelerate LLM inference using speculative decoding, Medusa multiple heads, and lookahead decoding techniques. Use when optimizing inference speed (1.5-3.6× speedup), reducing latency for real-time applications, or deploying models with limited compute. Covers draft models, tree-based attention, Jacobi iteration, parallel token generation, and production deployment strategies. |
| `torchtitan/` | skill | Provides PyTorch-native distributed LLM pretraining using torchtitan with 4D parallelism (FSDP2, TP, PP, CP). Use when pretraining Llama 3.1, DeepSeek V3, or custom models at scale from 8 to 512+ GPUs with Float8, torch.compile, and distributed checkpointing. |
<!-- PKBLLM_TABLE_END -->
