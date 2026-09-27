# Phase 00 — Agents Sync & Project Hardening (Rumus Anti-Slop) — Done

**Goal:** AGENTS.md 10§ full ID pakai rumus SEITH-MARKET-IDX (anti AI generik/slop, flow jelas, no bug logic) + 7 Zones lock rapih + skill SSOT + PM `seith-warden-pm` + scaffolding siap implementasi.

## WBS

| Task | Slice | Owner | Status |
|:---|:---|:---|:---|
| 01 | Backup & rewrite AGENTS.md 10§ (Identity, Snapshot, Arch, Hard Rules, Env, Boy Scout, Contract, DoD, Delegasi) | T0 Lead | Done 2026-09-26 |
| 02 | Buat skill `seith-warden-compliance` SSOT + PM `seith-warden-pm` di `.opencode/agents/` | T0 | Done |
| 03 | Rapikan 7 Zones: `docs/` SSOT, `flows/`, `tools/`, `data/`, `tests/fixtures`, `scripts/`, `.handoff/phase-NN`, `.opencode` + GitHub `public SEITH-WARDEN` + CI gate-only `.github/workflows/ci.yml` | T0 | Done |
| 04 | Sync `docs/arsitektur.md` (Graph+Code+HITL v0.2.0), `docs/security.md`, `docs/AGENTS.local.md`, `docs/CONTEXT.md`, `docs/setup.md`, `docs/assets/bob-integration.md` real + README bilingual | T0 | Done |
| 05 | Scaffold handoff phase 00 & template, verify tree+ruff+pii+json+ceiling_verify+graph | T0 | Done 2026-09-27 `verify.ps1 GREEN` |

## Dependency
Phase 00 adalah gate sebelum Phase 01 (Langflow chain uplift v0.2.0). Tanpa AGENTS lock, Phase 01 rawan slop dan wiring salah.

## DoD Phase 00 — GREEN
- [x] AGENTS.md 10§ lengkap, Tier-0 9 rules, 7 Zones, Boy Scout, Contract, DoD 8 gate + PM `seith-warden-pm` veto
- [x] Skill `seith-warden-compliance` SSOT + `.opencode/agents/seith-warden-pm` gate — `skill://seith-warden-compliance` WAJIB awal T0/T1/T2
- [x] `docs/` berisi prd/arsitektur (v0.2.0 Graph+Code+HITL)/security/CONTEXT/setup/hacktiv8/ide/assets/bob-integration real + decisions/ADR-001
- [x] Root bersih: hanya AGENTS.md, README.md, .env.example, .gitignore, pyproject.toml, opencode.json (7 Zones di luar docs)
- [x] `scripts/verify.ps1 → GATE GREEN` — `uv run ruff check . 0` + `uv run python tools/pii_sanitizer.py → ok` + `ceiling_verify.py → ok` + `json.tool flows/seith_warden_flow.json tests/test_scenarios.json data/kb/padk_graph.json .opencode/opencode.json .bob/mcp.json valid` + `tree /F 7 zones` + `handoff 14 file` + `Bob a760286c streamablehttp no-drift` + `CI .github/workflows/ci.yml gate-only`
- [x] GitHub `main` baseline 64a307a + uplift 75c5999 — public SEITH-WARDEN siap `git push -u origin main`

## Peran & Skill
- Lead T0: `seith-warden-compliance` + `seith-warden-pm` + `understand`
- Reviewer: `code-reviewer` + `security-reviewer` paralel (MANDATORY sebelum freeze) — Bob real connected `.bob/mcp.json`
- Refactor: `refactor-cleaner` WAJIB pasca-phase — `uv run ruff check --fix`, `fn<50`

## Next
Phase 01 — Langflow Chain uplift v0.2.0 (RefMapper, RuleAuditor+Graph+Code, RiskSynthesizer, MCP dual persona, Sheets HITL) + enkel 10 skenario — keep 1 fase, 2 batch T1 deterministik → T2 integration — `worktree handoff/01-langflow-chain`.
