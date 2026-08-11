param(
    [switch]$WithLogValidator
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Python virtual environment not found: $python"
}

Push-Location $repoRoot
try {
    Write-Host "[CP1] Running focused automated tests..."
    & $python -m pytest -q `
        tests/test_chat_observability.py `
        tests/test_pii.py `
        tests/test_metrics.py `
        tests/test_tracing_adapter.py `
        tests/test_agent_prompt_trace.py `
        tests/test_validate_logs.py
    if ($LASTEXITCODE -ne 0) {
        throw "CP1 automated tests failed with exit code $LASTEXITCODE"
    }

    if ($WithLogValidator) {
        if (-not (Test-Path -LiteralPath "data/logs.jsonl")) {
            throw "data/logs.jsonl not found. Start the API and run scripts/load_test.py first."
        }

        Write-Host "[CP1] Validating generated JSONL logs..."
        & $python scripts/validate_logs.py
        if ($LASTEXITCODE -ne 0) {
            throw "Log validator failed with exit code $LASTEXITCODE"
        }
    }

    Write-Host "[CP1] PASS"
}
finally {
    Pop-Location
}
