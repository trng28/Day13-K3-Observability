# Checkpoint 2 — Metrics, traces, prompt versioning và dashboard

> Thời lượng gợi ý: 1:30–2:30. Checkpoint này tạo chuỗi evidence đầy đủ từ log/metrics đến Langfuse trace, prompt version và dashboard runtime.

## Task 2.1 — Xác minh metrics đầu vào

Giữ API chạy và tạo traffic:

```powershell
python scripts/load_test.py --concurrency 5
Invoke-RestMethod http://127.0.0.1:8000/metrics | ConvertTo-Json -Depth 5
```

Kiểm tra `traffic`, `latency_p50/p95/p99`, `total_cost_usd`, token totals, `error_breakdown` và `quality_avg`. Đồng thời đối chiếu event `response_sent` trong `data/logs.jsonl`, vì đây mới là nguồn chuẩn của dashboard chấm điểm.

## Task 2.2 — Xác minh Langfuse tracing

Kiểm tra health:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health | Select-Object ok,tracing_enabled
```

`tracing_enabled` phải là `True`. Sau khi load test, mở project Langfuse và xác nhận:

- có tối thiểu 10 traces;
- trace có user ID dạng hash, session ID và tags;
- generation có model, token usage, cost và metadata;
- input/output không bị capture tự động ngoài chủ đích (`capture_input=False`, `capture_output=False`);
- có thể mở waterfall và nhận diện generation span.

Nếu trace ghi `prompt_source=local-fallback`, kiểm tra host/key/prompt label rồi khởi động lại API. Không sửa metadata để giả version.

## Task 2.3 — Tạo prompt version 1

Trong Langfuse Prompt Management, tạo text prompt tên `day13-chat` với đúng contract:

```text
Feature={{feature}}
Docs={{docs}}
Question={{message}}
```

Gắn labels `baseline` và `production` cho version 1. Trong `.env` đặt `LANGFUSE_PROMPT_LABEL=baseline`, khởi động lại API, rồi gửi một input chuẩn:

```powershell
$body = @{user_id='prompt-user'; session_id='prompt-v1'; feature='refund'; message='What is your refund policy?'} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/chat -ContentType application/json -Body $body
```

Ghi trace ID và xác nhận metadata `prompt_name=day13-chat`, `prompt_label=baseline`, `prompt_version=<version 1>`, `prompt_source=langfuse`.

## Task 2.4 — Tạo prompt version 2 và so sánh cùng input

Tạo version 2, giữ nguyên ba biến contract và chỉ thay đổi nhỏ về format/độ dài. Gắn label `candidate`. Đổi `.env` thành `LANGFUSE_PROMPT_LABEL=candidate`, khởi động lại API và gửi đúng input của Task 2.3.

Ghi trace ID thứ hai. Hai trace phải khác version/label nhưng cùng input để việc so sánh có ý nghĩa. Bài không chấm prompt nào “hay hơn”.

## Task 2.5 — Chứng minh promote và rollback

Trên Langfuse:

1. Chuyển label `production` từ version 1 sang version 2.
2. Chụp trạng thái label và gửi một request với `LANGFUSE_PROMPT_LABEL=production`.
3. Xác nhận trace dùng version 2.
4. Chuyển `production` về version 1.
5. Chụp trạng thái sau rollback và, nếu thời gian cho phép, gửi request xác minh lại.

Lưu ý client dùng cache TTL 60 giây; sau khi đổi label nên khởi động lại API hoặc chờ cache hết hạn trước khi kết luận rollback không hoạt động.

## Task 2.6 — Kiểm tra dashboard contract

```powershell
python scripts/validate_dashboard.py
```

Phải nhận `HỢP LỆ: 6/6 panel`. Validator chỉ kiểm tra YAML contract, không chứng minh dashboard runtime đã đọc đúng dữ liệu.

Dashboard cần đúng sáu nhóm:

| Panel | Nguồn log | Phép tính chính | Threshold |
|---|---|---|---|
| Latency | `response_sent.latency_ms` | P50/P95/P99 | P95 ≤ 3000 ms |
| Traffic | `request_received` | count/rate mỗi phút | ≥ 1 request/phút |
| Errors | received/failed + `error_type` | error rate và breakdown | ≤ 2% |
| Cost | `response_sent.cost_usd` | sum theo phút và total | total ≤ 2.5 USD |
| Tokens | `tokens_in`, `tokens_out` | sum từng field | ≤ 50,000 tokens |
| Quality | `quality_score` | mean | ≥ 0.75 |

Đặt time range 60 phút, refresh 15–30 giây, đơn vị và SLO/threshold line rõ ràng. Có thể dùng Streamlit, notebook, Grafana hoặc công cụ tương đương, nhưng nguồn chuẩn phải là `data/logs.jsonl`.

## Task 2.7 — Runtime test bằng incident practice

```powershell
python scripts/inject_incident.py --scenario rag_slow
python scripts/load_test.py --concurrency 5
Invoke-RestMethod http://127.0.0.1:8000/metrics | ConvertTo-Json -Depth 5
python scripts/inject_incident.py --scenario rag_slow --disable
```

So sánh baseline với incident: P95 phải tăng rõ ràng. Từ khoảng thời gian xấu, mở một trace chậm, lấy correlation ID và tìm log tương ứng. Luôn disable incident sau khi thử để tránh làm bẩn lần đo sau.

## Task 2.8 — SLO, alerts và runbook

Đối chiếu `config/slo.yaml`, hoàn thiện ba TODO alerts trong `config/alert_rules.yaml`, sau đó điền chi tiết tương ứng trong `docs/alerts.md`. Mỗi alert cần condition, duration, severity, user impact, owner, ba bước chẩn đoán đầu tiên và mitigation. Alert phải dựa trên triệu chứng/SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Evidence cần lưu

- danh sách ít nhất 10 traces và một waterfall;
- hai trace ID của baseline/candidate;
- ảnh hai prompt versions và ảnh promote/rollback;
- output validator dashboard;
- ảnh dashboard đủ 6 nhóm, time range, unit, threshold;
- alert rules và runbook hoàn chỉnh.

## Definition of Done

- [ ] Có ít nhất 10 traces thật với metadata đầy đủ.
- [ ] Trace v1/v2 gắn đúng prompt name, label và version.
- [ ] Promote/rollback `production` có bằng chứng.
- [ ] Dashboard validator báo 6/6 và dashboard runtime đủ sáu nhóm.
- [ ] SLO, ba alerts và runbook đã hoàn thiện.
