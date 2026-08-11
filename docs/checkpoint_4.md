# Checkpoint 4 — Báo cáo, kiểm tra và demo

> Thời lượng gợi ý: 3:30–4:00. Đây là checkpoint đóng gói: mọi nhận định phải truy ngược được tới evidence, commit và thành viên phụ trách.

## Task 4.1 — Chuẩn hóa evidence

Đặt toàn bộ evidence trong `submission/evidence/`, dùng tên dễ truy vết:

```text
cp0-health.png
cp0-log-baseline.txt
cp1-validator.txt
cp1-correlation-log.png
cp1-pii-redacted.png
cp2-trace-list.png
cp2-trace-waterfall.png
cp2-prompt-v1.png
cp2-prompt-v2.png
cp2-prompt-rollback.png
cp2-dashboard-validator.txt
cp2-dashboard.png
cp3-metrics-incident.png
cp3-trace-root-cause.png
cp3-log-root-cause.txt
cp3-recovery.png
```

Ảnh phải thấy tên panel/trace, time range và giá trị cần chứng minh. Không lưu ảnh mơ hồ hoặc ảnh có API key, raw PII.

## Task 4.2 — Hoàn thiện `submission/REPORT.md`

Điền đủ:

- repository URL và commit SHA cuối;
- điểm validator, tổng traces, số PII leak;
- correlation ID, trace ID, prompt name/labels/versions;
- đường dẫn tương đối đến từng evidence;
- dashboard, SLO, alert và runbook;
- challenge ID, triệu chứng, root cause, fix, preventive measure;
- đóng góp từng thành viên kèm commit/PR kiểm chứng được.

Mỗi claim kỹ thuật nên có ít nhất một đường dẫn evidence hoặc ID. Không điền commit SHA cuối cho tới sau commit cuối cùng.

## Task 4.3 — Chạy bộ kiểm tra cuối

Đảm bảo API chạy nếu cần tái tạo log, sau đó:

```powershell
python scripts/load_test.py --concurrency 5
python scripts/validate_logs.py
python scripts/validate_dashboard.py
python -m pytest -q
```

Điều kiện mong đợi: load test trả 200, log validator ≥ 80/100 (ưu tiên 100), dashboard 6/6 và pytest pass toàn bộ.

## Task 4.4 — Kiểm tra secret, PII và file không được nộp

```powershell
git status --short
git diff --check
git ls-files .env .venv
git grep -n -I -E "(LANGFUSE_SECRET_KEY=.+|sk-lf-[A-Za-z0-9_-]+|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY)"
python scripts/validate_logs.py
```

`git ls-files .env .venv` không được trả file nào. Lệnh grep không được phát hiện secret thật; placeholder trong tài liệu cần được xem xét thủ công. Không commit `.env`, `.venv/`, cache hoặc raw logs chứa PII.

Kiểm tra danh sách thay đổi:

```powershell
git diff --stat
git diff --name-only
```

Xác nhận không có thay đổi trái phép trong `config/challenge.json`:

```powershell
git diff -- config/challenge.json
```

## Task 4.5 — Commit có chủ đích

Chỉ stage các file đã kiểm tra, không dùng `git add .` khi chưa đọc danh sách thay đổi:

```powershell
git status --short
git add app config scripts tests docs submission
git diff --cached --stat
git diff --cached --check
git commit -m "Complete Day 13 observability lab"
git rev-parse HEAD
```

Chép SHA từ `git rev-parse HEAD` vào báo cáo. Nếu việc sửa báo cáo làm phát sinh commit mới, SHA cuối trong report phải phản ánh commit thực sự được nộp; có thể dùng commit hoàn thiện báo cáo riêng và cập nhật theo quy trình nhóm/Lab Coach.

## Task 4.6 — Chuẩn bị demo ngắn

Demo theo một luồng duy nhất, khoảng 5–7 phút:

1. Health và dashboard: chỉ ra SLO/threshold cùng triệu chứng.
2. Trace: mở trace ID đại diện và waterfall.
3. Logs: tìm cùng correlation ID và chứng minh root cause.
4. Prompt: mở v1/v2 và evidence rollback.
5. Fix/prevention: nêu mitigation, permanent fix và alert/runbook.
6. Verification: trình bày validator và pytest cuối.

Mỗi thành viên phải giải thích được phần mình triển khai và commit tương ứng. Chuẩn bị sẵn tab/đường dẫn để demo không mất thời gian tìm evidence.

## Task 4.7 — Checklist nộp bài

- Repository clone được và đúng quyền truy cập theo yêu cầu lớp.
- Branch/commit cần chấm đã push lên remote.
- `submission/REPORT.md` và `submission/evidence/` tồn tại trên đúng commit.
- URL nộp là URL repository, kèm commit SHA cuối.
- Không nộp `.env`, secret, `.venv/`, cache, sample solution hoặc PII chưa redact.

## Definition of Done

- [ ] Report đầy đủ và mọi evidence link mở được.
- [ ] Validators và toàn bộ tests pass theo ngưỡng yêu cầu.
- [ ] Không có secret, raw PII hoặc file cấm trong Git.
- [ ] Đóng góp cá nhân khớp commit/PR.
- [ ] Demo đi theo Metrics → Traces → Logs → Root cause → Fix.
- [ ] Repo URL và commit SHA cuối đã sẵn sàng để nộp.
