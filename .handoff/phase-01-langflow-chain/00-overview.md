# Phase 01 — Langflow Chain & MCP Compliance Radar

**Goal:** Bangun rantai 3-agent (RefMapper→RuleAuditor→RiskSynthesizer) di Langflow + expose 3 tool MCP `Action+Input` + dual-vector isolated + strict JSON. Phase ini adalah inti verifiable untuk judging 10% Technical + 15% Responsible AI. Belum eksekusi — hanya kontrak handoff agar T1/T2 langsung implement tanpa tanya ulang.

## WBS (Work Breakdown Structure)

| Task | Slice | Input → Output | Owner | Skill |
|:---|:---|:---|:---|:---|
| 01 | RefMapper — prompt 0.0 + retriever PADK | `sop_text` → `detected_references[]` (DEPRECATED/ACTIVE) | T1 | seith-warden-compliance, tdd-guide |
| 02 | RuleAuditor — prompt 0.0 + evaluasi 0,1%/Lock100% | `daily_rate_percent` → `substantive_evaluations[]` + `PERLU_VERIFIKASI_MANUAL` | T1 | seith-warden-compliance |
| 03 | RiskSynthesizer — prompt 0.1 + draf klausul | Gabung 01+02 → `risk_level HIGH/MEDIUM/LOW` + `draft_recommendation` | T2 | seith-warden-compliance |
| 04 | MCP Server expose — streamablehttp :7860 | `audit_sop_regulatory_reference` `evaluate_rate_cap_substance` `generate_compliance_remediation_log` | T2 | build-error-resolver |
| 05 | Tool-calling Sheets/Webhook — conditional HIGH | `generate_compliance_remediation_log` → `sheets_status/webhook_status` (Sheets 9 kolom, webhook HIGH only) | T2 | docs-lookup |

## Dependency

- Phase 00 (AGENTS 10§ + 7 Zones + skill SSOT + skeleton `flows/seith_warden_flow.json`) harus selesai dan lolos gate sebelum mulai.
- KB grounding `data/kb/padk_2026_curated.md` dan dummy SOP `data/sop_dummy/sop_bunga_dummy.md` sudah tersedia sebagai SSOT sitasi.
- Env free tier `GOOGLE_API_KEY` (Gemini Flash + text-embedding-004) + `LANGFLOW_API_KEY` + `VECTOR_STORE=chroma-local` sudah di `.env.example`.

## Arsitektur Rantai (Ref: docs/arsitektur.md §3-4)

```
[SOP Clause + RAG SOP 800/150] → RefMapper (0.0) → {detected_references}
[RAG PADK hierarchical Bab→Pasal→Ayat] ───────────→ RuleAuditor (0.0) → {substantive_evaluations} → RiskSynthesizer (0.1) → Final JSON
MCP Router :7860 — audit_sop_regulatory_reference | evaluate_rate_cap_substance | generate_compliance_remediation_log
Tool: Sheets (9 kolom: Timestamp|Dokumen|Klausul|Jenis|Nilai|Batas|Risiko|Rekomendasi|Reviewer) + Webhook (HIGH only)
Fallback: PERLU_VERIFIKASI_MANUAL bila tanpa angka eksplisit | Regex JSON fallback jika markdown bocor
```

## Kontrak Prompt Terkunci (AGENTS.md §2)

- Temp `0.0 / 0.0 / 0.1` lock — tidak ubah tanpa ADR.
- Fallback tunggal `PERLU_VERIFIKASI_MANUAL` — sinkron di CONTEXT, arsitektur §6, security.
- Schemas JSON adalah hukum — lihat `tests/test_scenarios.json` 10 skenario (HIGH 3, MEDIUM 3, LOW 2, COMPLIANT 2).

## DoD Phase 01 — 8 Gate AGENTS §7 + PM Veto (seith-warden-pm) — `scripts/verify.ps1 -Full`

1. `uv run ruff check .` 0 — `refactor-cleaner fn<50 file200-400 nesting≤4 no dead code` pass
2. `uv run python tools/pii_sanitizer.py → ok` (NIK→rekening→email)
3. `python -m json.tool flows/seith_warden_flow.json` + `tests/test_scenarios.json` + `.opencode/opencode.json` + `.bob/mcp.json` valid + `${env}` only (H-1 revoke)
4. `tree /F` 7 Zones rapih + `scripts/verify.ps1` GREEN
5. 10 skenario hijau HIGH3 MEDIUM3 LOW2 COMPLIANT2 — tiap `risk_level` + `PERLU_VERIFIKASI_MANUAL` sesuai
6. MCP `streamablehttp :7860` 3 tools `Action+Input` — `Invoke-WebRequest :7860/api/v1/flows 200` + Bob `.bob/mcp.json` discovery 3 tools (fallback no-header jika Desktop no-auth)
7. `code-reviewer + security-reviewer` paralel pass (MANDATORY) + `tdd-guide` edge pass + `no-ai-slop` prose pass
8. `todowrite` exactly-one `in_progress` + Accountability `✅/⚠️/🔻/♻️` + `♻️ Refactor:` lengkap per task

## Peran & Skill per Task (AGENTS §8 L1-L4 — WAJIB aktifkan sesuai kebutuhan)

- Lead T0: approve handoff, verifikasi delegasi, jaga single narrative — load `seith-warden-compliance` + `seith-warden-pm` gate
- T1 Eksekutor: Task 01-02 (RefMapper, RuleAuditor) — wajib `seith-warden-compliance` di awal + `tdd-guide` (10 skenario edge) + `refactor-cleaner` Boy Scout + `verification-loop` (`scripts/verify.ps1`)
- T2 Eksekutor: Task 03-05 (RiskSynthesizer, MCP, Sheets/Webhook) — wajib sama + `build-error-resolver` jika Langflow fail + `docs-lookup` untuk Sheets
- Gate wajib per task: `code-reviewer + security-reviewer` paralel sebelum freeze + `refactor-cleaner fn<50` WAJIB + `no-ai-slop` Tier-1 + `doc-updater` sync docs + `todowrite` exactly-one

## Handoff Output

- File di `.handoff/phase-01-langflow-chain/`: `01-refmapper.md`, `02-ruleauditor.md`, `03-risksynthesizer.md`, `04-mcp-server.md`, `05-sheets-webhook.md`.
- Tiap task file wajib: Goal, Prompt terkunci, Input/Output JSON example, Verification command + output nyata, Refactor note.

## Bob Real Connected (PDF Hal 4,21,30 — Real via .bob/mcp.json)

- Status: Bob REAL CONNECTED — `.bob/mcp.json` `lf-seith_warden` `a760286c-.../streamable` `streamablehttp + x-api-key` → Langflow Desktop `:7860` — verifikasi `Invoke-WebRequest :7860/api/v1/flows 200`
- Opencode dev proxy `.opencode/opencode.json` protokol identik — dev via opencode cepat, demo juri via Bob `Gear→MCP` natural language. Setup detail `docs/assets/bob-integration.md` real — Desktop via `Global Variables LANGFLOW_API_KEY` (no Generate API Key), fallback tanpa header jika 0 tools.
- DoD: Bob `Gear→MCP` 3 tools `Action+Input` hijau + chat `audit Pasal 1 0,25%` → `HIGH+PADK 12:1` = Playground

## Referensi

- `AGENTS.md` §2-4 (prompt & MCP contract) — `docs/arsitektur.md` §2-6 + `docs/assets/bob-integration.md` — `docs/CONTEXT.md` (lexicon) — `docs/setup.md` (uv run) — `data/kb/padk_2026_curated.md` (grounding) — PDF `docs/assets/Hacktiv8 Hackathon National - Google Slide.pdf`.
