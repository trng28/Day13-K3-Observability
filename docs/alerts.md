# Alert runbook

Các cảnh báo dưới đây dựa trên triệu chứng mà người dùng nhìn thấy hoặc mức tiêu thụ dịch vụ. Không cảnh báo trực tiếp theo tên hàm hay component nội bộ.

## Alert 1

- Tên: `high_latency_p95`
- Severity: `warning`
- SLI/SLO liên quan: `latency_p95_ms`; mục tiêu P95 không vượt quá 3.000 ms.
- Điều kiện và thời gian duy trì: `latency_p95_ms > 3000` liên tục trong 5 phút.
- Ảnh hưởng tới người dùng: đa số request chậm, giao diện có thể timeout hoặc người dùng gửi lại cùng yêu cầu.
- Ba bước kiểm tra đầu tiên:
  1. Xác nhận P50/P95/P99 và traffic trong cùng cửa sổ thời gian để loại trừ một outlier đơn lẻ.
  2. Mở các Langfuse trace chậm trong cửa sổ cảnh báo, so sánh thời lượng các span `retrieve` và `generate`.
  3. Lấy `correlation_id` từ trace metadata, tìm chuỗi event tương ứng trong `data/logs.jsonl` và kiểm tra incident đang bật.
- Mitigation tạm thời: tắt incident thử nghiệm nếu có; giảm concurrency hoặc chuyển traffic sang đường xử lý khỏe trong khi điều tra dependency chậm.
- Owner: `on-call-engineer`

## Alert 2

- Tên: `elevated_error_rate`
- Severity: `critical`
- SLI/SLO liên quan: `error_rate_pct`; mục tiêu không vượt quá 2%.
- Điều kiện và thời gian duy trì: `error_rate_pct > 5` liên tục trong 3 phút.
- Ảnh hưởng tới người dùng: request `/chat` thất bại, người dùng không nhận được câu trả lời hoặc nhận HTTP 500.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra `error_breakdown` và traffic để xác nhận tỷ lệ lỗi, loại lỗi chiếm ưu thế và kích thước mẫu.
  2. Mở trace lỗi gần nhất, xác định span thất bại và ghi lại trace ID, session, feature cùng timestamp.
  3. Dùng `correlation_id` đối chiếu event `request_failed` trong log đã scrub, sau đó kiểm tra trạng thái dependency/incident liên quan.
- Mitigation tạm thời: tắt incident thử nghiệm; vô hiệu hóa feature bị ảnh hưởng hoặc dùng fallback an toàn, đồng thời giữ các feature khỏe tiếp tục phục vụ.
- Owner: `on-call-engineer`

## Alert 3

- Tên: `cost_budget_exceeded`
- Severity: `warning`
- SLI/SLO liên quan: `daily_cost_usd`; ngân sách tối đa 2,5 USD/ngày.
- Điều kiện và thời gian duy trì: tổng chi phí trong ngày lớn hơn 2,5 USD; đánh giá lại mỗi 5 phút.
- Ảnh hưởng tới người dùng: chưa nhất thiết gây lỗi tức thời nhưng có nguy cơ hết ngân sách, throttling hoặc phải ngừng dịch vụ trong ngày.
- Ba bước kiểm tra đầu tiên:
  1. Xác nhận `total_cost_usd`, `avg_cost_usd`, traffic và token input/output trong cùng cửa sổ.
  2. Trong Langfuse, nhóm generation theo model/feature và tìm trace có token hoặc cost bất thường.
  3. Đối chiếu trace với log qua `correlation_id`, kiểm tra prompt version, output token và incident đang bật.
- Mitigation tạm thời: tắt incident thử nghiệm; giới hạn output token/concurrency hoặc chuyển sang model rẻ hơn theo chính sách đã phê duyệt.
- Owner: `team-lead`
