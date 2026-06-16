# Submission Checklist

> Do not delete — required for grading.

## Files to include in *.zip

| File | Status | Notes |
|---|---|---|
| `REPORT.md` | ☐ | ≤ 3 pages — serving config, eval results, SLO iteration log, agent value, future work |
| `infra/grafana/provisioning/dashboards/serving.json` | ☐ | Latency (percentiles), throughput, KV-cache panels |
| `agent/graph.py` | ☐ | verify + revise nodes, conditional edge, iteration cap |
| `agent/prompts.py` | ☐ | generate_sql, verify, revise prompts |
| `evals/run_eval.py` | ☐ | Execution accuracy, per-iteration pass rate, writes results JSON |
| `results/eval_baseline.json` | ☐ | Baseline eval against Qwen3-30B-A3B on H100 |
| `results/eval_after_tuning.json` | ☐ | Post-tuning eval results |
| `screenshots/vllm_manual_query.png` | ☐ | Phase 1 — vLLM running + manual query returning SQL |
| `screenshots/grafana_serving.png` | ☐ | Phase 2 — full dashboard reacting to load |
| `screenshots/langfuse_trace.png` | ☐ | Phase 4 — trace showing verify→revise loop |
| `screenshots/langfuse_tags.png` | ☐ | Phase 4 — trace list with metadata tags visible |
| `screenshots/grafana_eval_run.png` | ☐ | Phase 5 — Grafana dashboard during baseline eval run |
| `screenshots/grafana_before.png` | ☐ | Phase 6 — before tuning change |
| `screenshots/grafana_after.png` | ☐ | Phase 6 — after tuning change that moved the needle |

## Grading weights

| Area | Weight |
|---|---|
| Serving config & justification (Phase 1) | 15% |
| Observability dashboard (Phase 2) | 15% |
| Agent design (Phase 3) | 10% |
| Agent tracing (Phase 4) | 5% |
| Eval rigor (Phase 5) | 15% |
| SLO diagnosis & iteration (Phase 6) | 25% |
| Report & communication (Phase 7) | 15% |

## Phase progress

- [ ] Phase 0 — Setup (ports forwarded, BIRD data loaded, docker-compose up)
- [ ] Phase 1 — vLLM serving Qwen3-30B-A3B on H100, config flags documented
- [ ] Phase 2 — Grafana dashboard with latency/throughput/KV-cache panels
- [ ] Phase 3 — Agent graph wired (generate_sql → execute → verify → revise loop)
- [ ] Phase 4 — Langfuse tracing with metadata tags
- [ ] Phase 5 — Baseline eval run, per-iteration pass rates recorded
- [ ] Phase 6 — SLO iteration log, before/after screenshots, post-tuning eval
- [ ] Phase 7 — REPORT.md complete
