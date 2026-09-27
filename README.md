# SEITH-WARDEN — PADK Migration & Rate-Cap Compliance Radar

**ID:** AI Agent audit kepatuhan OJK otomatis — deteksi klausul SOP usang (SEOJK → PADK) + pelanggaran batas bunga 0,1%/hari & Lock Cap 100% pada SOP fintech lending/BNPL. Multi-agent Langflow + MCP Server `Action+Input` + Sheets/Webhook. Potong audit manual 14 hari menjadi hitungan jam.

**EN:** Automated OJK compliance AI — detects deprecated SEOJK→PADK references + 0.1%/day & 100% Lock Cap breaches in fintech SOPs. Langflow multi-agent chain + MCP `Action+Input` + Sheets/Webhook. Cuts 14-day manual audit to hours.

> Stack gratis / Free stack: Gemini 1.5 Flash (free tier) + `text-embedding-004` + `chroma-local` + Langflow `:7860` + Sheets API free + webhook.site. No paid Astra/Composio required for MVP.

> **Integrasi / Integration:** Langflow + IBM Bob via MCP `streamablehttp :7860` — Bob formalitas (protocol sama dengan opencode), runtime harian `opencode`. Lihat `docs/assets/bob-integration.md` (PDF Hal 21,30).

## Quick Start | Mulai Cepat

```bash
cp .env.example .env  # isi GOOGLE_API_KEY & LANGFLOW_API_KEY
uv sync
uv run ruff check .
uv run python tools/pii_sanitizer.py  # → ok
uv run python -m json.tool tests/test_scenarios.json
uv run langflow run --host 127.0.0.1 --port 7860
```

**ID:** Cek MCP: `Invoke-WebRequest http://localhost:7860/api/v1/flows -Headers @{"x-api-key"="$env:LANGFLOW_API_KEY"}` harus 200 sebelum demo.
**EN:** MCP check must return 200 before demo.

## Struktur | Structure (7 Zones Lock — AGENTS.md §3c)

```
flows/              Langflow flow JSON (seith_warden_flow.json)
tools/              Python uv — pii_sanitizer.py + custom Sheets/Webhook
data/kb/            KB PADK curated (grounding SSOT)
data/sop_dummy/     10 klausul dummy (HIGH/MEDIUM/LOW/COMPLIANT)
tests/              test_scenarios.json (10 skenario matrix)
docs/               prd/arsitektur/security/CONTEXT/setup/adr/hacktiv8
.handoff/phase-NN/  Governance per fase (00-overview.md + tasks)
scripts/.opencode/  Ops & harness + skill seith-warden-compliance
```

**ID:** Cross-zona import liar dilarang — `tools/` tidak import `flows/`, `data/` tidak berisi kode.
**EN:** Cross-zone imports forbidden.

## Dokumen | Docs

| Dokumen | Isi |
|:---|:---|
| `AGENTS.md` | Kontrak 3-agent + MCP + Tier-0 + DoD |
| `docs/arsitektur.md` | Arsitektur Langflow+MCP+dual-vector+env matrix |
| `docs/security.md` | Responsible AI, PII strip, HITL, fallback |
| `docs/CONTEXT.md` | Lexicon SEOJK/PADK/Lock Cap/P2SK |
| `docs/setup.md` | Langkah setup lengkap |
| `docs/prd.md` | Requirement + monetisasi SaaS Rp4,9/12,5/24,9jt |
| `docs/hacktiv8_hackathon_national.md` | Checklist submission 4 Okt 2026 |
| `docs/assets/bob-integration.md` | Bob MCP client formalitas — protocol sama dengan opencode (PDF Hal 56-60) |
| `docs/assets/Hacktiv8...pdf` | Slide resmi 88 hal (SSOT kompetisi) |

## Submission (4 Okt 2026) | Pengumpulan

**ID:** Tim solo + sertifikat IBM SkillsBuild | Overview | Technical Proof (`flows/seith_warden_flow.json` + `docs/arsitektur.md` + MCP + log JSON) | Deck 10 slide + 5 screenshot | Public link `bit.ly/submit-hackathon`.
**EN:** Solo team + certificate | Overview | Technical Proof | Deck + 5 screenshots | Public link.

**Secret Policy:** Dev lokal boleh plaintext `.opencode/opencode.json` sementara — **wajib revoke H-1 (2026-10-03)** sebelum public submit. Lihat `docs/AGENTS.local.md §4`.

**Responsible AI 15%:** PII strip `re` NIK→rekening→email + HITL `Preliminary Advisory` + `PERLU_VERIFIKASI_MANUAL` + grounding PADK `data/kb/padk_2026_curated.md` — lihat `docs/security.md` Hal 81-85.
