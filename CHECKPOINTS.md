# Checkpoint buổi lab

Tài liệu này là chỉ mục tiến độ. Mỗi checkpoint có một README độc lập, chia thành task nhỏ, lệnh chạy, evidence và Definition of Done:

| Mốc | Hướng dẫn chi tiết |
|---|---|
| Checkpoint 0 — Setup và baseline | [docs/checkpoint_0.md](docs/checkpoint_0.md) |
| Checkpoint 1 — Logging và PII | [docs/checkpoint_1.md](docs/checkpoint_1.md) |
| Checkpoint 2 — Metrics, traces và dashboard | [docs/checkpoint_2.md](docs/checkpoint_2.md) |
| Checkpoint 3 — Challenge chính thức | [docs/checkpoint_3.md](docs/checkpoint_3.md) |
| Checkpoint 4 — Báo cáo, kiểm tra và demo | [docs/checkpoint_4.md](docs/checkpoint_4.md) |

## Checkpoint 0 — 0:00–0:30: Setup và baseline

Hướng dẫn từng task: [docs/checkpoint_0.md](docs/checkpoint_0.md).

- Làm theo [SETUP.md](SETUP.md); ưu tiên Langfuse chung/cloud, Docker local chỉ là tùy chọn.
- API và load test chạy được.
- Có `data/logs.jsonl`.
- Lưu kết quả baseline từ `python scripts/validate_logs.py` vào báo cáo.

## Checkpoint 1 — 0:30–1:30: Logging và PII

Hướng dẫn từng task: [docs/checkpoint_1.md](docs/checkpoint_1.md).

- Mỗi request có correlation ID hợp lệ.
- Log API có `user_id_hash`, `session_id`, `feature`, `model`, `env`.
- Email, số điện thoại và số thẻ thử nghiệm không xuất hiện nguyên văn trong log.
- `validate_logs.py` đạt tối thiểu 80/100.

## Checkpoint 2 — 1:30–2:30: Metrics, traces và dashboard

Hướng dẫn từng task: [docs/checkpoint_2.md](docs/checkpoint_2.md).

- Có ít nhất 10 traces với metadata.
- Làm theo [docs/PROMPT_VERSIONING.md](docs/PROMPT_VERSIONING.md): có prompt v1/v2; trace hiển thị `prompt_name`, `prompt_label` và `prompt_version`.
- Thực hiện được một lần đổi label hoặc rollback; không chấm chất lượng prompt.
- `python scripts/validate_dashboard.py` báo hợp lệ.
- Làm theo [docs/DASHBOARD_SETUP.md](docs/DASHBOARD_SETUP.md): dashboard thể hiện latency, traffic, error, token/cost và quality theo [`config/dashboard.yaml`](config/dashboard.yaml).
- Có SLO line hoặc threshold rõ ràng.
- Chụp hai trace prompt, thao tác rollback, kết quả validator và dashboard vào `submission/evidence/`.

## Checkpoint 3 — 2:30–3:30: Challenge chính thức

Hướng dẫn từng task: [docs/checkpoint_3.md](docs/checkpoint_3.md).

Sau khi Lab Coach release `config/challenge.json`:

1. Chạy incident và input chính thức.
2. Xác định triệu chứng từ metrics.
3. Dùng trace để khoanh vùng span bất thường.
4. Dùng log để chứng minh root cause.
5. Đề xuất fix và biện pháp phòng ngừa.

## Hoàn tất — 3:30–4:00: Báo cáo và demo

Hướng dẫn từng task: [docs/checkpoint_4.md](docs/checkpoint_4.md).

- Hoàn thiện `submission/REPORT.md`.
- Kiểm tra không có secret hoặc PII trong Git.
- Commit toàn bộ phần việc hợp lệ.
- Chuẩn bị demo ngắn theo luồng Metrics → Traces → Logs → Root cause.
