# CP2 run summary

Run date: 2026-08-11 (Asia/Saigon)

## Runtime

- Health: `ok=true`, `tracing_enabled=true`
- Load test: 10/10 requests returned HTTP 200
- Traffic: 10
- Latency: P50 948 ms, P95 1302 ms, P99 1302 ms
- Total cost: 0.0210 USD
- Tokens: 330 input, 1334 output
- Error rate: 0.0%
- Quality average: 0.88

## Prompt versions

- Prompt name: `day13-chat`
- Baseline: version 1, labels `baseline` and `production`
- Candidate: version 2, label `candidate`
- Baseline request correlation ID: `req-aadd61fd`
- Candidate request correlation ID: `req-fd8f629c`
- Comparison input: `What is your refund policy?`

Trace IDs and screenshots must be copied from the Langfuse UI because trace IDs are assigned by Langfuse and are not returned by the `/chat` response.

## Validators

- Pytest: 29 passed
- Dashboard contract: 6/6 panels valid
- Alert rules: 3/3 symptom-based rules completed
- Log validator: 100/100; 0 potential PII leaks

## Required visual evidence still to capture

- `cp2-trace-list.png`
- `cp2-trace-waterfall.png`
- `cp2-prompt-v1.png`
- `cp2-prompt-v2.png`
- `cp2-prompt-rollback.png`
- `cp2-dashboard.png`
