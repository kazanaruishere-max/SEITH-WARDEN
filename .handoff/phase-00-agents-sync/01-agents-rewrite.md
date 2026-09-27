# 01 — Rewrite AGENTS.md 10§ Anti-Slop

**Goal:** AGENTS.md 10§ lock anti AI generik/slop, 7 Zones, Tier-0 9 rules, Boy Scout `fn<50`, DoD 8 gate — rumus SEITH-MARKET-IDX diadaptasi untuk WARDEN Langflow.

**Slice:** Backup `docs/AGENTS.prev.md` → rewrite `AGENTS.md` (~350 baris) → sync `docs/CONTEXT.md` + `docs/arsitektur.md` + `docs/security.md`.

**Done:**
- [x] AGENTS.md 10§: §1 Identity T0=Otak/T1-T2=Tangan + §1a Piagam Mandat + §2 Snapshot (30/20/20/15/10/5) + §3 Arch + §3c 7 Zones + §4 Tier-0 + §5 Env `uv` + §5b Boy Scout + §6 Contract + §6c Anti-slop + §7 DoD + §8 Delegasi+worktree
- [x] Backup `docs/AGENTS.prev.md` sebelum rewrite
- [x] KB grounding `data/kb/padk_2026_curated.md` sebagai gate — cabut = FAIL (Tier-0.1)

**Kontrak SSOT:**
- Prompt lock `0.0/0.0/0.1` §2 + `PERLU_VERIFIKASI_MANUAL` tunggal §4.4/§6 + MCP `Action+Input` §6 + `no auto legal` §1a.4

**Verify:**
```
uv run ruff check . → All checks passed!
uv run python tools/pii_sanitizer.py → ok
```
**Accountability:**
- ✅ Terverifikasi: AGENTS.md 303 baris + CONTEXT sync → `ruff 0` (nyata)
- ⚠️ Belum: review `code-reviewer` paralel sebelum freeze
- 🔻 Risiko: drift AGENTS↔docs jika edit tanpa sync — deteksi: `grep -r "PERLU_VERIFIKASI_MANUAL" docs/ AGENTS.md`
- ♻️ Refactor: hapus duplikat §2 Snapshot vs §3 Arch — extract snapshot table

**Next:** 02-zones-skill-scaffolding
