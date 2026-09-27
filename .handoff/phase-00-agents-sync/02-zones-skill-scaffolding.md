# 02 — 7 Zones + Skill SSOT + Scaffolding

**Goal:** 7 Zones lock rapih + skill `seith-warden-compliance` SSOT + skeleton 7 Zones siap implementasi tanpa bug logic.

**Slice:**
- 7 Zones: `flows/` | `tools/` | `data/kb+sop_dummy` | `tests/` | `docs/` | `.handoff/phase-NN` | `scripts/.opencode/.github`
- Skill: `.opencode/skills/seith-warden-compliance/SKILL.md` auto-load `docs/CONTEXT.md`
- Scaffolding: `flows/seith_warden_flow.json` skeleton `${env}` + `tools/pii_sanitizer.py` `re` urutan NIK→rek→email + `tests/test_scenarios.json` 10 skenario + `docs/assets/bob-integration.md` Bob formalitas

**Done:**
- [x] 7 Zones tercipta, cross-zone import liar dilarang (§3c) — `tools/` tidak import `flows/`
- [x] Skill SSOT ter-load via `skill://seith-warden-compliance` — pointer AGENTS→docs
- [x] Bob formalitas: `docs/assets/bob-integration.md` + PDF Hal 4,21,30 — runtime harian `opencode` (protocol identik), Bob via `uvx mcp-proxy` jika diminta juri
- [x] `.gitignore`: `/.wt/` + `_wt/` + `.handoff/*.md` allowlist + `.ruff_cache/` + `.env` + `flows/*.json` `!README`

**Kontrak:**
- `flows/seith_warden_flow.json` no hardcode `sk-...` (Tier-0.5) — hanya `${GOOGLE_API_KEY}`
- `tests/test_scenarios.json` 10 skenario oracle (HIGH3 MEDIUM3 LOW2 COMPLIANT2) termasuk `PERLU_VERIFIKASI_MANUAL`
- `.env.example` free tier: `GOOGLE_API_KEY`, `LANGFLOW_API_KEY`, `VECTOR_STORE=chroma-local`, `SHEETS_*`

**Verify:**
```
uv run ruff check . → All checks passed!
uv run python tools/pii_sanitizer.py → ok
python -m json.tool flows/seith_warden_flow.json → valid 0
python -m json.tool tests/test_scenarios.json → valid 0
tree /F → 7 Zones rapih
```
**Accountability:**
- ✅ Terverifikasi: tree 7 Zones + ruff 0 + pii ok + json valid (nyata)
- 🔻 Risiko: `chroma-local` path salah → bleeding — deteksi: `grep chroma data/` per zone isolated
- ♻️ Refactor: `.gitignore` allowlist `.handoff/*.md` — sempitkan ke `phase-*/*.md`

**Next:** Phase 01 chain (RefMapper→RuleAuditor→RiskSynthesizer + MCP + Sheets)
