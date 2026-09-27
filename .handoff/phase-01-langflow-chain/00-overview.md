# Phase 01 — Langflow Chain & MCP Compliance Radar (Uplift v0.2.0 Graph+Code deterministic+HITL)

**Goal:** Bangun rantai 3-agent (RefMapper→RuleAuditor→RiskSynthesizer) + GraphLookup `padk_graph.json` + Code `ceiling_verify.py` deterministik + Sheets HITL REJECT→re-route + cost_avoided + dual persona Router + expose 3 tool MCP `Action+Input` + dual-vector isolated + strict JSON. Inti verifiable untuk judging 30% Innovation (Graph+deterministik+HITL) + 15% Responsible AI + 10% Technical — tidak LLM math.

## WBS (Work Breakdown Structure) — keep 1 fase, 2 batch T1 deterministik → T2 integration

| Task | Slice | Input → Output | Owner | Skill | Batch |
|:---|:---|:---|:---|:---|:---|
| 01 | RefMapper — prompt 0.0 + retriever PADK | `sop_text` → `detected_references[]` (DEPRECATED/ACTIVE) | T1 | seith-warden-compliance, tdd-guide | T1 |
| 02 | RuleAuditor — prompt 0.0 + Graph+Code | `daily_rate_percent` + Graph 0.1/100 → `substantive_evaluations[]` + `PERLU_VERIFIKASI_MANUAL` | T1 | seith-warden-compliance, tdd-guide | T1 |
| 06 | Ceiling Graph — `padk_graph.json` | `pasal12 ayat1 0.1 ayat3 100` → GraphLookup node | T1 | seith-warden-compliance | T1 |
| 07 | Deterministic Verify — `ceiling_verify.py` | `raw:"0,25%"` → Code `re` → `found>ceiling` bool + span | T1 | tdd-guide, seith-warden-compliance | T1 |
| 03 | RiskSynthesizer — prompt 0.1 + draf klausul | Gabung 01+02+06+07 → `risk_level HIGH/MEDIUM/LOW` + `draft_recommendation` | T2 | seith-warden-compliance | T2 |
| 04 | MCP Server expose — streamablehttp :7860 | `audit_sop_regulatory_reference` `evaluate_rate_cap_substance` `generate_compliance_remediation_log` + dual persona `audit_severity|draft_remediation` | T2 | build-error-resolver | T2 |
| 05 | Sheets/Webhook — conditional HIGH | `generate_compliance_remediation_log` → `sheets_status/webhook_status` (9 kolom) | T2 | docs-lookup | T2 |
| 08 | HITL Loop + cost_avoided | `Reviewer REJECT`→API readback→re-route + `cost_avoided docs*35jt*0.85` | T2 | docs-lookup | T2 |

Execution: Batch T1 (01,02,06,07) → verify `ruff/pii/ceiling_verify/json` GREEN → Batch T2 (03,04,05,08) → `verify -Full :7860 200` + `code/security reviewer` paralel.

## Dependency

- Phase 00 done + gate `scripts/verify.ps1 GREEN` lolos sebelum mulai.
- KB grounding `data/kb/padk_2026_curated.md` + `data/kb/padk_graph.json` sinkron (ceiling 0.1/100) + dummy SOP `data/sop_dummy/sop_bunga_dummy.md` 10 klausul SSOT.
- Env free tier `GOOGLE_API_KEY` (Gemini Flash + text-embedding-004) + `LANGFLOW_API_KEY` + `VECTOR_STORE=chroma-local` + `SHEETS_*` di `.env.example`.

## Arsitektur Rantai (Ref: docs/arsitektur.md §3-4 — v0.2.0 14 nodes 17 edges)

```
[ChatInput dual persona Router] → PII re `pii_sanitizer.py` NIK→rek→email → Vector SOP 800/150 + Vector PADK hierarchical
  → RefMapper 0.0 → [RuleAuditor LLM extract raw:"0,25%" + Code ceiling_verify re + GraphLookup padk_graph.json 0.1/100] → RiskSynthesizer 0.1 (regex fallback)
  → Sheets 9 kolom → Router HIGH → API readback Reviewer REJECT→re-route → Chat Output strict JSON + cost_avoided
MCP Router :7860 — audit_sop_regulatory_reference | evaluate_rate_cap_substance | generate_compliance_remediation_log
       Persona: audit_severity vs draft_remediation (Router branching visible)
Tool: Sheets (9 kolom: Timestamp|Dokumen|Klausul|Jenis|Nilai|Batas|Risiko|Rekomendasi|Reviewer) + Webhook HIGH only
Fallback: PERLU_VERIFIKASI_MANUAL bila tanpa angka | Regex JSON fallback jika markdown bocor
```

## Kontrak Prompt Terkunci (AGENTS.md §2)

- Temp `0.0 / 0.0 / 0.1` lock — tidak ubah tanpa ADR.
- Fallback tunggal `PERLU_VERIFIKASI_MANUAL` — sinkron di CONTEXT, arsitektur §6, security.
- Schemas JSON adalah hukum — `tests/test_scenarios.json` 10 skenario HIGH3 MEDIUM3 LOW2 COMPLIANT2 + `data/kb/padk_graph.json` ceiling SSOT + `tools/ceiling_verify.py` deterministic.

## DoD Phase 01 — 8 Gate AGENTS §7 + PM Veto (seith-warden-pm) — `scripts/verify.ps1 -Full`

1. `uv run ruff check .` 0 — `refactor-cleaner fn<50 file200-400 nesting≤4 no dead code` pass
2. `uv run python tools/pii_sanitizer.py → ok` (NIK→rekening→email) + `uv run python tools/ceiling_verify.py → ok` (deterministic re+Graph)
3. `python -m json.tool flows/seith_warden_flow.json` (v0.2.0 14 nodes) + `data/kb/padk_graph.json` + `tests/test_scenarios.json` + `.opencode/opencode.json` + `.bob/mcp.json` valid + `${env}` only (H-1 revoke)
4. `tree /F` 7 Zones rapih + `scripts/verify.ps1` GREEN
5. 10 skenario hijau HIGH3 MEDIUM3 LOW2 COMPLIANT2 — tiap `risk_level` + `PERLU_VERIFIKASI_MANUAL` sesuai + graph ceiling exact
6. MCP `streamablehttp :7860` 3 tools `Action+Input` + dual persona — `Invoke-WebRequest :7860/api/v1/flows 200` + Bob `.bob/mcp.json` 3 tools (fallback no-header jika Desktop no-auth)
7. `code-reviewer + security-reviewer` paralel pass (MANDATORY sebelum freeze) + `tdd-guide` edge pass + `no-ai-slop` prose pass
8. `todowrite` exactly-one `in_progress` + Accountability `✅/⚠️/🔻/♻️` + `♻️ Refactor:` lengkap per task

## Peran & Skill per Task (AGENTS §8 L1-L4 — WAJIB aktifkan sesuai kebutuhan)

- Lead T0: approve handoff, verifikasi delegasi, jaga single narrative — load `seith-warden-compliance` + `seith-warden-pm` gate
- T1 Eksekutor: Task 01,02,06,07 (RefMapper, RuleAuditor, Graph, Deterministic) — wajib `seith-warden-compliance` di awal + `tdd-guide` (10 skenario edge) + `refactor-cleaner` Boy Scout + `verification-loop` (`scripts/verify.ps1`)
- T2 Eksekutor: Task 03,04,05,08 (RiskSynthesizer, MCP dual persona, Sheets, HITL) — wajib sama + `build-error-resolver` jika Langflow fail + `docs-lookup` untuk Sheets + `code-reviewer+security-reviewer` paralel sebelum merge
- Gate wajib per task: `refactor-cleaner fn<50` WAJIB + `no-ai-slop` Tier-1 + `doc-updater` sync docs + `todowrite` exactly-one

## Handoff Output

- File di `.handoff/phase-01-langflow-chain/`: `01-refmapper.md`, `02-ruleauditor.md`, `03-risksynthesizer.md`, `04-mcp-server.md`, `05-sheets-webhook.md`, `06-ceiling-graph.md`, `07-deterministic-verify.md`, `08-hitl-loop.md`.
- Tiap task file wajib: Goal, Prompt terkunci, I/O JSON example, Verification command + output nyata, Refactor note (`♻️`) + `✅/⚠️/🔻/♻️`.

## Bob Real Connected (PDF Hal 4,21,30 — Real via .bob/mcp.json)

- Status: Bob REAL CONNECTED — `.bob/mcp.json` `lf-seith_warden` `a760286c-db9f-406b-bb95-4d2121592e5e/streamable` `streamablehttp + x-api-key` → Langflow Desktop `:7860` — verifikasi `Invoke-WebRequest :7860/api/v1/flows 200`
- Opencode dev proxy `.opencode/opencode.json` protokol identik — dev via opencode cepat, demo juri via Bob `Gear→MCP` natural language dual persona (`audit_severity` vs `draft_remediation`). Setup detail `docs/assets/bob-integration.md` real — Desktop via `Global Variables LANGFLOW_API_KEY` (no Generate API Key), fallback tanpa header jika 0 tools.
- DoD: Bob `Gear→MCP` 3 tools `Action+Input` hijau + chat `audit Pasal 1 0,25%` → `HIGH+PADK 12:1` = Playground + chat `draft perbaikan Pasal 1` → klausul baru

## Referensi

- `AGENTS.md` §2-4 (prompt & MCP contract) — `docs/arsitektur.md` §2-6 (Graph+Code+HITL v0.2.0) + `docs/assets/bob-integration.md` — `docs/CONTEXT.md` (lexicon) — `docs/setup.md` (uv run) — `data/kb/padk_2026_curated.md` + `data/kb/padk_graph.json` — `tools/ceiling_verify.py` — `tests/test_scenarios.json` — PDF `docs/assets/Hacktiv8 Hackathon National - Google Slide.pdf`.
