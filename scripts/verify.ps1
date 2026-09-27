param([switch]$Full)
$ErrorActionPreference="Stop"
function ok($m){Write-Host "[OK] $m" -ForegroundColor Green}
function fail($m){Write-Host "[FAIL] $m" -ForegroundColor Red; $script:failed=1}
$failed=0
Write-Host "=== SEITH-WARDEN PM Gate (AGENTS §7 + seith-warden-pm) ===" -ForegroundColor Cyan
Write-Host "Bob: .bob/mcp.json lf-seith_warden a760286c-... vs opencode .opencode/opencode.json identik" -ForegroundColor DarkGray
try{uv run ruff check . 2>&1 | Out-String -Stream | Write-Host; if($LASTEXITCODE -ne 0){fail "ruff"}else{ok "ruff"}}catch{fail "ruff $_"}
try{uv run python tools/pii_sanitizer.py 2>&1 | Write-Host; if($LASTEXITCODE -ne 0){fail "pii"}else{ok "pii NIK→rek→email"}}catch{fail "pii $_"}
foreach($f in @("flows/seith_warden_flow.json","tests/test_scenarios.json",".opencode/opencode.json",".bob/mcp.json")){
  try{uv run python -m json.tool $f 1>$null; ok "json $f"}catch{fail "json $f $_"}
}
try{$t=(Get-ChildItem -Path .handoff -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count; if($t -lt 8){fail "handoff $t file <8"}else{ok "handoff $t file"}}catch{fail "handoff $_"}
try{if(-not (Test-Path "flows/seith_warden_flow.json")){fail "flows missing"}else{ok "flows zone"} if(-not (Test-Path "tools/pii_sanitizer.py")){fail "tools missing"}else{ok "tools zone"} if(-not (Test-Path "data/kb/padk_2026_curated.md")){fail "data/kb missing"}else{ok "data/kb zone"} if(-not (Test-Path "tests/test_scenarios.json")){fail "tests missing"}else{ok "tests zone"}; tree /F 2>$null | Select-Object -First 5 | Write-Host }catch{fail "tree $_"}
try{$c=Get-Content ".bob/mcp.json" -Raw -ErrorAction SilentlyContinue; $o=Get-Content ".opencode/opencode.json" -Raw -ErrorAction SilentlyContinue; if($c -notmatch "a760286c-db9f-406b-bb95-4d2121592e5e"){fail "bob project id"}else{ok "bob a760286c-..."} if($c -notmatch "streamablehttp"){fail "bob streamablehttp"}else{ok "bob streamablehttp"} if($o -notmatch "a760286c-"){fail "opencode project id drift"}else{ok "opencode vs bob identik (no drift)"}}catch{fail "mcp check $_"}
if($Full){
  $k=if($env:LANGFLOW_API_KEY){$env:LANGFLOW_API_KEY}else{'${LANGFLOW_API_KEY}'}; try{$r=Invoke-WebRequest http://localhost:7860/api/v1/flows -Headers @{"x-api-key"=$k} -UseBasicParsing -TimeoutSec 5; if($r.StatusCode -eq 200){ok "langflow :7860 200"}else{fail "langflow $($r.StatusCode)"}}catch{Write-Host "[SKIP] langflow :7860 not running (start: uv run langflow run --host 127.0.0.1 --port 7860)" -ForegroundColor Yellow}
  Write-Host "[MANUAL] code-reviewer + security-reviewer paralel | refactor-cleaner fn<50 | no-ai-slop" -ForegroundColor Yellow
}
if($failed){Write-Host "=== GATE RED — PM veto merge ke main ===" -ForegroundColor Red; exit 1}else{Write-Host "=== GATE GREEN — ready implement ===" -ForegroundColor Green}
