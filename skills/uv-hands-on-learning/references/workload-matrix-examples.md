# Workload matrix examples

## Serving runtime (OpenAI-compatible server)

| Workload | Batch | Seq len | Dtype | Notes |
| --- | --- | --- | --- | --- |
| single chat | 1 | 128 in / 32 out | fp16 | validate end-to-end |
| concurrent chat | 16 | 128 in / 32 out | fp16 | throughput under concurrency |
| kv growth | 1 | 128 in / 256 out | fp16 | observe ITL growth with KV length |

## Kernel library (FlashInfer / attention primitives)

| Workload | Batch | Seq len | Dtype | Notes |
| --- | --- | --- | --- | --- |
| prefill microbench | 1 | 1024 | fp16 | cold vs warm |
| decode microbench | 32 | 1 | fp16 | kv_len sweep |
| paged kv append | 32 | N/A | fp16 | page_size sweep |

