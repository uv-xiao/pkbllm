# Training (post-training)

Post-training methods and toolchains (curated: MILES, SLiME, VERL).

## <TABLE>
<!-- PKBLLM_TABLE_START -->
| Path | Type | Description |
| --- | --- | --- |
| `miles/` | skill | Provides guidance for enterprise-grade RL training using miles, a production-ready fork of slime. Use when training large MoE models with FP8/INT4, needing train-inference alignment, or requiring speculative RL for maximum throughput. |
| `slime/` | skill | Provides guidance for LLM post-training with RL using slime, a Megatron+SGLang framework. Use when training GLM models, implementing custom data generation workflows, or needing tight Megatron-LM integration for RL scaling. |
| `verl/` | skill | Provides guidance for training LLMs with reinforcement learning using verl (Volcano Engine RL). Use when implementing RLHF, GRPO, PPO, or other RL algorithms for LLM post-training at scale with flexible infrastructure backends. |
<!-- PKBLLM_TABLE_END -->
