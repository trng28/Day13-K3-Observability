# Checkpoint 3 — Điều tra challenge chính thức

> Thời lượng gợi ý: 2:30–3:30. Mục tiêu là chứng minh root cause theo luồng Metrics → Traces → Logs, không chỉ đoán từ tên incident.

## Điều kiện bắt đầu

- Checkpoint 1 và 2 đã hoàn tất.
- API đang chạy tại `http://127.0.0.1:8000`.
- `config/challenge.json` là file chính thức do Lab Coach release. Không tạo, sửa hoặc thay thế file này.
- Đã lưu baseline metrics/dashboard trước khi bật challenge.

Repo K3 hiện kỳ vọng challenge có `challenge_id`, cohort `K3`, incident hợp lệ, seed, affected feature, latency threshold và danh sách query. Chỉ đọc file để ghi nhận phạm vi; không dùng tên incident làm bằng chứng kết luận.

## Task 3.1 — Ghi nhận baseline và challenge ID

```powershell
Get-Content config/challenge.json
Invoke-RestMethod http://127.0.0.1:8000/health | ConvertTo-Json -Depth 4
Invoke-RestMethod http://127.0.0.1:8000/metrics | ConvertTo-Json -Depth 5
```

Ghi `challenge_id`, thời điểm bắt đầu, feature bị ảnh hưởng và các giá trị baseline P95/error/cost/quality. Không đưa secret vào ảnh.

## Task 3.2 — Bật incident chính thức

Bỏ `--scenario` để script đọc đúng `config/challenge.json`:

```powershell
python scripts/inject_incident.py
python scripts/load_test.py --challenge --concurrency 5
```

Output load test phải hiện đúng Challenge ID/Cohort và status của từng request. Nếu script báo file chưa release hoặc config không hợp lệ, dừng và báo Lab Coach; không tự sửa file.

## Task 3.3 — Xác định triệu chứng bằng metrics

```powershell
Invoke-RestMethod http://127.0.0.1:8000/metrics | ConvertTo-Json -Depth 5
```

So sánh với baseline theo cùng cửa sổ thời gian và trả lời:

- chỉ số nào vượt threshold/SLO;
- bắt đầu lúc nào, kéo dài bao lâu;
- toàn hệ thống hay chỉ một feature;
- error, latency, cost, token hoặc quality thay đổi theo hướng nào.

Chụp dashboard có time range và threshold. Metrics chỉ cho biết triệu chứng; chưa đủ để kết luận root cause.

## Task 3.4 — Khoanh vùng bằng trace

Trong Langfuse, lọc đúng thời gian và feature của challenge:

1. Chọn trace bất thường đại diện.
2. Ghi trace ID, timestamp, latency tổng và prompt version.
3. Mở waterfall, so sánh thời lượng các span.
4. Xác định span chiếm phần lớn latency hoặc sinh lỗi/cost bất thường.
5. Nếu có thể, so sánh với một trace khỏe của cùng feature và input gần tương đương.

Kết luận trung gian phải dựa trên số cụ thể, ví dụ “span retrieval chiếm X ms trên tổng Y ms”, không chỉ nói “RAG chậm”.

## Task 3.5 — Chứng minh bằng logs

Lấy correlation ID liên quan từ response/trace metadata rồi tìm trong JSONL:

```powershell
$correlationId = 'THAY_BANG_CORRELATION_ID'
Select-String -Path data/logs.jsonl -SimpleMatch $correlationId
```

Đối chiếu chuỗi event `request_received` → `response_sent` hoặc `request_failed`, latency, feature, error type và timestamp. Ghi số dòng hoặc trích JSON đã redact vào report. Nếu trace không có correlation ID trực tiếp, dùng session ID/timestamp/feature để đối chiếu rồi xác nhận lại correlation ID từ log.

## Task 3.6 — Viết root cause và hành động

Mỗi kết luận trong `submission/REPORT.md` cần đủ:

- Symptom: chỉ số nào xấu và vượt ngưỡng bao nhiêu.
- Scope: feature/user flow và cửa sổ thời gian bị ảnh hưởng.
- Trace evidence: trace ID và span bất thường.
- Log evidence: correlation ID/log line phù hợp.
- Root cause: cơ chế kỹ thuật gây triệu chứng.
- Fix action: thay đổi trực tiếp để khôi phục dịch vụ.
- Preventive measure: test, timeout, fallback, capacity, alert hoặc guardrail ngăn tái diễn.

Phân biệt mitigation (giảm tác động ngay) với permanent fix (loại bỏ nguyên nhân).

## Task 3.7 — Tắt incident và xác minh phục hồi

Lấy giá trị incident từ file chính thức rồi disable bằng đúng scenario. Với challenge K3 hiện tại:

```powershell
python scripts/inject_incident.py --scenario rag_slow --disable
python scripts/load_test.py --concurrency 5
Invoke-RestMethod http://127.0.0.1:8000/metrics | ConvertTo-Json -Depth 5
```

Lưu bằng chứng metric/trace sau phục hồi. Nếu incident chính thức khác `rag_slow`, thay giá trị `--scenario` bằng incident được release (`tool_fail` hoặc `cost_spike`).

## Evidence cần lưu

- dashboard/metrics trước và trong incident;
- trace ID cùng ảnh waterfall;
- log line có correlation ID tương ứng;
- bằng chứng sau khi disable;
- đoạn phân tích root cause, fix và preventive measure.

## Definition of Done

- [ ] Challenge chạy bằng file chính thức, không sửa config.
- [ ] Triệu chứng được chứng minh bằng metric và threshold.
- [ ] Span bất thường được chỉ rõ bằng trace ID.
- [ ] Root cause được nối với log/correlation ID cụ thể.
- [ ] Có mitigation, permanent fix và preventive measure.
- [ ] Incident đã tắt và có bằng chứng phục hồi.
