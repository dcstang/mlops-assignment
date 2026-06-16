#!/usr/bin/env bash
#
# Start vLLM with your chosen configuration.
# Reference: https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html

# set -euo pipefail

# Load .env so HF_TOKEN and other vars are available
if [ -f "$(dirname "$0")/../.env" ]; then
  set -a; source "$(dirname "$0")/../.env"; set +a
fi

MODEL="Qwen/Qwen3-30B-A3B-Instruct-2507"

vllm serve \
    --model "$MODEL" \
    --host 0.0.0.0 \
    --port 8011 \
    --trust-remote-code \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.90 \
    --max-num-seqs 100 \
    --enable-chunked-prefill
