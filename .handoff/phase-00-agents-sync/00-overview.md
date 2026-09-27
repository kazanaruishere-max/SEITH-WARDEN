# Phase 00 — Agents Sync & Project Hardening (Rumus Anti-Slop)

**Goal:** AGENTS.md 10§ full ID pakai rumus SEITH-MARKET-IDX (anti AI generik/slop, flow jelas, no bug logic) + 7 Zones lock rapih + skill SSOT + scaffolding siap implementasi.

## WBS

| Task | Slice | Owner | Status |
|:---|:---|:---|:---|
| 01 | Backup & rewrite AGENTS.md 10§ (Identity, Snapshot, Arch, Hard Rules, Env, Boy Scout, Contract, DoD, Delegasi) | T0 Lead | Done 2026-09-26 |
| 02 | Buat skill `seith-warden-compliance` SSOT di `.opencode/skills/` | T0 | Done |
| 03 | Rapikan 7 Zones: `docs/` SSOT, `flows/`, `tools/`, `data/`, `tests/fixtures`, `scripts/`, `.handoff/phase-NN`, `.opencode` | T0 | Done |
| 04 | Sync `docs/arsitektur.md`, `docs/security.md`, `docs/AGENTS.local.md`, `docs/CONTEXT.md` full ID + README bilingual | T0 | Done |
| 05 | Scaffold handoff phase 00 & template, verify tree+ruff+pii+json | T0 | In progress |

## Dependency
Phase 00 adalah gate sebelum Phase 01 (Langflow chain). Tanpa AGENTS lock, Phase 01 rawan slop dan wiring salah.

## DoD Phase 00
- [x] AGENTS.md 193→~350 baris, 10§ lengkap, Tier-0 9 rules, 7 Zones, Boy Scout, Contract, DoD 8 gate
- [x] Skill `seith-warden-compliance` ter-load via `skill://seith-warden-compliance`
- [x] `docs/` berisi prd/arsitektur/security/CONTEXT/setup/hacktiv8/ide + decisions/ADR-001
- [x] Root bersih: hanya AGENTS.md, README.md, .env.example, .gitignore, opencode.json (7 Zones di luar docs)
- [ ] `tree /F` 7 zones rapih + `uv run ruff check .` 0 + `uv run python tools/pii_sanitizer.py → ok` + `json.tool tests/test_scenarios.json` valid

## Peran & Skill
- Lead T0: `seith-warden-compliance` + `understand`
- Reviewer: `code-reviewer` + `security-reviewer` (post-phase 00)
- Refactor: `refactor-cleaner` WAJIB pasca-phase

## Next
Phase 01 — Langflow Chain (RefMapper→RuleAuditor→RiskSynthesizer) + MCP Action+Input + 10 skenario.
