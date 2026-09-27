# 05 — Tool-Calling Sheets + Webhook (Conditional HIGH)

**Goal:** Audit trail Sheets permanen + notifikasi Webhook hanya HIGH — Tool-Calling via LLM terkontrol, bukan spam.

**Owner:** T2 | **Skill:** `docs-lookup` + `seith-warden-compliance`

**Tool:** `generate_compliance_remediation_log(clause_id, risk_level LOW|MEDIUM|HIGH, remediation_text)` → `{sheets_status, webhook_status}`

**Sheets (free, 9 kolom — AGENTS.local §3):**
```
Timestamp | Dokumen | Klausul | Jenis Temuan | Nilai Temuan | Batas Regulasi | Tingkat Risiko | Rekomendasi Klausul | Reviewer (HITL)
2026-09-27T10:00 | SOP-Bunga | 1 | RATE_CAP_BREACH | 0.25%/hari | 0.10% Pasal12(1) | HIGH | Ganti: "Bunga max 0,1%..." | compliance@fintech.id
```
- Sheets API free — `SHEETS_ID` + `SHEETS_WEBHOOK_URL` di `.env`, custom component `tools/` jika perlu.
- Normalized schema — fail fast jika `remediation_text` kosong.

**Webhook (HIGH only):**
```
if risk_level=="HIGH" → POST {SHEETS_WEBHOOK_URL} {clause_id, risk_level, remediation_text, sheets_status}
else → {webhook_status:"skipped"} // LOW/MEDIUM/PERLU_VERIFIKASI_MANUAL/COMPLIANT = OK, bukan error
```
- `webhook.site` / Slack free — `skipped` adalah expected, bukan fail.
- Tool-calling via Langflow conditional node — bukan auto-fire.

**Env:** `GOOGLE_API_KEY` + `LANGFLOW_API_KEY` + `SHEETS_ID` + `SHEETS_WEBHOOK_URL` — hanya `${env}` di `flows/*.json` (Tier-0.5).

**Verify:**
```
uv run ruff check . → 0
SHEETS_WEBHOOK_URL kosong → webhook skipped OK
risk_level HIGH → sheets_status:"ok" + webhook_status:"ok"/"skipped" tergantung env
tree /F → tools/ custom component <50 baris jika ada
```
**Accountability:**
- ✅: —
- ⚠️: Sheets quota free → graceful degradation: return `sheets_status:"degraded: quota"` + tetap JSON valid
- 🔻: webhook fire untuk LOW → spam — deteksi: `grep webhook_status tests/*.json` hanya HIGH ok
- ♻️ Refactor: extract `sheets_row()` + `webhook_payload()` fn<50

**Next:** Phase 01 verify gate → Phase 02 (jika ada: E2E + deck)
