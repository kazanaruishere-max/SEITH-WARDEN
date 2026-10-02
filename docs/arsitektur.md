# DOKUMEN ARSITEKTUR SISTEM: SEITH-WARDEN
**Sistem:** Supervisory Engine for Institutional Trust & Hazard-mitigation — Workflow Automation & Regulatory Detection Engine Network  
**Platform Inti:** Langflow (AI Agent Orchestration & Model Context Protocol Server)  
**Kategori:** RegTech / Financial Compliance Automation — Stack Gratis (Free Tier)

Langflow adalah execution engine sekaligus MCP Server. Dual-vector isolation wajib; context bleeding SOP↔PADK = FAIL.

## 1. Ikhtisar Arsitektur

SEITH-WARDEN adalah sistem audit kepatuhan terotomatisasi berbasis Multi-Agent Pipeline dan Model Context Protocol (MCP). Menerima SOP internal P2P/BNPL, melakukan PII sanitizing, konfrontasi terhadap KB PADK 2026 & UU P2SK, deteksi celah struktural dan substansial, skor risiko, serta eskalasi otomatis. Langflow sebagai backend sekaligus MCP Server mandiri yang mengekspos tool fungsional ke client eksternal.

```
┌────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                            │
│  (Compliance Officer Console / Direct API / MCP Client / IDE)  │
└──────────────────────────────┬─────────────────────────────────┘
                               │ JSON-RPC / MCP
                               ▼
┌────────────────────────────────────────────────────────────────┐
│               LANGFLOW ENGINE & MCP SERVER :7860               │
│  MCP Router (Action+Input):                                    │
│   audit_sop_regulatory_reference | evaluate_rate_cap_substance │
│   generate_compliance_remediation_log                          │
│                     │                                          │
│  DUAL-VECTOR PIPELINE: [SOP Collection] ↔ [PADK Collection]    │
│                     │  (isolated, anti context-bleeding)       │
│  CHAIN: RefMapper (0.0) → RuleAuditor (0.0) → RiskSynthesizer  │
│                     │  (0.1)                                   │
│  TOOL-CALLING: Google Sheets (audit trail) + Webhook (HIGH)    │
└──────────────────────────────────┬─────────────────────────────┘
                                   │ Strict JSON
                                   ▼
                          Chat Output + Sheets/Webhook
```

```
[SOP Internal PDF/txt] ─┐
                         ├─► PII Sanitizer (re stdlib, NIK→rekening→email) ─► Recursive Splitter 800/150 ─► Embedding text-embedding-004 ─► Vector SOP (chroma-local collection_sop_internal)
[KB PADK 2026 curated] ─┘                                                    └► Hierarchical Splitter Bab→Pasal→Ayat ────────► Vector PADK (chroma-local collection_ojk_padk2026)
                                         │                                              │
                                         └────────────── Dual-Collection Isolated ──────┘
                                                              │
                         ┌────────────────────────────────────▼────────────────────────────────────┐
                         │              LANGFLOW ENGINE & MCP SERVER :7860                        │
                         └───────────────────────────────────┬───────────────────────────────────┘
```

## 2. Pipeline Ingestion & Dual-Store Isolation

Dua collection terisolasi untuk mencegah kontaminasi konteks antara klausul internal dan pasal resmi.

### 2.1 Collection SOP Internal — `collection_sop_internal`

- **Sumber:** Dokumen SOP operasional, kebijakan bunga kredit, manual penagihan fintech (`data/sop_dummy/sop_bunga_dummy.md` — 10 klausul dummy: HIGH 3, MEDIUM 3, LOW 2, COMPLIANT 2).
- **Pre-processing PII Sanitizer:** Wajib sebelum chunk & embedding. Urutan `NIK → rekening → email` (NIK 16 digit harus didahulukan agar tidak tertelan regex rekening 13-19 digit). Implementasi `tools/pii_sanitizer.py` — `re` stdlib only, `fn <50`.
```python
import re
def sanitize_sop_text(t: str) -> str:
    t = re.sub(r'\b\d{16}\b', '[REDACTED_NIK]', t)
    t = re.sub(r'\b(?:\d[ -]*?){13,19}\b', '[REDACTED_ACCOUNT_NO]', t)
    t = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', t)
    return t
```
Input `4111 1111 1111 1111` → `[REDACTED_ACCOUNT_NO]`; NIK 16 digit → `[REDACTED_NIK]`; `a@b.co` → `[REDACTED_EMAIL]`. Self-check: `uv run python tools/pii_sanitizer.py` harus `ok`.
- **Chunking:** Recursive Character Text Splitter `800 tokens / overlap 150`, separator per pasal/klausul. Contoh chunk: `Pasal 1 — Bunga 0,25%/hari...` terpisah dari `Pasal 9 — Bunga 0,08%...`.
- **Embedding:** Google `text-embedding-004` free tier. Vector store `chroma-local` persistent di `chroma_db/` (gitignore).

### 2.2 Collection Regulasi — `collection_ojk_padk2026`

- **Sumber:** `data/kb/padk_2026_curated.md` — PADK OJK 2026, POJK 40/2024, UU P2SK 4/2026, PMK 8/2026. SSOT grounding untuk sitasi.
- **Ceiling Graph:** `data/kb/padk_graph.json` — Knowledge Graph deterministik presisi batas (Pasal12 Ayat1 0.1%/hari konsumtif + 0.2 produtif, Ayat3 100% Lock Cap) sinkron dengan curated.md — RuleAuditor query GraphLookup `Custom Component` bukan cosine RAG (100% presisi, sitasi exact) — lihat `.handoff/06-ceiling-graph.md`.
- **Chunking:** Hierarchical Text Splitter terstruktur `Bab → Pasal → Ayat` untuk presisi kutipan (contoh: `Bab III Pasal 12 Ayat 1 — bunga konsumtif maks 0,1%/hari`).
- **Embedding:** Sama `text-embedding-004`, collection terpisah, tidak pernah digabung dengan SOP.

### 2.3 Isolasi Dual-Vector

- SOP dan PADK tidak pernah campur index. Retriever A query `collection_sop_internal`, Retriever B query `collection_ojk_padk2026`. Konfigurasi Langflow: dua vector store node independen, dua retriever node. Validasi: query SOP tidak mengembalikan pasal PADK dan sebaliknya.

## 3. Alur Multi-Agent (Chained Execution)

Rantai sekuensial tiga agen — output JSON agen N menjadi input agen N+1.

```
[ChatInput dual persona Router] → PII re → Vector SOP 800/150 + Vector PADK hierarchical → RefMapper(0.0) → [RuleAuditor LLM extract raw% + Code ceiling_verify re + GraphLookup padk_graph.json] → RiskSynthesizer(0.1 + regex fallback) → Sheets 9 kolom → Router HIGH → API readback HITL → Chat Output strict JSON + cost_avoided
```

- **Agent 1 RefMapper (0.0):** Deteksi kode `SEOJK` usang vs `PADK/POJK` aktif. Status enum `DEPRECATED | ACTIVE | UNKNOWN`. Prompt terkunci di `AGENTS.md §2.1`. Input: `sop_text`. Output: `{"detected_references": [{cited_code, format_type, status, migration_required}]}`.
- **Agent 2 RuleAuditor (0.0):** LLM ekstrak `raw:"0,25%"` saja, Code node `tools/ceiling_verify.py` `extract_percent`+`verify_ceiling(re, Graph)` deterministik bandingkan ke plafon `data/kb/padk_graph.json` 0.1%/100% — violation jika `found>ceiling` (LLM dilarang hitung). Jika tanpa angka → `PERLU_VERIFIKASI_MANUAL`. Lihat `.handoff/07-deterministic-verify.md` — Code hijau visible anti-hallucination.
- **Agent 3 RiskSynthesizer (0.1):** Sintesis temuan 1+2, skor `risk_level HIGH|MEDIUM|LOW`, sitasi `PADK OJK No. 12/PADK.05/2026 Bab III Pasal 12`, draf klausul pengganti. Output strict JSON tunggal tanpa markdown, wajib disclaimer `Preliminary Advisory`. Prompt terkunci `AGENTS.md §2.3`.

Kontrak suhu `0.0 / 0.0 / 0.1` tidak bisa diubah tanpa ADR. Fallback tunggal `PERLU_VERIFIKASI_MANUAL`.

## 4. Langflow sebagai MCP Server

### 4.1 Daftar Tool (Action+Input)

| Tool MCP | Input Schema | Output |
|:---|:---|:---|
| `audit_sop_regulatory_reference` | `{"sop_text": string}` — potongan klausul SOP | `{"detected_references": [{clause_location, cited_code, format_type, status, target_migration_code, migration_required}]}` |
| `evaluate_rate_cap_substance` | `{"daily_rate_percent": number, "lock_cap_percent"?: number, "sop_text"?: string}` — bunga harian wajib, lainnya opsional | `{"substantive_evaluations": [{parameter, found_value, regulatory_ceiling, violation, breach_magnitude, legal_basis, status}]}` — jika ambigu → `status: "PERLU_VERIFIKASI_MANUAL"` |
| `generate_compliance_remediation_log` | `{"clause_id": string, "risk_level": "LOW"|"MEDIUM"|"HIGH", "remediation_text": string, "legal_basis"?: string, "export_target"?: "sheets"|"webhook"|"both"}` | `{"sheets_status": "ok|failed|skipped", "sheets_url": string, "webhook_status": "sent|skipped|failed", "reason": string}` — webhook hanya `risk_level=="HIGH"` |

Tool 3: input `sop_text` di Tool 1 & 2 tetap melalui PII Sanitizer sebelum ke LLM; Tool 3 menulis Sheets dan trigger webhook kondisional.

### 4.2 Konfigurasi MCP (JSON Contract) — Free Tier

```json
{
  "mcpServers": {
    "seith-warden-langflow": {
      "type": "local",
      "command": ["uvx", "--with", "mcp~=1.28", "mcp-proxy", "--transport", "streamablehttp", "--headers", "x-api-key", "${LANGFLOW_API_KEY}", "http://localhost:7860/api/v1/mcp/project/a760286c-db9f-406b-bb95-4d2121592e5e/streamable"],
      "enabled": true
    }
  }
}
```

Kredensial via `${env}` — `GOOGLE_API_KEY` free tier, `LANGFLOW_API_KEY` lokal. File `.opencode/opencode.json` simpan placeholder `${LANGFLOW_API_KEY}`; key plaintext lokal dev-only sampai H-1 wajib rotate.

### 4.3 Bob sebagai MCP Client — Real Connected (Dual Persona Router)

- **PDF Hal 21-26,30-31:** Bob = MCP client dual persona; Langflow = MCP server branching. Aliran: `User natural → Bob (audit_severity vs draft_remediation) → Router → MCP streamablehttp → Langflow :7860 (Graph+Code deterministik) → Sheets HITL → Chat Output → Bob → User`.
- **Setup Bob Real:** `.bob/mcp.json` `lf-seith_warden` `a760286c-.../streamable` `streamablehttp + x-api-key ${LANGFLOW_API_KEY}` → Desktop `Global Variables LANGFLOW_API_KEY` reuse (no Generate API Key) fallback tanpa header jika 0 tools. Opencode `.opencode/opencode.json` protokol identik — dev via opencode, demo via Bob `Gear→MCP`.
- **Dual Persona:** Canvas `Router audit_severity|draft_remediation` visible branching vs 3 tool flat — Technical 10% wow. Verifikasi: Flow Playground `0.25%→HIGH` vs Bob `"audit Pasal 1"+"draft perbaikan"` 2 persona → `scripts/verify.ps1 -Full` `:7860 200`. Detail: `docs/assets/bob-integration.md` real + `.handoff/08-hitl-loop.md`.

## 5. Integrasi Tool Eksternal

- **Google Sheets API (Custom Component) + HITL Readback:** Audit trail + closed loop — `Timestamp|Dokumen|Klausul|Jenis|Nilai|Batas|Risiko|Rekomendasi|Reviewer(HITL)`. Officer edit `Reviewer=REJECT` → `API Request` poll Sheets → re-route ke RiskSynthesizer + `cost_avoided docs*35jt*0.85` di Chat Output. Contoh: `...|HIGH|Ganti 0,1%|Pending→REJECT→re-draft`. Lihat `.handoff/08-hitl-loop.md` — User Impact 20%.
Contoh baris: `2026-09-26T10:00:00 | SOP-Bunga | Pasal 1 | RATE_CAP_BREACH | 0,25%/hari | 0,10%/hari | HIGH | Turunkan ke 0,1%... | Pending Review`. Service account free, `SHEETS_ID` di `.env`.
- **Webhook Notification:** `webhook.site` / Slack free webhook. Trigger conditional node — hanya `risk_level=="HIGH"` yang `sent`, `LOW/MEDIUM` → `skipped` (bukan error). `SHEETS_WEBHOOK_URL` di `.env`.

## 6. Fault Tolerance & Penanganan Galat

1. **Strict JSON Parsing Fallback:** Jika Agent 3 menghasilkan markdown di luar JSON, parser menjalankan ekstraksi regex JSON sebelum kirim ke Sheets/Webhook:
```python
import re, json
m = re.search(r'\{.*\}', text, re.S)
data = json.loads(m.group(0)) if m else {"status": "PERLU_VERIFIKASI_MANUAL"}
```
Output tetap valid JSON.
2. **Ambiguity Circuit-Breaker:** Jika potongan SOP tidak memuat angka eksplisit (misal hanya "bunga kompetitif") → agen DILARANG berasumsi → wajib `{"status": "PERLU_VERIFIKASI_MANUAL", "catatan": "Klausul ambigu: angka spesifik tidak dicantumkan."}`. Tidak ada `violation: false` dengan tebak.
3. **Isolasi Kegagalan Tool Eksternal:** Jika Sheets/Webhook timeout/gagal → `sheets_status: "failed"` / `webhook_status: "failed"` namun audit inti tetap return JSON ke console (graceful degradation, tidak putus alur). Log error tanpa bocor secret.

## 7. Matriks Env Var Free Tier

| Var | Wajib | Gratis | Catatan |
|:---|:---|:---|:---|
| `GOOGLE_API_KEY` | Ya | Free tier Google AI (Gemini Flash + text-embedding-004) | LLM + embedding |
| `LANGFLOW_API_KEY` | Ya | Lokal | MCP `x-api-key` streamablehttp |
| `VECTOR_STORE` | Tidak | `chroma-local` default gratis | `astra` opsional H2 |
| `SHEETS_ID` / `SHEETS_WEBHOOK_URL` | Tidak | Free (Sheets API + webhook.site/Slack) | Sheets + alert |
| `COMPOSIO_API_KEY` | Tidak | Opsional | Hanya jika pakai Composio berbayar |

## 8. Kontrak Flow JSON (P0 Pisah Flow)

- **File SOP:** `flows/seith_warden_flow.json` (4DCB, 10v13e, restore 8F1C clean, cost strings → `impact_note`, `hits 35jt/cost_avoided = 0`).
- **File Seller Guard:** `flows/seith_warden_seller_guard.json` (4621, 10v13e, HMAC `SELLER_REF_KEY` fail-closed via Global Variable, router BOM `\ufeff` strip + case-insensitive + `;`→`,` + header strict `order_id,gross_invoice_value` atau ERROR, bar capped `min(pct,100)/100*20 + overflow 6,60%`, banners `[DUMMY][UNVERIFIED]`).
- **Kedua flow:** Import sebagai **dua flow berbeda** di Langflow (jangan menimpa). No hardcode secret `${env}` only.
- **Verifikasi:** `tree /F` + `uv run python -m json.tool flows/seith_warden_flow.json flows/seith_warden_seller_guard.json data/kb/padk_graph.json` valid + `uv run python tools/ceiling_verify.py → ok` + `uv run ruff check .` 0 + `scripts/verify.ps1 -Full :7860 200` + `scripts/verify_seller_guard.ps1` (8 + 13 tests, SHA 4deb = oracle 66).

## 9. Handoff & Verification Gate

Awal sesi `Read docs/AGENTS.local.md + .handoff/phase-NN-topic/00-overview.md` + `skill://seith-warden-compliance` + `seith-warden-pm` gate. Akhir `skill://handoff → .handoff/phase-NN-topic/*.md` + `todowrite` trace + `✅/⚠️/🔻/♻️`.
Gate SOP: `scripts/verify.ps1` (`ruff + pii + json×4 valid + graph vs curated sync + tree 7 Zones + Bob a760286c streamablehttp no-drift`) + `ceiling_verify.py ok`.
Gate Seller Guard: `scripts/verify_seller_guard.ps1` (`ruff + 8 tests test_seller_guard + 13 tests test_e2e_seller_guard + json×6 valid + Graph 10v13e x2 + SHA 4deb = oracle 66` + HMAC fail-closed + router strict + bar capped).
`code-reviewer+security-reviewer` paralel + `refactor-cleaner fn<50` + `no-ai-slop`. Jangan fabrikasi — PM veto jika merah. Oracle hitung teks `tests/fixtures/ORACLE_manual_2026-11-01.md` (533jt 106,60%) vs engine dibanding terbalik.
