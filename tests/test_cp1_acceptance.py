from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from fastapi.testclient import TestClient
from structlog.contextvars import bind_contextvars, clear_contextvars

from app import agent as agent_module
from app import logging_config, metrics
from app.main import app
from app.pii import hash_user_id, scrub_text


def _read_events(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_cp1_correlation_id_enrichment_and_pii_scrubbing(
    monkeypatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    payload = {
        "user_id": "student-private-id",
        "session_id": "session-cp1",
        "feature": "qa",
        "message": (
            "Email student@vinuni.edu.vn, phone 0901234567, "
            "CCCD 001234567890, card 4111-1111-1111-1111, "
            "passport A12345678, đường Nguyễn Trãi"
        ),
    }

    with TestClient(app) as client:
        custom = client.post(
            "/chat", headers={"x-request-id": "req-deadbeef"}, json=payload
        )
        generated = client.post("/chat", json={**payload, "session_id": "session-next"})

    assert custom.status_code == 200
    assert custom.headers["x-request-id"] == "req-deadbeef"
    assert custom.json()["correlation_id"] == "req-deadbeef"
    assert float(custom.headers["x-response-time-ms"]) >= 0

    generated_id = generated.headers["x-request-id"]
    assert re.fullmatch(r"req-[0-9a-f]{8}", generated_id)
    assert generated_id != "req-deadbeef"
    assert generated.json()["correlation_id"] == generated_id

    api_events = [event for event in _read_events(log_path) if event.get("service") == "api"]
    assert api_events
    for event in api_events:
        assert event["correlation_id"] in {"req-deadbeef", generated_id}
        assert event["user_id_hash"] == hash_user_id(payload["user_id"])
        assert event["feature"] == "qa"
        assert event["model"] == "claude-sonnet-4-5"
        assert event["env"] == "dev"

    raw_logs = log_path.read_text(encoding="utf-8")
    for secret in (
        "student-private-id",
        "student@vinuni.edu.vn",
        "0901234567",
        "001234567890",
        "4111-1111-1111-1111",
        "A12345678",
    ):
        assert secret not in raw_logs
    # The logged preview is intentionally truncated to 80 characters. Verify the
    # markers that fit in that preview; all PII types are exercised separately below.
    for pii_type in ("EMAIL", "PHONE_VN", "CCCD"):
        assert f"REDACTED_{pii_type}" in raw_logs


def test_cp1_scrub_text_supports_common_formats() -> None:
    samples = {
        "student@vinuni.edu.vn": "REDACTED_EMAIL",
        "+84 90 123 4567": "REDACTED_PHONE_VN",
        "090.123.4567": "REDACTED_PHONE_VN",
        "001234567890": "REDACTED_CCCD",
        "4111 1111 1111 1111": "REDACTED_CREDIT_CARD",
        "A12345678": "REDACTED_PASSPORT",
        "đường Nguyễn Trãi": "REDACTED_ADDRESS_VN",
    }
    for raw, marker in samples.items():
        result = scrub_text(raw)
        assert raw not in result
        assert marker in result


def test_cp1_trace_contains_correlation_id(monkeypatch) -> None:
    class RecordingClient:
        def __init__(self) -> None:
            self.trace_updates: list[dict] = []

        def update_current_trace(self, **kwargs) -> None:
            self.trace_updates.append(kwargs)

        def update_current_generation(self, **kwargs) -> None:
            pass

    client = RecordingClient()
    monkeypatch.setattr(agent_module, "get_langfuse_client", lambda: client)
    monkeypatch.setattr(agent_module, "tracing_enabled", lambda: False)
    clear_contextvars()
    bind_contextvars(correlation_id="req-cafebabe")
    try:
        agent = agent_module.LabAgent()
        agent_module.LabAgent.run.__wrapped__(
            agent,
            user_id="student-01",
            feature="qa",
            session_id="session-01",
            message="Explain traces",
        )
    finally:
        clear_contextvars()

    trace = client.trace_updates[-1]
    assert trace["metadata"]["correlation_id"] == "req-cafebabe"
    assert trace["user_id"] == hash_user_id("student-01")
    assert trace["session_id"] == "session-01"


def test_cp1_metrics_error_rate(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "TRAFFIC", 8)
    monkeypatch.setattr(metrics, "ERRORS", Counter({"RuntimeError": 2}))

    result = metrics.snapshot()

    assert result["error_rate_pct"] == 20.0
    assert result["error_breakdown"] == {"RuntimeError": 2}
