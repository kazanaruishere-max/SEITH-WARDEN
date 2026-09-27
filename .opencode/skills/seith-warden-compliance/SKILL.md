# Skill: seith-warden-compliance — SSOT Pointer SEITH-WARDEN

> **WAJIB load di awal setiap sesi T0/T1/T2 + PM.** Sumber kebenaran tunggal compliance radar. Jangan coding sebelum baca rantai SSOT. Skill ini + PM gate = veto jika dilanggar.

## Misi
SEITH-WARDEN = audit SOP fintech vs PADK 2026 — deteksi 2-arah (format SEOJK→PADK + substansi 0,1%/Lock 100%) dengan sitasi pasal `data/kb/padk_2026_curated.md`, strict JSON, Sheets 9 kolom + Webhook HIGH only. Gagal jika hallucinate angka atau context bleeding SOP↔PADK. Bob = wajah juri, Langflow = otak.

## Dual-Agent Max (Opencode + Bob) — Jangan Duplikat
- **Opencode (T0 dev, otak):** `handoff/01-langflow-chain` worktree + TDD `tools/pii_sanitizer.py` `re` NIK→rek→email + dual-vector `chroma-local` 800/150 vs hierarchical + `uv run ruff/pii/json` + `verification-loop` + `refactor-cleaner fn<50`
- **Bob (wajah juri, MCP Client):** `.bob/mcp.json` `lf-seith_warden` `a760286c-db9f-406b-bb95-4d2121592e5e/streamable` `streamablehttp + x-api-key` → discovery 3× `Action+Input` — natural `"audit Pasal 1 0,25%"` → `HIGH+PADK 12:1` — 0 logika audit
- Protokol identik — dev via opencode cepat, demo via Bob real (PDF Hal 4,21,30). Detail `docs/assets/bob-integration.md` real.

## Rantai SSOT (baca urut, jangan skip)
1. `AGENTS.md` — Tier-0 9 rules + 7 Zones + Boy Scout + DoD 8 gate + §8 delegasi/branch/worktree (wajib hafal)
2. `docs/CONTEXT.md` — lexicon SEOJK/PADK/POJK/Lock Cap/P2SK/PERLU_VERIFIKASI_MANUAL/Action+Input
3. `docs/prd.md` — requirement + monetisasi SaaS Rp4,9/12,5/24,9jt + 10 skenario mapping
4. `docs/arsitektur.md` — Langflow + dual-vector isolated + MCP 3 schema + env free tier
5. `docs/security.md` — Responsible AI Hal 81-85 + PII strip + HITL + fallback + transport TLS
6. `docs/setup.md` — `uv sync → langflow :7860 → test 10 skenario` + Bob Hal 56-60
7. `docs/decisions/ADR-001-dual-store-local.md` — chroma-local gratis vs Astra H2
8. `docs/AGENTS.local.md` — Decision Log + H-1 secret revoke + tracer phase-00 done + phase-01 sliced
9. `tests/test_scenarios.json` — 10 skenario HIGH3 MEDIUM3 LOW2 COMPLIANT2 oracle
10. `docs/assets/bob-integration.md` — Bob real connected Gear→MCP + Global Variables LANGFLOW_API_KEY reuse

## Tier-0 (PM veto jika langgar)
- Grounding PADK wajib `data/kb/padk_2026_curated.md` — cabut = FAIL. No auto legal, wajib `Preliminary Advisory` di JSON.
- Dual-vector isolation SOP vs PADK — bleeding = FAIL.
- Temp `0.0/0.0/0.1` lock — ubah butuh ADR. Fallback tunggal `PERLU_VERIFIKASI_MANUAL`.
- Secrets via env `GOOGLE_API_KEY/LANGFLOW_API_KEY/SHEETS_*` — `.env` gitignore, `.opencode/opencode.json:15` H-1 revoke 2026-10-03.
- Langflow `:7860` NEVER kill — cek `Invoke-WebRequest http://localhost:7860/api/v1/flows` 200.
- MCP `Action+Input`: `audit_sop_regulatory_reference` | `evaluate_rate_cap_substance` | `generate_compliance_remediation_log` — 3 tools strict.

## Workflow Wajib per Sesi (AGENTS §7/§8d)
```
Understand → Plan → todowrite (exactly-one in_progress) → Implement → Verify → Refactor → Document → handoff
```
- Awal: `Read docs/AGENTS.local.md + .handoff/phase-NN-topic/00-overview.md` (phase aktif)
- Akhir: `skill://handoff → .handoff/phase-NN-topic/01-*.md` + Accountability `✅/⚠️/🔻/♻️`
- Verify: `uv run ruff check .` + `uv run python tools/pii_sanitizer.py → ok` + `python -m json.tool flows/... tests/... .opencode/opencode.json .bob/mcp.json` valid + `tree /F` 7 Zones
- Refactor Boy Scout §5b: `fn<50 file200-400 nesting≤4 no dead code` + `uv run ruff check --fix` + `♻️ Refactor:` wajib
- Todo: `todowrite` trace `pending→in_progress→completed` — tanpa trace = FAIL

## Skill Wajib per Lapisan (AGENTS §8 — aktifkan sesuai kebutuhan)
- **L1 Lead/PM:** `seith-warden-pm` (`.opencode/agents/seith-warden-pm/`) orkestrasi handoff/branch/worktree + veto gate
- **L2 Gate wajib:** `code-reviewer` (Python `tools/` + flow wiring) + `security-reviewer` (secrets/PII/bearer/input validation) — paralel — MANDATORY sebelum freeze + `tdd-guide` (matrix 10 skenario edge PERLU_VERIFIKASI_MANUAL)
- **L3 Governance:** `doc-updater` (sync README/ADR/docs) + `handoff` + `verification-loop` + `remember`
- **L4 On-demand (kecuali refactor WAJIB):** `refactor-cleaner` WAJIB pasca tiap task + `build-error-resolver` (uv/langflow fail) + `explorer` + `e2e-runner` (Playwright H-1) + `docs-lookup` + `no-ai-slop` (Tier-1 prose) + `git-worktree-manager`

## Anti AI Slop (Tier-1 Phased)
- Prose/docs/deck: `no-ai-slop` sebelum merge — larang `delve,leverage,robust,cutting-edge`, binary `It's not X it's Y`, colon reveals, em-dash crutch.
- Flow canvas: naming `Action+Input`, no node menggantung.
- Minggu 1-2 warn, H-1 hard fail.

## 7 Zones Lock (file liar = PM veto §8c)
`flows/` | `tools/` | `data/kb,sop_dummy` | `tests/` | `docs/decisions` | `.handoff/phase-NN/` | `scripts/.opencode/.github` — `tools/`≠`flows/`, `data/`≠kode

## Handoff Governance (AGENTS §8b)
- 1 fase = 1 folder `.handoff/phase-NN-topic/` → `00-overview.md` (Goal,WBS,Dependency,Arsitektur,PromptLock,DoD,Peran,Output,Referensi) + `01-*.md` per task
- Branch `handoff/NN-topic` flat dari `main` + worktree `../warden-wt/handoff-NN-*` + `/.wt/` gitignore
- Template: `.handoff/phase-template/00-overview.md` + SSOT `.handoff/README.md`

## PM Gate (sebelum claim done)
Jangan claim selesai tanpa: `ruff 0` + `pii ok` + `json valid×4` + `tree 7 Zones` + `dual-review pass` + `refactor-cleaner pass` + `no-ai-slop pass` + `todowrite trace` + `Accountability ✅/⚠️/🔻/♻️` + `Bob 3 tools` jika sentuh MCP. PM veto merge ke `main` jika satu gate merah.
