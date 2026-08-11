# Checkpoint 1 — Structured logging, correlation ID và PII

> Thời lượng gợi ý: 0:30–1:30. Mục tiêu là hoàn thiện các TODO quan sát được trong code và đạt tối thiểu 80/100 với `validate_logs.py`.

## Phạm vi code

- `app/middleware.py`: vòng đời correlation ID.
- `app/main.py`: bind metadata của request.
- `app/logging_config.py`: scrub PII trước khi render/ghi JSON.
- `app/pii.py`: pattern PII và hàm hash/summarize.
- `config/logging_schema.json`: hợp đồng field; chỉ dùng để đối chiếu, không hạ yêu cầu validator.

## Task 1.1 — Viết test trước khi sửa

Chạy nhóm test liên quan để có baseline:

```powershell
python -m pytest tests/test_pii.py tests/test_chat_observability.py tests/test_validate_logs.py -q
```

Bổ sung test cho các hành vi quan trọng nếu public tests chưa bao phủ: giữ `x-request-id` hợp lệ từ client, sinh ID dạng `req-<8 ký tự hex>` khi header không có, response trả lại cùng ID, và log không chứa email/điện thoại/CCCD/thẻ tín dụng nguyên văn.

## Task 1.2 — Hoàn thiện correlation ID middleware

Trong `app/middleware.py`, hoàn thiện theo đúng thứ tự:

1. Gọi `clear_contextvars()` ở đầu mỗi request để tránh rò context giữa request đồng thời.
2. Đọc header `x-request-id`; nếu rỗng thì tạo `req-` cộng 8 ký tự hex từ UUID.
3. Gọi `bind_contextvars(correlation_id=correlation_id)` trước `call_next`.
4. Gán cùng ID vào `request.state.correlation_id`.
5. Đo thời gian bằng `time.perf_counter()` và thêm hai response header: `x-request-id`, `x-response-time-ms`.

Kiểm tra thủ công:

```powershell
$body = @{user_id='u-01'; session_id='s-01'; feature='qa'; message='Explain observability'} | ConvertTo-Json
$headers = @{'x-request-id'='req-demo1234'}
Invoke-WebRequest -Method Post -Uri http://127.0.0.1:8000/chat -ContentType application/json -Headers $headers -Body $body | Select-Object StatusCode,Headers
```

ID trong response, body và các log của request phải đồng nhất.

## Task 1.3 — Bind metadata request

Trong handler `/chat` tại `app/main.py`, bind context trước log `request_received`:

- `user_id_hash`: dùng `hash_user_id(body.user_id)`, tuyệt đối không log raw `user_id`;
- `session_id`: `body.session_id`;
- `feature`: `body.feature`;
- `model`: `agent.model`;
- `env`: giá trị `APP_ENV`, mặc định `dev`.

Các event `request_received`, `response_sent` và `request_failed` của cùng request phải nhận metadata thông qua context, không lặp logic thủ công ở từng log call.

## Task 1.4 — Bật PII scrubbing đúng vị trí

Trong pipeline `structlog` tại `app/logging_config.py`, đăng ký `scrub_event` sau khi merge context và thêm timestamp/level, nhưng bắt buộc trước `JsonlFileProcessor()` và `JSONRenderer()`. Như vậy dữ liệu đã được che trước lúc ghi xuống disk.

`scrub_event` hiện xử lý chuỗi trong `payload` và trường `event`. Nếu nhóm thêm field tự do có thể chứa input người dùng, mở rộng processor theo hướng đệ quy cho dict/list thay vì chỉ che một cấp.

Không ghi raw request body để rồi che sau; dữ liệu nhạy cảm không được chạm file log ở dạng nguyên văn.

## Task 1.5 — Kiểm thử PII bằng dữ liệu chủ động

Gửi request thử nghiệm:

```powershell
$pii = @{user_id='student-raw-id'; session_id='pii-test'; feature='qa'; message='Email student@vinuni.edu.vn, phone 0901234567, CCCD 012345678901, card 4111-1111-1111-1111'} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/chat -ContentType application/json -Body $pii
Get-Content data/logs.jsonl -Tail 10
```

Kỳ vọng có marker như `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CCCD]`, `[REDACTED_CREDIT_CARD]`; không còn giá trị gốc.

## Task 1.6 — Tạo log sạch và chạy validator

Log cũ từ baseline có thể còn `correlation_id=MISSING` và làm validator thất bại. Chỉ xóa log sinh cục bộ sau khi đã lưu baseline và chắc chắn file không phải evidence cần giữ:

```powershell
Remove-Item -LiteralPath data/logs.jsonl -ErrorAction SilentlyContinue
python scripts/load_test.py --concurrency 3
python scripts/validate_logs.py
python -m pytest -q
```

Kết quả mục tiêu:

- ít nhất 2 unique correlation IDs;
- không thiếu field enrichment trên log `service=api`;
- 0 PII leak;
- Estimated Score từ 80/100 trở lên, ưu tiên 100/100;
- toàn bộ public tests pass.

## Evidence cần lưu

- Output đầy đủ của `validate_logs.py`.
- Một dòng `request_received` và một dòng `response_sent` cùng correlation ID.
- Dòng log PII đã được redact, không chụp/commit dữ liệu nguyên bản.
- Kết quả test liên quan.

Tên file gợi ý: `cp1-validator.txt`, `cp1-correlation-log.png`, `cp1-pii-redacted.png`.

## Definition of Done

- [ ] Correlation ID không còn `MISSING`, truyền xuyên suốt request/response/log.
- [ ] API logs có đủ `user_id_hash`, `session_id`, `feature`, `model`, `env`.
- [ ] Raw PII không xuất hiện trong `data/logs.jsonl`.
- [ ] Validator đạt ít nhất 80/100.
- [ ] `python -m pytest -q` pass.
