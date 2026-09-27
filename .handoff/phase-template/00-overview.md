# Phase NN — <topic> — <1 baris goal kaitkan judging 30/20/20/15/10/5>

**Goal:** <tujuan fase 1 baris, kaitkan bobot judging + problem/Bob/inovasi>

## WBS

| Task | Slice | Input → Output | Owner | Skill | Status |
|:---|:---|:---|:---|:---|:---|
| 01 | `<slice verb>` | `<input> → <output JSON>` | T1/T2 | seith-warden-compliance + <skill wajib> | pending |
| 02 | `<slice>` | | T1/T2 | | pending |

- Skill wajib isi per L1-L4 AGENTS §8: L2 `code-reviewer+security-reviewer+tdd-guide`, L3 `doc-updater+handoff+verification-loop`, L4 `refactor-cleaner` WAJIB + `build-error-resolver` jika Langflow
- Dual-agent sebut eksplisit jika sentuh MCP: `Bob Gear→MCP lf-seith_warden` vs `opencode .opencode/opencode.json` protokol `a760286c-.../streamable`

## Dependency

- Phase NN-1 harus selesai + gate PM lolos sebelum mulai.
- SSOT: `AGENTS.md §X` + `docs/arsitektur.md §Y` + `data/kb/padk_2026_curated.md` + `tests/test_scenarios.json` + `docs/assets/bob-integration.md` real jika MCP

## Arsitektur Slice

```
<input> → <component> (temp X.X) → <output> → <next>
PII: sanitize_sop_text NIK→rek→email | Vector: SOP 800/150 vs PADK hierarchical
MCP: tool_name(Action+Input) jika ada | Fallback: PERLU_VERIFIKASI_MANUAL jika ambigu | Sheets 9 kolom + webhook HIGH only
Never kill :7860
```

## Kontrak Prompt Terkunci (jika LLM)

- Temp `0.0/0.0/0.1` lock — ubah butuh ADR.
- Strict JSON + `Preliminary Advisory` disclaimer — regex fallback jika markdown bocor. Grounded `data/kb/padk_2026_curated.md`.

## DoD Phase NN — 8 Gate AGENTS §7 + PM Veto (§8 seith-warden-pm)

1. `uv run ruff check .` 0
2. `uv run python tools/pii_sanitizer.py → ok` (NIK→rekening→email)
3. `python -m json.tool flows/seith_warden_flow.json` + `tests/test_scenarios.json` + `.opencode/opencode.json` + `.bob/mcp.json` valid + `${env}` only
4. `tree /F` 7 Zones rapih — no file liar, cross-zone import benar
5. Skenario matrix HIGH/MEDIUM/LOW/PERLU_VERIFIKASI_MANUAL/COMPLIANT sesuai — Bob 3 tools `Action+Input` jika MCP
6. MCP `:7860` 200 `Invoke-WebRequest http://localhost:7860/api/v1/flows` + `a760286c-.../streamable` discovery jika expose
7. Dual-review `code-reviewer + security-reviewer` paralel pass (MANDATORY sebelum freeze) + `tdd-guide` 10 skenario edge pass
8. `refactor-cleaner` fn<50 file200-400 nesting≤4 no dead code pass + `no-ai-slop` prose pass + `todowrite` exactly-one + Accountability `✅/⚠️/🔻/♻️`

## Peran & Skill per Task

- T0 Lead: approve handoff, verifikasi delegasi, jaga single narrative
- T1/T2: implement slice — wajib `skill://seith-warden-compliance` di awal + `todowrite` + `verification-loop`
- Gate: `refactor-cleaner` Boy Scout §5b pasca tiap task + PM veto jika merah

## Handoff Output

- File di `.handoff/phase-NN-topic/`: `01-*.md` per task slice. Tiap file wajib: Goal, Prompt terkunci/I/O JSON example, Verify cmd+output nyata (`ruff/pii/json/tree`), Refactor `♻️`, Accountability `✅/⚠️/🔻/♻️` + `todowrite` trace
- Commit `type: desc` + no force push + `/.wt/` gitignore

## Referensi

- `AGENTS.md` §X + `.opencode/skills/seith-warden-compliance/SKILL.md` + `.opencode/agents/seith-warden-pm/SKILL.md` — `docs/arsitektur.md` §Y — `docs/CONTEXT.md` — `docs/security.md Hal 81-85` — `docs/assets/bob-integration.md` real — `tests/test_scenarios.json` — PDF Hal 4,21,30
