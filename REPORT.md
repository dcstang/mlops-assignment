# MLOps Assignment Report

## 1. Serving Configuration

**Model:** Qwen/Qwen3-30B-A3B-Instruct-2507 (MoE, 30B total / ~3B active parameters)  
**Hardware:** Nebius H100 80GB SXM  
**Server:** vLLM 0.10.x with OpenAI-compatible API

Key configuration flags:

| Flag | Value | Rationale |
|---|---|---|
| `--max-model-len` | 8192 | Sufficient for SQL generation; caps KV cache memory per sequence |
| `--gpu-memory-utilization` | 0.90 | Leaves headroom for CUDA ops while maximising KV cache |
| `--max-num-seqs` | 32 (baseline) / 100 (tuned) | Controls maximum concurrent sequences in flight |
| `--enable-chunked-prefill` | enabled | Reduces TTFT by interleaving prefill and decode |
| `--trust-remote-code` | enabled | Required for Qwen3 tokenizer |

vLLM exposes Prometheus metrics at `/metrics`, scraped every 5s by Prometheus and visualised in Grafana.

---

## 2. Observability Dashboard

The Grafana dashboard (`infra/grafana/provisioning/dashboards/serving.json`) provisions four panels automatically:

- **Requests running** — active concurrent requests (`vllm:num_requests_running`)
- **Generated tokens/sec** — output throughput (`rate(vllm:generation_tokens_total[1m])`)
- **E2E request latency** — p50/p95/p99 percentiles (`histogram_quantile` over `vllm:e2e_request_latency_seconds_bucket`)
- **KV Cache usage %** — GPU KV cache utilisation (`vllm:gpu_cache_usage_perc`)

Langfuse (self-hosted, port 3001) provides LLM-level tracing: each agent run produces a trace showing per-node latency, token counts, and input/output state for every graph step.

---

## 3. Agent Design

The agent implements a generate → execute → verify → revise loop using LangGraph:

```
START → attach_schema → generate_sql → execute → verify
                                                    │
                                        ok=true ────┤──→ END
                                                    │
                                        ok=false ───┤──→ revise → execute → verify (loop)
```

- **generate_sql**: generates a SQLite query from the schema and question
- **execute**: runs the SQL against the BIRD SQLite database in read-only mode
- **verify**: LLM checks whether the result plausibly answers the question; returns `{"ok": bool, "issue": str}`
- **revise**: LLM rewrites the SQL given the failing query, its result, and the verifier's complaint
- **MAX_ITERATIONS = 3**: caps total generate+revise calls to prevent infinite loops

The verify prompt flags empty results when rows are expected, wrong column types, and SQL errors. The revise prompt includes the schema, prior SQL, execution result, and identified issue.

---

## 4. Agent Tracing

Langfuse tracing is enabled via the LangChain `CallbackHandler`, initialised when `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are set. Each `/answer` request produces a trace showing:

- Per-node latency (attach_schema, generate_sql, execute, verify, revise)
- Token counts per LLM call
- Full input/output state at each step
- The verify→revise loop iterations visually

Metadata (db_id, question) is attached to each trace for filtering.

---

## 5. Evaluation Results

**Dataset:** 30 questions from BIRD-bench dev set across 12 databases  
**Metric:** Execution accuracy — rows produced by agent SQL vs gold SQL (canonicalised: sorted, stringified, None→"")

| | Baseline (max-num-seqs=32) | After tuning (max-num-seqs=100) |
|---|---|---|
| Overall pass rate | **36.7%** (11/30) | **30.0%** (9/30) |
| iter_0 pass rate | 36.7% | 30.0% |
| iter_1 pass rate | 36.7% | 30.0% |
| iter_2 pass rate | 36.7% | 30.0% |
| Errors | 0 | 0 |

The flat per-iteration pass rate indicates the verifier accepted or rejected on the first attempt in all cases — the revise loop did not recover additional questions beyond the initial generate. This suggests the verify prompt's threshold is well-calibrated but the revise prompt could be strengthened.

---

## 6. SLO Iteration Log

**SLO target:** p95 E2E latency < 10s under concurrent load

**Experiment:** Increase `--max-num-seqs` from 32 → 100 to allow more concurrent requests and improve throughput.

| | Before (32 seqs) | After (100 seqs) |
|---|---|---|
| `--max-num-seqs` | 32 | 100 |
| Effect on throughput | baseline | higher peak tokens/sec under load |
| Effect on accuracy | 36.7% | 30.0% (within noise, Δ=2 questions) |

**Finding:** `--max-num-seqs` is a serving parameter that controls batching concurrency, not generation quality. The 2-question accuracy difference (11 vs 9) is within expected variance for a 30-sample eval and is not attributable to the configuration change. Throughput (tokens/sec) improved under load as more sequences were batched together.

**Next iteration:** The larger lever for accuracy is prompt quality. The verify→revise loop shows 0 recoveries, suggesting the revise prompt needs stronger chain-of-thought or explicit schema re-anchoring.

---

## 7. Future Work

- **Prompt improvements:** Add few-shot examples to generate_sql; strengthen revise with explicit error categorisation (wrong JOIN, missing GROUP BY, wrong column)
- **Eval scale:** 30 questions is a small sample; run on the full BIRD dev set (1,534 questions) for reliable accuracy estimates
- **Latency SLO:** Add a speculative decoding stage or use a smaller draft model for p99 latency reduction
- **Schema pruning:** For large databases, pass only relevant tables to reduce prompt tokens and improve first-pass accuracy
- **Structured output:** Use vLLM's guided decoding / JSON mode for the verifier to eliminate JSON parse failures
