# Checkpoint 0 — Setup và baseline

> Thời lượng gợi ý: 0:00–0:30. Mục tiêu của checkpoint là chứng minh môi trường chạy đúng, API phản hồi, load test tạo được log và nhóm có số liệu baseline trước khi sửa code.

## Kết quả cần đạt

- Python 3.11+ và virtual environment hoạt động.
- API trả `ok: true` tại `/health`.
- Load test gọi được `/chat` và tạo `data/logs.jsonl`.
- Đã lưu kết quả baseline của validator; baseline có thể chưa đạt vì các TODO chưa hoàn thiện.
- Không có `.env`, API key hoặc secret trong Git.

## Task 0.1 — Kiểm tra công cụ và vị trí làm việc

Mở PowerShell tại thư mục gốc repository:

```powershell
Set-Location D:\vinuni-lab\Day13-K3-Observability
python --version
git --version
git status --short
```

Python phải từ 3.11 trở lên. Ghi nhận các file đã thay đổi trước khi làm để tránh ghi đè công việc của thành viên khác.

## Task 0.2 — Tạo môi trường Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Nếu PowerShell chặn script kích hoạt, chỉ áp dụng cho terminal hiện tại rồi kích hoạt lại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Không commit `.env` hoặc `.venv/`.

## Task 0.3 — Cấu hình tracing

Điền các biến `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` và `LANGFUSE_HOST` trong `.env` bằng project được Lab Coach cấp. Giữ:

```dotenv
LANGFUSE_PROMPT_NAME=day13-chat
LANGFUSE_PROMPT_LABEL=production
```

Nếu chưa có key, checkpoint setup vẫn làm được nhưng `/health` sẽ báo `tracing_enabled: false`; evidence trace và prompt version ở checkpoint 2 sẽ chưa thể hoàn tất.

## Task 0.4 — Chạy API và health check

Terminal 1 (giữ terminal này chạy):

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --env-file .env
```

Terminal 2:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health | ConvertTo-Json -Depth 4
```

Kết quả tối thiểu phải có `"ok": true`. Nếu cổng 8000 bị chiếm, tìm và dừng đúng tiến trình đang dùng cổng trước khi chạy lại; các script trong lab đang cố định URL `http://127.0.0.1:8000`.

## Task 0.5 — Tạo dữ liệu baseline

Trong Terminal 2:

```powershell
python scripts/load_test.py
Test-Path data/logs.jsonl
Get-Content data/logs.jsonl -Tail 5
python scripts/validate_logs.py
python scripts/validate_dashboard.py
python -m pytest -q
```

Ý nghĩa kết quả:

- `load_test.py` phải in HTTP status `200` cho các request.
- `Test-Path` phải trả `True`; mỗi dòng log phải là một JSON object.
- `validate_logs.py` có thể dưới 80/100 ở baseline vì middleware, context và PII processor còn TODO.
- `validate_dashboard.py` phải in `HỢP LỆ: 6/6 panel`.
- Lưu lỗi test nếu có để phân loại cho checkpoint sau, không sửa bằng cách hard-code output.

## Evidence cần lưu

Tạo `submission/evidence/` nếu chưa có và lưu ảnh hoặc text có:

- kết quả `/health` không lộ key;
- kết quả baseline `validate_logs.py`;
- xác nhận `data/logs.jsonl` đã được tạo;
- phiên bản Python.

Tên file gợi ý: `cp0-health.png`, `cp0-log-baseline.txt`, `cp0-environment.png`.

## Definition of Done

- [ ] API chạy tại cổng 8000 và `/health` trả `ok: true`.
- [ ] `scripts/load_test.py` tạo request thành công.
- [ ] `data/logs.jsonl` tồn tại và đọc được.
- [ ] Baseline validator đã được lưu làm evidence.
- [ ] `.env` và `.venv/` không xuất hiện trong `git status --short`.

## Xử lý lỗi nhanh

- `ModuleNotFoundError`: kích hoạt đúng `.venv`, sau đó cài lại requirements.
- `Connection refused`: kiểm tra Terminal 1 còn chạy và API dùng cổng 8000.
- Không có log: kiểm tra `LOG_PATH=data/logs.jsonl` và gửi ít nhất một request `/chat`.
- `tracing_enabled: false`: kiểm tra đủ public key, secret key và khởi động lại API sau khi sửa `.env`.
