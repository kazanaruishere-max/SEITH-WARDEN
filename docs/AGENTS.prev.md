# SPESIFIKASI DETAIL AI AGENT: SEITH - WARDEN | AI AGENT SPECIFICATION
**Sistem / System:** Supervisory Engine for Institutional Trust & Hazard-mitigation — Workflow Automation & Regulatory Detection Engine Network  
**Platform Eksekusi / Runtime:** Langflow Chained LLM Agents & MCP Server  
**Versi / Version:** 1.0.0 MVP — Bilingual ID | EN (Free Tier Stack)

> **ID:** Dokumen ini adalah sumber kebenaran tunggal untuk 3-agent chain dan kontrak MCP. Semua perubahan prompt/temperature/schema wajib dicatat di `docs/AGENTS.local.md` Decision Log.
> **EN:** Single source of truth for 3-agent chain and MCP contract. All prompt/temperature/schema changes must be logged in `docs/AGENTS.local.md`.

---

## 1. Topologi Multi-Agent & Pembagian Peran | Multi-Agent Topology & Role Split

**ID:** SEITH-WARDEN memecah audit menjadi 3 agen sekuensial untuk mencegah *cognitive overload* dan memastikan output JSON terverifikasi per tahap.
**EN:** Splits compliance audit into 3 sequential specialists to prevent overload and guarantee verifiable JSON per stage.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        ALUR KERJA MULTI-AGENT BERANTAI | CHAINED FLOW                  │
│   [Klausul SOP / SOP Clause] ──► [AGENT 1: SEITH-RefMapper]                            │
│                            │                                                           │
│                            ▼ (JSON Citations Map)                                      │
│                     [AGENT 2: SEITH-RuleAuditor] ◄── [Knowledge Base PADK 2026]        │
│                            │                                                           │
│                            ▼ (JSON Gap Analysis)                                       │
│                     [AGENT 3: WARDEN-RiskSynthesizer]                                  │
│                            │                                                           │
│                            ▼ (Strict Audit Report JSON)                                │
│                     [Eksekusi Tool MCP / Sheets / Webhook | MCP Tools Execution]       │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

**Kontrak Suhu | Temperature Contract (LOCKED):** Agent 1 `0.0` — Agent 2 `0.0` — Agent 3 `0.1`. Dilarang ubah tanpa ADR.

**Fallback Tunggal | Single Fallback Term:** `PERLU_VERIFIKASI_MANUAL` — dipakai di semua agen bila angka tidak eksplisit atau konteks ambigu. **EN:** Use this exact string when SOP lacks explicit numeric rate; never guess, never hallucinate.

---

## 2. Spesifikasi Teknis Tiap Agen | Per-Agent Technical Spec

### 2.1 AGENT 1: SEITH-RefMapper (Regulation Reference Checker) | Pemeta Rujukan Regulasi

* **Tujuan / Goal:** Temukan rujukan SEOJK usang vs PADK/POJK aktif, petakan migrasi 2026. **EN:** Detect deprecated SEOJK vs active PADK/POJK.
* **LLM:** Google Gemini 1.5 Flash (free tier) / Pro — `temperature: 0.0` deterministik mutlak.

#### System Prompt (Agent 1) — LOCKED:
```text
Kamu adalah SEITH-RefMapper, AI auditor spesialis pemetaan instrumen regulasi finansial OJK Indonesia.
Tugas utamamu adalah memindai teks Standard Operating Procedure (SOP) internal dan mengekstrak seluruh rujukan peraturan yang disebutkan.
Pedoman Eksekusi:
1. Identifikasi setiap penyebutan kode regulasi, seperti SEOJK, POJK, atau PADK.
2. Tentukan status: "DEPRECATED" (SEOJK wajib migrasi PADK 2026), "ACTIVE" (PADK/POJK berlaku), "UNKNOWN" (format tidak valid).
3. Petakan kode lama ke padanan PADK berdasarkan knowledge base.
4. JANGAN analisis angka/suku bunga; fokus HANYA referensi legalitas.
5. Keluaran HARUS list objek JSON valid.
6. Jika tidak ada rujukan, kembalikan {"detected_references": []}.
```

#### Schema I/O (Agent 1):
```json
{
  "detected_references": [
    {
      "clause_location": "Paragraf 1",
      "cited_code": "19/SEOJK.05/2023",
      "format_type": "SEOJK",
      "status": "DEPRECATED",
      "target_migration_code": "PADK OJK 2026",
      "migration_required": true
    }
  ]
}
```

### 2.2 AGENT 2: SEITH-RuleAuditor (Substantive Gap Analyzer) | Auditor Substansi Numerik

* **Tujuan / Goal:** Ekstrak parameter finansial (bunga harian, denda, biaya admin, lock cap) dan bandingkan ke batas PADK 2026. **EN:** Extract financial params and compare to PADK ceilings.
* **LLM:** Google Gemini 1.5 Flash — `temperature: 0.0`

#### System Prompt (Agent 2) — LOCKED:
```text
Kamu adalah SEITH-RuleAuditor, auditor kepatuhan finansial kuantitatif fintech lending/BNPL.
Aturan Kunci PADK 2026:
1. Bunga konsumtif maks 0,1%/hari; produktif maks 0,2%/hari.
2. Lock Cap 100%: total bunga+denda+biaya ≤100% pokok.
3. Dilarang bunga berbunga pada denda.
Instruksi:
- Ekstrak angka eksplisit. Jika SOP > batas → violation=true.
- Jika SOP TIDAK cantumkan angka eksplisit (misal "bunga kompetitif") → status="PERLU_VERIFIKASI_MANUAL". DILARANG MENEBAK.
- Kembalikan JSON terstruktur.
```

#### Schema Output (Agent 2):
```json
{
  "substantive_evaluations": [
    {
      "parameter": "daily_interest_rate_consumptive",
      "found_value": 0.0025,
      "found_value_display": "0.25%/hari",
      "regulatory_ceiling": 0.0010,
      "regulatory_ceiling_display": "0.10%/hari",
      "violation": true,
      "breach_magnitude": "+0.15%/hari",
      "legal_basis": "PADK OJK 2026 tentang Batas Maksimum Manfaat Ekonomi",
      "status": "VIOLATION"
    }
  ]
}
```
**Status enum Agent 2:** `VIOLATION` | `COMPLIANT` | `PERLU_VERIFIKASI_MANUAL`

### 2.3 AGENT 3: WARDEN-RiskSynthesizer (Risk & Recommendation Drafter) | Sintesis Risiko & Rekomendasi

* **Tujuan / Goal:** Gabungkan temuan Agent 1+2, hitung severity, draf klausul pengganti legal drafting. **EN:** Synthesize findings, score severity, draft replacement clause.
* **LLM:** Google Gemini 1.5 Flash — `temperature: 0.1`

#### System Prompt (Agent 3) — LOCKED:
```text
Kamu adalah WARDEN-RiskSynthesizer, Lead Compliance & Risk Drafter.
Kriteria Severity:
- HIGH: pelanggaran numerik (bunga>0,1%/hari, Lock Cap>100%, denda ganda) → risiko pembekuan izin.
- MEDIUM: referensi SEOJK tanpa padanan PADK, angka belum terbukti melanggar.
- LOW: inkonsistensi istilah minor tanpa dampak finansial.
Tugas: tulis draf klausul pengganti formal Indonesia + klausul mitigasi 100% cap. Output HARUS JSON tunggal tanpa markdown di luar JSON. Sertakan disclaimer Preliminary Advisory.
```

#### Schema Output Final (Agent 3):
```json
{
  "audit_summary": {
    "clause_identifier": "SOP-PINJAMAN-KONSUMTIF-PASAL-4",
    "overall_status": "NON_COMPLIANT",
    "risk_level": "HIGH",
    "requires_escalation": true
  },
  "findings": [
    {
      "issue_category": "RATE_CAP_BREACH",
      "description": "Bunga 0,25%/hari melampaui plafon 0,1%/hari PADK 2026.",
      "severity": "HIGH",
      "legal_reference": "PADK OJK 2026 Pasal 12 Ayat 1"
    }
  ],
  "draft_recommendation": {
    "proposed_clause_replacement": "Tingkat suku bunga harian ... paling banyak 0,1% per hari kalender ... total akumulasi ≤100% pokok sesuai PADK OJK 2026.",
    "action_plan": "Terbitkan SK Direksi revisi tabel bunga dan update template Perjanjian Pendanaan.",
    "disclaimer": "Preliminary Advisory — wajib validasi Compliance Officer sebelum implementasi."
  }
}
```

---

## 3. Spesifikasi Kontrak Tool MCP Server | MCP Server Tool Contract

**ID:** Diexpose via Langflow MCP `streamablehttp` di `127.0.0.1:7860`. Penamaan wajib `Action+Input`.
**EN:** Exposed via Langflow MCP streamablehttp at 127.0.0.1:7860. Naming must be `Action+Input`.

### Tool 1: `audit_sop_regulatory_reference` — Periksa rujukan SEOJK→PADK | Check SEOJK→PADK refs
* **Input Schema:**
```json
{ "type": "object", "properties": { "sop_text": { "type": "string", "description": "Potongan klausul SOP" } }, "required": ["sop_text"] }
```
* **Output:** `{"detected_references": [...]}` sesuai Agent 1. **EN:** Mapping old→new code + migration_required flag.

### Tool 2: `evaluate_rate_cap_substance` — Uji kepatuhan bunga & Lock Cap | Test rate & cap substance
* **Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "daily_rate_percent": { "type": "number", "description": "Bunga harian di SOP, mis 0.25" },
    "lock_cap_percent": { "type": "number", "description": "Total akumulasi biaya, mis 100" },
    "sop_text": { "type": "string", "description": "Konteks klausul (opsional, untuk grounding)" }
  },
  "required": ["daily_rate_percent"]
}
```
* **Output:** `{"substantive_evaluations": [...]}` dengan `violation` + `status` enum. Jika input ambigu → `PERLU_VERIFIKASI_MANUAL`.

### Tool 3: `generate_compliance_remediation_log` — Rekam log & eskalasi | Log & escalate
* **Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "clause_id": { "type": "string" },
    "risk_level": { "type": "string", "enum": ["LOW", "MEDIUM", "HIGH"] },
    "remediation_text": { "type": "string" },
    "legal_basis": { "type": "string" },
    "export_target": { "type": "string", "enum": ["sheets", "webhook", "both"], "default": "both" }
  },
  "required": ["clause_id", "risk_level", "remediation_text"]
}
```
* **Output:** `{"sheets_status": "ok|failed", "sheets_url": "...", "webhook_status": "sent|skipped|failed", "reason": "..."}`
* **Trigger Webhook:** Hanya jika `risk_level=="HIGH"` (conditional node). **EN:** Webhook fires only on HIGH.

---

## 4. Handoff & Verification Gate | Gerbang Serah-Terima & Verifikasi

**ID:**
- Awal sesi: baca `docs/AGENTS.local.md` + `.handoff/latest.md`.
- Akhir sesi/topik: jalankan `skill://handoff` → tulis `.handoff/<YYYY-MM-DD>.md` (state, next step, blok Accountability).
- Klaim "selesai" HANYA setelah `build/lint/test` relevan lulus (laporkan perintah+output asli, jangan fabrikasi).
- Free stack gate: `uv run ruff check .` + `tree` verifikasi struktur + 10 skenario JSON valid.

**EN:**
- Session start: read `docs/AGENTS.local.md` + `.handoff/latest.md`.
- Session end: run `skill://handoff` → `.handoff/<YYYY-MM-DD>.md`.
- No "done" without passing build/lint/test with real output.
- Free gate: ruff check + tree + 10 JSON scenarios pass.

**Blok Accountability wajib per task yang ubah file/jalankan perintah:**
`✅ Terverifikasi: <apa> + <perintah> → <hasil> | ⚠️ Belum: <asumsi> | 🔻 Risiko: <1-2> — deteksi: <cara>`

**Secret Policy (Free & Solo):** Kredensial via env var (`GOOGLE_API_KEY`, `LANGFLOW_API_KEY`, `SHEETS_*`). File `opencode.json` simpan `${env}` placeholder; key lokal plaintext diizinkan dev-only sampai H-1 (2026-10-03) wajib revoke sebelum submit public link. **EN:** Env-only before public submission.

---

## 5. Referensi Cepat Env Free Tier | Free Tier Env Quick Ref

| Var | Penggunaan | Default Gratis |
|-----|------------|----------------|
| `GOOGLE_API_KEY` | Gemini Flash + text-embedding-004 | Free tier Google AI |
| `LANGFLOW_API_KEY` | MCP streamablehttp `x-api-key` | Local, no cost |
| `VECTOR_STORE` | `chroma-local` / `faiss` (free) vs `astra` | `chroma-local` |
| `SHEETS_WEBHOOK_URL` | `webhook.site` / Slack free webhook | Free |
