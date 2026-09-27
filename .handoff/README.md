# Handoff Governance — SEITH-WARDEN

**Aturan (AGENTS.md §8b + seith-warden-pm gate):** 1 fase = 1 folder `.handoff/phase-NN-topic/` → `00-overview.md` (Goal,WBS,Dependency,Arsitektur,PromptLock,DoD,Peran,Output,Referensi + dual-agent Bob vs opencode jika MCP) + `01-*.md` per task slice (Goal, I/O JSON, Verify, Accountability `✅/⚠️/🔻/♻️` + `♻️ Refactor:`).

**Lifecycle:**
- Awal sesi: `Read docs/AGENTS.local.md + .handoff/phase-NN-topic/00-overview.md` + `skill://seith-warden-compliance` (SSOT 10 docs)
- Akhir sesi/topik: `skill://handoff → .handoff/phase-NN-topic/*.md` + `todowrite` trace + Accountability Block wajib
- Branch: `handoff/NN-topic` flat dari `main` + worktree `../warden-wt/handoff-NN-*` — file handoff tetap di `.handoff/phase-NN-topic/` ter-commit, worktree `/.wt/` gitignore
- Commit: `type: desc` (feat/fix/test/chore/docs) — no force push ke `main`/`handoff/*`
- PM seith-warden-pm: orkestrasi + gate + veto merge ke `main` jika satu gate merah

**Fase Aktif:**
- Phase 00 — `.handoff/phase-00-agents-sync/` — **done** — AGENTS 10§ anti-slop + 7 Zones + skill SSOT + Bob real `.bob/mcp.json` → `01-agents-rewrite.md` `02-zones-skill-scaffolding.md`
- Phase 01 — `.handoff/phase-01-langflow-chain/` — **ready → sliced** — 3-agent chain + MCP real + Sheets/Webhook → `01-refmapper.md` `02-ruleauditor.md` `03-risksynthesizer.md` `04-mcp-server.md` `05-sheets-webhook.md`
- Template — `.handoff/phase-template/00-overview.md` — SSOT Phase NN+1 (DoD 8 gate + PM veto + dual-agent + 7 Zones)

**Gate WAJIB sebelum claim done (AGENTS §7 + PM veto):**
```
uv run ruff check .                → 0 (refactor-cleaner fn<50 pass)
uv run python tools/pii_sanitizer.py → ok (NIK→rek→email)
python -m json.tool flows/seith_warden_flow.json → valid + 3 prompt terkunci (jika Phase01+)
python -m json.tool tests/test_scenarios.json    → valid 10 oracle HIGH3 MED3 LOW2 COMP2
python -m json.tool .opencode/opencode.json + .bob/mcp.json → valid, ${LANGFLOW_API_KEY} only
tree /F                            → 7 Zones rapih (no file liar)
code-reviewer + security-reviewer  → paralel pass (MANDATORY sebelum freeze)
no-ai-slop                         → prose/deck pass (warn→hard fail H-1)
todowrite exactly-one in_progress + Accountability ✅/⚠️/🔻/♻️
Bob real: 3 tools Action+Input + Invoke-WebRequest :7860 200 (jika sentuh MCP)
```
Klaim tanpa output nyata = Tier-0.9 pelanggaran + PM veto.

**Skill Wajib Aktifkan per Kebutuhan (AGENTS §8/§10):**
- Selalu: `seith-warden-compliance` — Tiap fase: `verification-loop` + `refactor-cleaner` WAJIB — Sebelum freeze: `security-reviewer`
- Sesuai slice: `tdd-guide` (matrix edge PERLU_VERIFIKASI_MANUAL) | `code-reviewer` (Python/flow) | `doc-updater` (sync docs) | `build-error-resolver` (langflow fail) | `explorer` | `e2e-runner` H-1 | `git-worktree-manager`
- PM: `.opencode/agents/seith-warden-pm/agent.json + SKILL.md` — autonomous gate

**Referensi:** `AGENTS.md §8b/§8c/§8d/§10` + `docs/AGENTS.local.md §6` tracer + `.opencode/skills/seith-warden-compliance/SKILL.md` + `.opencode/agents/seith-warden-pm/SKILL.md` + `docs/assets/bob-integration.md` real + `scripts/verify.ps1`
