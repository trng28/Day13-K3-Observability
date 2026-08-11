# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`:
- Tổng số traces: 70 
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall: submission/evidence/trace_waterfall_v1.png, submission/evidence/trace_waterfall_v2.png
- Giải thích một span đáng chú ý: Span `run` đại diện cho execution generation gọi model `claude-sonnet-4-5`, ghi nhận thời gian xử lý, tokens in/out, chi phí (cost) và metadata liên kết trực tiếp với managed prompt trên Langfuse.

## 4. Prompt versioning

- Prompt name: day13-chat
- Version/label baseline: Version 1 (label: baseline)
- Version/label candidate: Version 2 (label: candidate)
- Bằng chứng đổi label hoặc rollback: submission/evidence/prompt_version.png, submission/evidence/prompt_rollback_v1.png, submission/evidence/prompt_rollback_v2.png


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
| | | | |
