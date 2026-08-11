# CP3 incident investigation

## Scope

- Challenge: `day13-k3-observability-v1`
- Incident window: 2026-08-11 04:09:18–04:09:35 UTC
- Affected feature: `refund`
- SLO threshold: P95 latency <= 2,000 ms for this challenge

## Metrics evidence

| Phase | Traffic | P50 | P95 | P99 | Error rate | Cost | Quality |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 5 | 153 ms | 1,076 ms | 1,076 ms | 0% | $0.0115 | 0.86 |
| Incident | 5 | 2,652 ms | 3,425 ms | 3,425 ms | 0% | $0.0102 | 0.86 |
| Recovery | 5 | 152 ms | 1,034 ms | 1,034 ms | 0% | $0.0106 | 0.86 |

Incident P95 exceeded the 2,000 ms challenge threshold by 1,425 ms (71.25%). Stable error rate, cost, and quality isolate the symptom to latency.

## Trace evidence

| Phase | Trace ID | Correlation ID | Total | retrieve | generate |
|---|---|---|---:|---:|---:|
| Baseline | `caea41cb6706b5d00d2c4d28562130d2` | `req-11f92f7f` | 1,077 ms | ~0 ms | 151 ms |
| Incident | `d3def7b3c062452a3235eab86333061f` | `req-53e0c4f6` | 3,426 ms | 2,504 ms | 152 ms |
| Recovery | `fabdbab6c033b785f7d03de79d4088fe` | `req-17511444` | 1,034 ms | ~0 ms | 151 ms |

The incident adds approximately 2.5 seconds entirely inside `retrieve`; generation duration remains stable.

## Log evidence

- Baseline: lines 99–100, `req-11f92f7f`, `latency_ms=1076`.
- Incident: lines 111–112, `req-53e0c4f6`, `latency_ms=3425`.
- Recovery: lines 122–123, `req-17511444`, `latency_ms=1034`.
- All records have `feature=refund`; no PII leak was detected.

## Conclusion and remediation

- Root cause: the retrieval path incurred an artificial blocking delay of approximately 2.5 seconds.
- Immediate mitigation: disable the incident and route retrieval to a healthy dependency or cached fallback.
- Permanent fix: enforce a retrieval timeout with graceful fallback and remove blocking behavior.
- Prevention: add timeout/circuit breaker, caching, span-level latency tests, and a P95 symptom-based alert.

## Visual evidence still required

- `cp3-metrics-incident.png`: baseline/incident/recovery values with threshold.
- `cp3-trace-root-cause.png`: incident waterfall showing the 2,504 ms `retrieve` span.
- `cp3-log-root-cause.png`: log line for `req-53e0c4f6`.
