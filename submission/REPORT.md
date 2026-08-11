# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: PARIS
- Repository URL: https://github.com/trng28/Day13-K3-Observability
- Commit SHA cuối:
- Thành viên và vai trò: 

    - Teamname: PARIS
    - Room: D303
  
Tên | ID
---|---
Nguyễn Mai Thanh Trúc | 2A202601473
Nguyễn Thị Khánh Ly | 2A202601403
Nguyễn Thị Tuyết Mai | 2A202601693



## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`:
- Tổng số traces:
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

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

- Challenge ID: `day13-k3-observability-v1` (cohort K3, feature `refund`).
- Triệu chứng từ metrics: baseline P95 là 1.076 ms; khi incident xảy ra P95 tăng lên 3.425 ms, vượt threshold 2.000 ms khoảng 71,25%. Error rate vẫn 0%, quality vẫn 0,86 và cost không tăng đáng kể, nên triệu chứng được khoanh vùng là latency. Sau khi tắt incident, P95 giảm về 1.034 ms.
- Trace ID liên quan: trace incident `d3def7b3c062452a3235eab86333061f` kéo dài 3.426 ms; span `retrieve` chiếm 2.504 ms trong khi `generate` chỉ 152 ms. Trace baseline `caea41cb6706b5d00d2c4d28562130d2` có `retrieve` khoảng 0 ms và tổng 1.077 ms. Trace recovery `fabdbab6c033b785f7d03de79d4088fe` có `retrieve` khoảng 0 ms và tổng 1.034 ms.
- Log line/correlation ID liên quan: `req-53e0c4f6`, dòng 111–112 trong `data/logs.jsonl`; event `response_sent` ghi `latency_ms=3425`, feature `refund`, model `claude-sonnet-4-5`. Dòng baseline 99–100 (`req-11f92f7f`) ghi 1.076 ms và recovery 122–123 (`req-17511444`) ghi 1.034 ms.
- Root cause: retrieval bị chèn thêm khoảng 2,5 giây delay. Bằng chứng trực tiếp là span `retrieve` tăng từ khoảng 0 ms lên 2.504 ms, trong khi span `generate`, error rate, quality và cost gần như không đổi.
- Fix action: mitigation ngay lập tức là disable `rag_slow`/chuyển retrieval sang dependency khỏe hoặc fallback cache; permanent fix là loại bỏ blocking delay ở retrieval, đặt timeout và xử lý fallback khi vector store chậm.
- Preventive measure: thêm timeout/circuit breaker cho retrieval, cache kết quả phổ biến, load test latency theo từng span và alert symptom-based khi P95 vượt 3.000 ms trong 5 phút.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
