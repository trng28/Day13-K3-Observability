from collections import Counter

from app import metrics
from app.metrics import percentile


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_snapshot_exposes_error_rate(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "TRAFFIC", 8)
    monkeypatch.setattr(metrics, "ERRORS", Counter({"RuntimeError": 2}))

    result = metrics.snapshot()

    assert result["error_rate_pct"] == 20.0
    assert result["error_breakdown"] == {"RuntimeError": 2}
