# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối: latest commit on branch `cp1-structured-logging-pii`
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (CP1)
- Tổng số traces: 20 unique correlation IDs found / 42 log records analyzed
- Số PII leak còn lại: 0 potential leaks detected by `scripts/validate_logs.py`
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID: `submission/evidence/cp1-redacted-log-snippet.jsonl` có các log `request_received` với `correlation_id` dạng `req-<8hex>`, ví dụ `req-5ba2a6be`. Correlation ID này cũng xuất hiện trong metadata của Langfuse trace để đối chiếu trace với log thô.
- Evidence PII redaction: `submission/evidence/cp1-redacted-log-snippet.jsonl` chứng minh PII đã được che bằng các chuỗi `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CREDIT_CARD]`. Kiểm tra thủ công trên `data/logs.jsonl` không còn email chứa `@` hoặc số thẻ test `4111`.
- Evidence trace waterfall: `submission/evidence/cp1-trace-waterfall.png`, trace ID `2f9b8db3acec775245e0d5133c3ae6e9` trên Langfuse, hiển thị waterfall gồm span `run` và generation con; metadata có `correlation_id=req-5ba2a6be`.
- Giải thích một span đáng chú ý: Span `run` là span chính của `LabAgent.run`, bao phủ quá trình retrieve context, resolve prompt, gọi mock LLM/generation, tính cost/quality và ghi metrics. Metadata `correlation_id=req-5ba2a6be` giúp nối trace này với dòng log tương ứng trong `data/logs.jsonl`.

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Thị Khánh Ly | CP1 - Structured Logging, Correlation ID & PII: hoàn thiện middleware correlation ID, enrich log context, bật PII scrubbing, thêm PII patterns, liên kết correlation ID vào Langfuse trace, bổ sung `error_rate_pct` và lưu evidence. | Branch `cp1-structured-logging-pii`; implementation commits `7203617`, `270d92a`; PR link: https://github.com/trng28/Day13-K3-Observability/pull/new/cp1-structured-logging-pii | Hiểu cách dùng `structlog.contextvars` để truyền metadata theo từng request, vì sao cần `clear_contextvars()` để tránh rò context giữa requests, và cách nối log với trace bằng `correlation_id`. |
