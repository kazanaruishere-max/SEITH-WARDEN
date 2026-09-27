# 08 — HITL Closed Loop + Cost Dashboard (Sheets Readback)

**Goal:** Sheets bukan fire-and-forget — officer `REJECT` di Sheets → re-route + dashboard `cost_avoided`.

**Owner:** T2 | **Skill:** `docs-lookup` + `seith-warden-compliance` | **Zone:** `flows` + `scripts/verify.ps1`

**Alur Canvas:**
```
RiskSynthesizer → Sheets Write(9 kolom) → Router(HIGH only) → API Request(GET Sheets Reviewer col) → Router(REJECT?) → RiskSynthesizer re-draft
                                                      → Chat Output strict JSON + cost_avoided calculation
```

**Sheets 9 kolom + HITL col:**
```
Timestamp|Dokumen|Klausul|Jenis|Nilai|Batas|Risiko|Rekomendasi|Reviewer(HITL)
...|HIGH|Ganti: 0,1%...|Pending → officer edit REJECT/APPROVE → API Request poll
```

**Dual Persona Router (Bob vs opencode):**
- Entry 1: `audit_severity` — Bob natural `"audit Pasal 1"` → severity + violation bool
- Entry 2: `draft_remediation` — Bob `"draft perbaikan Pasal 1"` → klausul baru
- Canvas branching visible = Technical 10% wow (bukan 3 tool flat). Opencode shared `re` logic via same Code node.

**Cost Dashboard (Langflow Code node):**
```py
cost_avoided = docs_per_month * 35_000_000 * 0.85  # docs dari Sheet row count, retainer manual 35jt vs SaaS 4.9jt
```
- Tampil di Chat Output `+ {"impact": {"sheets_rows":12, "cost_avoided_rp": "Rp420jt/bln"}}` — User Impact 20%

**Verify:**
```
Sheets write → HIGH sent else skipped (S05 PERLU skipped OK)
Edit Reviewer=REJECT di Sheets → API Request detect → re-route hijau
verify.ps1: sheets_status/webhook_status + cost_avoided in JSON
```

**Accountability:**
- ⚠️ Sheets API quota free — graceful `failed` tapi JSON tetap return
- 🔻 Spam webhook LOW → Router HIGH only wajib
- ♻️ Refactor: extract `sheets_row()` `cost_avoided()` fn<50

**Next:** Phase 01 implementasi T1 06-07 → T2 08 + 04-MCP dual persona + 05-Sheets verify
