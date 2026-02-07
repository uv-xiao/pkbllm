# Distributed training

Distributed training frameworks and orchestration (curated: DeepSpeed, PyTorch FSDP2, Ray Train).

## <TABLE>
<!-- PKBLLM_TABLE_START -->
| Path | Type | Description |
| --- | --- | --- |
| `deepspeed/` | skill | Expert guidance for distributed training with DeepSpeed - ZeRO optimization stages, pipeline parallelism, FP16/BF16/FP8, 1-bit Adam, sparse attention |
| `pytorch-fsdp2/` | skill | Adds PyTorch FSDP2 (fully_shard) to training scripts with correct init, sharding, mixed precision/offload config, and distributed checkpointing. Use when models exceed single-GPU memory or when you need DTensor-based sharding with DeviceMesh. |
| `ray-train/` | skill | Distributed training orchestration across clusters. Scales PyTorch/TensorFlow/HuggingFace from laptop to 1000s of nodes. Built-in hyperparameter tuning with Ray Tune, fault tolerance, elastic scaling. Use when training massive models across multiple machines or running distributed hyperparameter sweeps. |
<!-- PKBLLM_TABLE_END -->
