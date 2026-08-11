from __future__ import annotations

import os
import uuid
from pathlib import Path


# Unit tests must never export telemetry to the real Langfuse project.
os.environ.pop("LANGFUSE_PUBLIC_KEY", None)
os.environ.pop("LANGFUSE_SECRET_KEY", None)
os.environ["OTEL_SDK_DISABLED"] = "true"


def pytest_configure(config) -> None:
    """Use a fresh workspace-local temp root on every pytest invocation.

    A fixed basetemp can retain Windows ACLs from another process or sandbox and
    make later runs fail before test setup. A unique path avoids that shared
    mutable state and also bypasses an inaccessible system pytest temp root.
    """
    if config.option.basetemp is None:
        run_id = uuid.uuid4().hex[:12]
        config.option.basetemp = Path(__file__).parent / "data" / f".pytest-tmp-{run_id}"
