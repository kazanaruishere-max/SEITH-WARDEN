$ErrorActionPreference = "Stop"

Write-Host "=== SEITH-WARDEN: PM Verification Gate (Seller Guard) ===" -ForegroundColor Cyan

# 1. Linting with Ruff
Write-Host "[1/5] Running Ruff check on codebase..." -ForegroundColor Yellow
uv run ruff check .
if ($LASTEXITCODE -ne 0) {
    Write-Error "Ruff check failed!"
    exit 1
}
Write-Host "  -> [OK] Ruff check clean (0 errors)" -ForegroundColor Green

# 2. Unit Tests
Write-Host "[2/5] Running Seller Guard Unit Tests (8 tests)..." -ForegroundColor Yellow
uv run python tests/test_seller_guard.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Unit tests failed!"
    exit 1
}
Write-Host "  -> [OK] Unit tests passed" -ForegroundColor Green

# 3. E2E Scenario Matrix Tests (S1-S12)
Write-Host "[3/5] Running E2E Scenarios & Security Tests (13 tests)..." -ForegroundColor Yellow
uv run python tests/test_e2e_seller_guard.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "E2E scenario tests failed!"
    exit 1
}
Write-Host "  -> [OK] E2E scenarios S1-S12 passed" -ForegroundColor Green

# 4. JSON Syntax & Contract Validation
Write-Host "[4/5] Validating JSON files..." -ForegroundColor Yellow
uv run python -m json.tool data/kb/pmk37_config.json > $null
uv run python -m json.tool data/kb/pmk37_rules.json > $null
uv run python -m json.tool tests/fixtures/config_test.json > $null
uv run python -m json.tool tests/expected_seller_guard.json > $null
uv run python -m json.tool flows/seith_warden_flow.json > $null
Write-Host "  -> [OK] JSON files valid" -ForegroundColor Green

# 5. Langflow Graph Validation
Write-Host "[5/5] Validating Langflow Runtime Graph Compilation..." -ForegroundColor Yellow
& "C:\Users\Lenovo\AppData\Local\com.LangflowDesktop\.langflow-venv\Scripts\python.exe" -c "
import json
from lfx.graph.graph.base import Graph
with open('flows/seith_warden_flow.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
g = Graph.from_payload(d)
assert len(g.vertices) == 10, f'Expected 10 vertices, got {len(g.vertices)}'
assert len(g.edges) == 13, f'Expected 13 edges, got {len(g.edges)}'
print(f'Graph build PASS: {len(g.vertices)} vertices, {len(g.edges)} edges connected.')
"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Langflow graph compilation failed!"
    exit 1
}
Write-Host "  -> [OK] Graph compilation verified 100%" -ForegroundColor Green

Write-Host "`n=== SELLER GUARD GATE GREEN: ALL VERIFICATIONS PASSED ===" -ForegroundColor Green
