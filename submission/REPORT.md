# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: PARIS
- Room: D303
- Repository: <https://github.com/trng28/Day13-K3-Observability>
- Pull Requests: [PR #1](https://github.com/trng28/Day13-K3-Observability/pull/1), [PR #2](https://github.com/trng28/Day13-K3-Observability/pull/2), [PR #3](https://github.com/trng28/Day13-K3-Observability/pull/3)
- Trạng thái: cả 3 PR đã merge vào `main` ngày 11/08/2026.
- Merge commits: PR #1 `189d77b`, PR #2 `a4053a3`, PR #3 `4606a9c`.

| Thành viên | ID |
|---|---|
| Nguyễn Mai Thanh Trúc | 2A202601473 |
| Nguyễn Thị Khánh Ly | 2A202601403 |
| Nguyễn Thị Tuyết Mai | 2A202601693 |

## 2. Kết quả kỹ thuật

- `pytest -q`: **29 passed**, không còn warning.
- `scripts/validate_logs.py`: **100/100**.
- `scripts/validate_dashboard.py`: **HỢP LỆ — 6/6 panel**.
- Tổng số traces trên Langfuse tại thời điểm hoàn thiện báo cáo: **84**.
- Số PII leak còn lại: **0**.
- Correlation IDs hợp lệ trong lần validator cuối: **81**.
- Dashboard contract: [`config/dashboard.yaml`](../config/dashboard.yaml).
- Dashboard specification: [`docs/dashboard-spec.md`](../docs/dashboard-spec.md).
- Tổng quan evidence CP2: [`submission/evidence/cp2-run-summary.md`](evidence/cp2-run-summary.md).

## 3. Logging và tracing

- Evidence correlation ID: [`submission/evidence/cp1-redacted-log.txt`](evidence/cp1-redacted-log.txt); API trả `x-request-id`, `x-response-time-ms` và ghi cùng ID vào JSONL log.
- Evidence PII redaction: [`submission/evidence/cp1-validator.txt`](evidence/cp1-validator.txt); email, số điện thoại, CCCD, thẻ tín dụng, passport và từ khóa địa chỉ được thay bằng `[REDACTED_*]`.
- Evidence trace waterfall: trace incident `d3def7b3c062452a3235eab86333061f` và [`submission/evidence/cp3-investigation.md`](evidence/cp3-investigation.md).
- Span đáng chú ý: trong incident, trace tổng kéo dài 3.426 ms; `retrieve` chiếm 2.504 ms trong khi `generate` chỉ 152 ms. Baseline có `retrieve` khoảng 0 ms.
- Liên kết trace–log: trace metadata chứa `correlation_id=req-53e0c4f6`, khớp event `response_sent` tại dòng 111–112 của `data/logs.jsonl` với `latency_ms=3425`.

## 4. Prompt versioning

- Prompt name: `day13-chat`.
- Baseline: version **1**, label `baseline`; trace `0fb7052fccb7c362593eac54987ba755`, correlation ID `req-reportb1`.
- Candidate: version **2**, label `candidate`; trace `fa7452a3a0bb20064bc20eb248593d79`, correlation ID `req-reportc2`.
- Cả hai trace dùng cùng input: `What is your refund policy?` và có `prompt_source=langfuse`.
- Promote/rollback: đã chuyển label `production` sang version 2, sau đó rollback về version 1. Trạng thái cuối: version 1 có `baseline, production`; version 2 có `candidate`.
- Script thiết lập có thể chạy lại an toàn: [`scripts/setup_cp2_prompts.py`](../scripts/setup_cp2_prompts.py).

## 5. Dashboard, SLO và alerts

- Dashboard validator: **6/6 panel hợp lệ** gồm Latency, Traffic, Error, Cost, Tokens và Quality.
- Time range mặc định: 60 phút; refresh: 30 giây.
- Evidence validator: [`submission/evidence/cp2-validator.txt`](evidence/cp2-validator.txt).
- SLO:
  - P95 latency ≤ 3.000 ms.
  - Error rate ≤ 2%.
  - Daily cost ≤ 2,5 USD.
  - Quality average ≥ 0,75.
- Alert rules: [`config/alert_rules.yaml`](../config/alert_rules.yaml) gồm `high_latency_p95`, `elevated_error_rate` và `cost_budget_exceeded`.
- Runbook: [`docs/alerts.md`](../docs/alerts.md), mỗi alert có user impact, ba bước chẩn đoán, mitigation và owner.
- Alert được thiết kế symptom-based vì latency/error/cost phản ánh tác động người dùng và ổn định hơn tên implementation nội bộ.

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1` — cohort K3, feature `refund`.
- Triệu chứng: baseline P95 là 1.076 ms; trong incident P95 tăng lên 3.425 ms, vượt threshold 2.000 ms khoảng 71,25%. Error rate vẫn 0%, quality vẫn 0,86 và cost không tăng đáng kể. Sau khi tắt incident, P95 giảm về 1.034 ms.
- Trace incident: `d3def7b3c062452a3235eab86333061f`, tổng 3.426 ms; span `retrieve` 2.504 ms; span `generate` 152 ms.
- Trace baseline: `caea41cb6706b5d00d2c4d28562130d2`, tổng 1.077 ms; `retrieve` khoảng 0 ms.
- Trace recovery: `fabdbab6c033b785f7d03de79d4088fe`, tổng 1.034 ms; `retrieve` khoảng 0 ms.
- Log/correlation ID: `req-53e0c4f6`, dòng 111–112 trong `data/logs.jsonl`, `event=response_sent`, `latency_ms=3425`, `feature=refund`.
- Root cause: retrieval bị chèn thêm khoảng 2,5 giây blocking delay. Bằng chứng trực tiếp là `retrieve` tăng từ khoảng 0 ms lên 2.504 ms, còn `generate`, error rate, cost và quality gần như không đổi.
- Mitigation: disable `rag_slow`, chuyển retrieval sang dependency khỏe hoặc cache fallback.
- Permanent fix: loại bỏ blocking delay, đặt timeout và graceful fallback cho vector store.
- Preventive measure: timeout/circuit breaker, caching, span-level latency test và cảnh báo P95 symptom-based.
- Báo cáo điều tra đầy đủ: [`submission/evidence/cp3-investigation.md`](evidence/cp3-investigation.md).

## 7. Pull Requests và đóng góp cá nhân

### Tổng hợp 3 Pull Requests

| PR | Tác giả | Nội dung có bằng chứng trong diff | Quy mô | Trạng thái |
|---|---|---|---:|---|
| [#1 — Complete CP1 structured logging, correlation ID, and PII scrubbing](https://github.com/trng28/Day13-K3-Observability/pull/1) | `ngnkhanhly7` — Nguyễn Thị Khánh Ly | Hoàn thiện middleware correlation ID, log enrichment, PII scrubbing, metrics/error handling; cập nhật load test, report và evidence CP1 | 5 commits, 12 files, +66/−37 | Merged, merge commit `189d77b` |
| [#2 — Complete AI observability checkpoints](https://github.com/trng28/Day13-K3-Observability/pull/2) | `trng28` — Nguyễn Mai Thanh Trúc | Hoàn thiện CP1–CP3, tests, dashboard contract, alert/runbook, prompt setup, incident investigation, pytest Windows isolation và tài liệu checkpoint | 2 commits, 34 files, +1.259/−66 | Merged, merge commit `a4053a3` |
| [#3 — Feat/tracing prompt evidence](https://github.com/trng28/Day13-K3-Observability/pull/3) | `nguyenmaihi` — Nguyễn Thị Tuyết Mai | Bổ sung Langfuse tracing evidence, prompt version/rollback screenshots, trace waterfall evidence và cập nhật report | 3 commits, 10 files, +12/−6 | Merged, merge commit `4606a9c` |

### Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Thị Khánh Ly (`ngnkhanhly7`) | Structured logging, correlation ID, PII scrubbing, error-rate metrics và evidence CP1 | [PR #1](https://github.com/trng28/Day13-K3-Observability/pull/1), commit chính [`7203617`](https://github.com/trng28/Day13-K3-Observability/commit/7203617076523230bb22c71e8e5e04622900bed1) | Làm giàu log context, nối request bằng correlation ID và ngăn PII xuất hiện trong log |
| Nguyễn Mai Thanh Trúc (`trng28`) | Tích hợp tổng thể CP1–CP3; metrics, traces, dashboard/alerts, prompt setup, incident investigation, tests và tài liệu | [PR #2](https://github.com/trng28/Day13-K3-Observability/pull/2), commit chính [`bac7ef6`](https://github.com/trng28/Day13-K3-Observability/commit/bac7ef6e6637bda1796eee58a92e052a64555380) | Liên kết metrics → traces → logs để chứng minh root cause; thiết kế alert symptom-based và test ổn định trên Windows |
| Nguyễn Thị Tuyết Mai (`nguyenmaihi`) | Thu thập và bổ sung evidence Langfuse trace list/waterfall, prompt versions và rollback | [PR #3](https://github.com/trng28/Day13-K3-Observability/pull/3), commit chính [`ee3774b`](https://github.com/trng28/Day13-K3-Observability/commit/ee3774b0f6f0d401c250826710a0da9ee4a1a2d8) | Xác minh trace metadata, prompt versioning và rollback bằng evidence trực quan |

## 8. Checklist evidence

- [x] Pytest full pass: 29/29.
- [x] Log validator: 100/100, không có PII leak.
- [x] Dashboard contract: 6/6.
- [x] Có ít nhất 10 traces; hiện có 84 traces.
- [x] Có trace baseline v1 và candidate v2 với metadata đúng.
- [x] Đã promote và rollback label `production`.
- [x] Có phân tích CP3 nối metric, trace ID và correlation ID.
- [ ] Bổ sung ảnh giao diện Langfuse trace list/waterfall nếu chưa chụp.
- [ ] Bổ sung ảnh dashboard runtime nếu chưa chụp.
