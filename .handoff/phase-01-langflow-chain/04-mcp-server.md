# 04 — MCP Server (streamablehttp :7860) + Bob Real Connected

**Goal:** Expose 3 tools `Action+Input` via Langflow MCP `streamablehttp` — Bob real discovery SEITH-WARDEN.

**Owner:** T2 | **Skill:** `build-error-resolver` + `seith-warden-compliance`

**MCP Router:** `127.0.0.1:7860` — transport `streamablehttp`, bearer `x-api-key: ${LANGFLOW_API_KEY}` (Desktop via Global Variables Credential `LANGFLOW_API_KEY`, fallback no-auth)

**3 Tools (Action+Input — PDF Hal 27-29):**
```
audit_sop_regulatory_reference(sop_text: string) → {detected_references[]}
evaluate_rate_cap_substance(daily_rate_percent: number, lock_cap_percent?: number) → {substantive_evaluations[]}
generate_compliance_remediation_log(clause_id: string, risk_level: LOW|MEDIUM|HIGH, remediation_text: string) → {sheets_status, webhook_status}
```

**Flow wiring:**
```
PII Sanitizer → Vector SOP 800/150 + Vector PADK hierarchical → RefMapper → RuleAuditor → RiskSynthesizer → Structured Output → Sheets/Webhook (conditional HIGH)
MCP Server expose 3 tools → streamablehttp :7860/api/v1/mcp/project/a760286c-db9f-406b-bb95-4d2121592e5e/streamable (cek ID di URL bar /project/<id>)
```

**Bob Real Connected (Gear → MCP):**
- Langflow Desktop `Settings → Global Variables → Credential LANGFLOW_API_KEY = sk-...So` (reuse `.opencode/opencode.json:15`, H-1 revoke 2026-10-03, no generate baru)
- Bob `Gear → MCP → edit lf-seith_warden` args: `["/c","uvx","--with","mcp~=1.28","mcp-proxy","--transport","streamablehttp","--headers","x-api-key","<LANGFLOW_API_KEY>","http://localhost:7860/api/v1/mcp/project/a760286c-.../streamable"]` — fallback tanpa `--headers` jika 0 tools
- Opencode proxy `.opencode/opencode.json` protokol identik — dev harian via opencode, Bob sebagai wajah juri

**Never kill :7860** (Tier-0.3) — dev lain kill via PID port 3000 spesifik.

**Verify:**
```
uv run langflow run --host 127.0.0.1 --port 7860
Invoke-WebRequest http://localhost:7860/api/v1/flows → 200
Bob Gear→MCP → 3 tools Action+Input tampil (restart Bob setelah edit)
Bob chat "audit klausul Pasal 1 bunga 0,25%/hari" → HIGH + PADK 12:1 (bandingkan Playground)
python -m json.tool flows/seith_warden_flow.json → valid, env ${LANGFLOW_API_KEY} only
```
**Accountability:**
- ✅: Bob config `lf-seith_warden` via Gear→MCP — real connected, bukan formalitas
- ⚠️: Desktop no-auth fallback — tanpa header juga valid, jangan anggap 0 tools = fail sebelum coba fallback
- 🔻: kill 7860 / ID mismatch → MCP 404 — deteksi: pre-demo `Invoke-WebRequest :7860` + compare URL vs opencode.json
- ♻️ Refactor: extract mcp_config single source (opencode vs Bob)

**Next:** 05-sheets-webhook.md → verify E2E screenshot Bob 3 tools untuk submission
