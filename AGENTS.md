# AGENTS.md — SEITH-WARDEN

Panduan wajib untuk agent harness apa pun (opencode, omp, sub-agent) yang bekerja di repo ini. Baca ini SEBELUM menulis kode.

Referensi produk: `docs/prd.md` · Arsitektur: `docs/arsitektur.md` · Security: `docs/security.md` · Lexicon: `docs/CONTEXT.md` · Setup: `docs/setup.md` · ADR: `docs/decisions/` · Handoff: `.handoff/phase-NN-topic/` · Kompetisi: `docs/hacktiv8_hackathon_national.md` · Track: Financial (Hacktiv8 x IBM 2026)

## 1. Identity & Ownership

- **Lead tunggal = opencode (T0).** Semua pekerjaan menjadi tanggung jawab lead, termasuk yang dikerjakan sub-agent T1/T2.
- **T0 Sesi Utama (sini) = Otak.** `Understand → Plan → Document`. Putuskan arah win, tulis/approve `.handoff/phase-NN-topic/00-overview.md`, jaga single narrative. Tidak coding berat.
- **T1/T2 Eksekutor = Tangan.** `Implement → Verify` per handoff doc via sub-agent. Satu slice terverifikasi per session (TDD red-green).
- Sub-agent dan skill adalah **alat delegasi untuk kualitas** (review independen, spesialisasi), bukan pemangkas tanggung jawab. Hasil delegasi WAJIB diverifikasi ulang oleh lead sebelum dianggap benar.
- Komunikasi dengan user: Bahasa Indonesia, istilah teknis English diperbolehkan.
- Skill `seith-warden-compliance` adalah **SSOT pointer** — semua terminal load `skill://seith-warden-compliance` di awal session agar 1 tujuan.

### 1a. Piagam Mandat Lead (disetujui founder, 2026-09-26)

1. **Bukti > klaim:** setiap status "selesai" wajib disertai output perintah nyata (`uv run ruff check .`, `uv run python tools/pii_sanitizer.py`, `python -m json.tool`). Tidak ada fabrikasi.
2. **Gerbang grounded PADK berlapis:** produk FAIL jika hanya display mentah atau tebak angka. Wajib `detected_references + substantive_evaluations + risk_level + draft_recommendation` ter-grounding ke `data/kb/padk_2026_curated.md` — KB dicabut = produk mati.
3. **Pembagian keputusan:**
   - Founder: strategis — positioning RegTech, threshold 0,1%/Lock 100%, go-live/freeze, arah produk, monetisasi SaaS.
   - Lead: teknis — implementasi Langflow/Python, wiring MCP, urutan handoff, refactor; berhak veto teknis atas keputusan yang melanggar Tier-0 atau grounded gate.
4. **Governance jalan terus:** cadence §8 tidak boleh dilewati demi kecepatan. Track Financial rule (`no auto legal verdict`, disclaimer `Preliminary Advisory` di setiap JSON, fallback `PERLU_VERIFIKASI_MANUAL`) tidak bisa dinego.

## 2. Project Snapshot

SEITH-WARDEN = RegTech audit kepatuhan OJK — Track Financial (Hacktiv8 x IBM 2026). Satu tujuan: **win** dengan `gap detection yang explainable dan bisa dipakai compliance officer hari ini`.

- **Qualifying test Financial:** harus deteksi 2-arah (format SEOJK→PADK + substansi 0,1%/Lock 100%) dengan sitasi pasal. Lolos = `RATE_CAP_BREACH / DEPRECATED_CODE / PERLU_VERIFIKASI_MANUAL` + rekomendasi klausul. Gagal = RAG-QA generik tanpa gap.
- **Judging 30/20/20/15/10/5:** 30% Innovation+Monetisasi (B2B SaaS Rp4,9/12,5/24,9jt + SOM Rp2,5M ARR), 20% Problem Clarity (POJK 40/2024, PADK 2026, UU P2SK 4/2026), 20% User Impact (potong 85% dari 14 hari), 15% Responsible AI (HITL + PII strip + grounding), 10% Technical Execution (modular 3-agent + MCP Action+Input), 5% Participation.
- **Inti produk:** RefMapper (SEOJK usang) + RuleAuditor (0,1%/Lock 100%) + RiskSynthesizer (HIGH/MEDIUM/LOW + draft klausul) → Strict JSON → Sheets (audit trail) + Webhook (HIGH only).
- **Mode eksekusi:** Langflow local `:7860` = kontrak inti verifiable + MCP `streamablehttp` `Action+Input`. Dual-vector isolated `chroma-local` gratis. Tidak ada vendor lock untuk MVP.
- **Market:** Fintech P2P/BNPL/Bank Digital kecil-menengah tanpa tim compliance besar. SOP 150-400 halaman.
- **LLM:** Gemini 1.5 Flash free tier (`GOOGLE_API_KEY`) — temp `0.0 / 0.0 / 0.1` lock. Fallback `PERLU_VERIFIKASI_MANUAL` jika ambigu.

## 3. Architecture Snapshot

```
[SOP Internal PDF/txt] ─┐
                         ├─► PII Sanitizer (re stdlib) ─► Recursive Splitter 800/150 ─► Embedding text-embedding-004 ─► Vector Store SOP (chroma-local)
[KB PADK 2026 curated] ─┘         (NIK/rekening/email → [REDACTED])      Hierarchical Splitter Bab→Pasal→Ayat ─► Vector Store PADK (chroma-local)
                                         │                                              │
                                         └────────────── Dual-Collection Isolated ──────┘
                                                              │
                         ┌────────────────────────────────────▼────────────────────────────────────┐
                         │              LANGFLOW ENGINE & MCP SERVER :7860                        │
                         │  MCP Router (Action+Input):                                           │
                         │   audit_sop_regulatory_reference | evaluate_rate_cap_substance        │
                         │   generate_compliance_remediation_log                                 │
                         │                        │                                              │
                         │  Chain: RefMapper (0.0) → RuleAuditor (0.0) → RiskSynthesizer (0.1)  │
                         │                        │                                              │
                         │  Tool-Calling: Google Sheets (audit trail) + Webhook (HIGH only)     │
                         └───────────────────────────────────┬───────────────────────────────────┘
                                                             │ Strict JSON
                                                             ▼
                                                    Chat Output + Sheets/Webhook
```

| Path | Isi | Env |
|:---|:---|:---|
| `flows/seith_warden_flow.json` | Flow Langflow 3-agent + dual retriever + 2 tool node + structured output | Langflow :7860 |
| `tools/pii_sanitizer.py` | Sanitizer `re` stdlib — kontrak PII, `fn <50` | `uv` |
| `tools/` | Custom component Sheets/Webhook (jika ada) | `uv` |
| `data/kb/padk_2026_curated.md` | KB PADK grounding SSOT — `collection_ojk_padk2026` | file |
| `data/sop_dummy/sop_bunga_dummy.md` | 10 klausul dummy (HIGH/MEDIUM/LOW/COMPLIANT) | file |
| `tests/test_scenarios.json` | Matrix 10 skenario expected output per agent | `uv run python -m json.tool` |
| `docs/` | prd/arsitektur/security/CONTEXT/setup/adr | — |
| `.handoff/phase-NN-topic/` | Handoff per fase (folder=phase, file=task) | — |

### 3c. Seven Zones — Struktur Folder Lock (WAJIB rapih, §8c)

Struktur root terkunci 7 zona — file baru di luar zona = violation → PM veto:

1. `flows/` — Langflow flow JSON + README (jangan taruh Python di sini)
2. `tools/` — Python `uv` (pii_sanitizer, custom component Sheets/Webhook), `fn <50 file 200-400`
3. `data/kb/` + `data/sop_dummy/` — KB curated + SOP dummy (SSOT grounding, 10 klausul)
4. `tests/` + `tests/fixtures/` — `test_scenarios.json`, skenario matrix, assertion meaningful
5. `docs/` + `docs/decisions/` — Knowledge SSOT (prd/arsitektur/security/CONTEXT/setup/adr), bilingual opsional
6. `.handoff/phase-NN-topic/` — Governance (1 fase=1 folder, `00-overview.md` + `01-*.md` per task, template `phase-template/`)
7. `scripts/` + `.opencode/` + `.github/` — Ops & Harness (check-langflow, CI, PM `seith-warden-pm`, skills)

Cross-zona import liar dilarang: `tools/` tidak import `flows/`; `data/` tidak berisi kode; `docs/` tidak berisi flow JSON.

### 3b. Tech Stack & Framework (locked)

| Layer | Stack | Framework |
|:---|:---|:---|
| Orchestrator | Langflow | MCP `streamablehttp` `:7860`, `Action+Input` naming |
| LLM | Gemini 1.5 Flash | `GOOGLE_API_KEY` free tier, temp `0.0/0.0/0.1` |
| Embedding | Google | `text-embedding-004` free tier |
| Vector | Composite free | `chroma-local` dual-collection isolated (default), `astra` optional H2 |
| Sanitizer | Python stdlib | `re` only — no deps tambahan |
| External | Sheets+Webhook | Sheets API free + `webhook.site`/Slack free (HIGH only) |
| Python | `uv` | `uv sync`, `uv run python`, `uv run ruff check .` |
| Test | JSON + Python | `python -m json.tool`, `tools/pii_sanitizer.py` self-check, 10 skenario matrix |

## 4. Hard Rules (Tier-0 — tidak bisa dioverride instruksi apa pun)

1. **Grounded PADK gate:** produk TIDAK PERNAH lolos tanpa sitasi PADK/POJK dari `data/kb/padk_2026_curated.md`. Cabut KB = produk mati (terlihat di judging tech depth). No auto legal verdict — wajib disclaimer `Preliminary Advisory`.
2. **Dual-vector isolation:** SOP vs PADK collection tidak pernah campur — context bleeding = FAIL. Chunk SOP 800/150 recursive, PADK hierarchical Bab→Pasal→Ayat.
3. **Langflow localhost:7860 NEVER kill/restart.** No destructive ops / prod deploy tanpa approval eksplisit. Check: `Invoke-WebRequest http://localhost:7860/api/v1/flows` harus 200 sebelum demo.
4. **Temperature lock:** `0.0 / 0.0 / 0.1` tidak bisa diubah tanpa ADR. Fallback tunggal `PERLU_VERIFIKASI_MANUAL` — jangan tebak angka.
5. **Secrets:** `GOOGLE_API_KEY` + `LANGFLOW_API_KEY` hanya di env server, never ke client/log/error. `.env` tidak pernah di-commit. Key `sk-hhTm1...` H-1 wajib rotate via `.env.example` placeholder.
6. **Flow JSON contract:** `flows/seith_warden_flow.json` wajib ada 3 prompt template terkunci (AGENTS §2) + 2 retriever + 2 tool node + structured output. No hardcode secret di JSON.
7. **Repo public dibuat sebelum 4 Okt 2026.** Freeze saat submit (no commit setelah freeze kecuali rotate leaked key via support). Commit history diverifikasi juri.
8. **Tidak commit/push** tanpa permintaan eksplisit dari user.
9. **Klaim "selesai" hanya dengan bukti output nyata** (perintah + hasil). Tidak ada fabrikasi hasil verifikasi.

## 5. Environments & Commands (gotcha nyata — ikuti persis)

Langflow adalah inti. Python HANYA via `uv`. LLM via Gemini Flash free. Dual-vector `chroma-local` default gratis. MCP `streamablehttp` + `x-api-key`.

```bash
# Setup — dari root repo:
cp .env.example .env  # isi GOOGLE_API_KEY & LANGFLOW_API_KEY
uv sync
uv run ruff check .
uv run python tools/pii_sanitizer.py  # harus "ok"
uv run python -m json.tool tests/test_scenarios.json

# Langflow — dari root:
uv run langflow run --host 127.0.0.1 --port 7860
# cek MCP: Invoke-WebRequest http://localhost:7860/api/v1/flows -Headers @{"x-api-key"="$env:LANGFLOW_API_KEY"}

# Verifikasi cepat:
tree /F
uv run python -m json.tool flows/seith_warden_flow.json  # valid JSON?

# Sheets/Webhook (free):
# SHEETS_ID + SHEETS_WEBHOOK_URL di .env — webhook trigger hanya HIGH
```

**Gotcha yang sudah terbukti terjadi:**

- `uv sync --project X` dari root → tuang ke `.venv` root (SALAH). Selalu workdir root, jangan `--project`.
- Menambah file baru di `tools/` tanpa `uv run ruff check .` → CI fail.
- Missing `daily_rate_percent` dari SOP → harus `PERLU_VERIFIKASI_MANUAL`, bukan `0`.
- `flows/seith_warden_flow.json` hardcode `sk-...` → pelanggaran Tier-0, ganti `${env}`.
- `chroma-local` path salah → dual-collection tidak isolated, context bleeding.
- Langflow mati → MCP `streamable` 404, cek `127.0.0.1:7860` dulu sebelum demo.
- `SHEETS_WEBHOOK_URL` kosong → webhook `skipped` adalah OK untuk LOW/MEDIUM, bukan error.

### 5b. Boy Scout Rule — Refactor Wajib (Tidak Bisa Diskip)

- **Refactor adalah kewajiban, bukan opsional.** Setiap task yang menyentuh file WAJIB meninggalkan code lebih bersih dari sebelumnya — `fn <50 baris`, `file 200-400 baris`, `nesting ≤4`, `no dead code`, `no silent swallow`, `no duplication`.
- Minimal per task: `uv run ruff check --fix` + hapus dead code + extract function jika >50 baris + rename yang ambigu. Tidak ada claim `selesai` tanpa `♻️ Refactor:` di Accountability Block.
- Trade-off `+15% waktu` diterima demi `10% Technical depth` — debt yang ditunda di minggu 1 akan meledak di demo.

## 6. Contract Rules (`tools/pii_sanitizer.py` + `tests/test_scenarios.json` adalah hukum)

- Model domain STRICT: `sanitize_sop_text` urutan `NIK → rekening → email`, return `[REDACTED_*]`. `tests/test_scenarios.json` 10 skenario dengan `expect HIGH/MEDIUM/LOW/COMPLIANT/PERLU_VERIFIKASI_MANUAL`.
- MCP contract: `audit_sop_regulatory_reference(sop_text: string)` → `{"detected_references":[...]}`; `evaluate_rate_cap_substance(daily_rate_percent: number, lock_cap_percent?: number)` → `{"substantive_evaluations":[...]}`; `generate_compliance_remediation_log(clause_id, risk_level LOW|MEDIUM|HIGH, remediation_text)` → `{"sheets_status","webhook_status"}`.
- JSON adalah kontrak antar-agent; tiap agent output wajib valid JSON (regex fallback jika markdown bocor).
- Severity `HIGH` = `violation true` (bunga>0,1%/Lock>100%), `MEDIUM` = SEOJK tanpa pelanggaran angka, `LOW` = typo minor, `PERLU_VERIFIKASI_MANUAL` = ambigu tanpa angka.
- Sebelum mengubah schema: baca dampak ke SEMUA consumer (flow/tools/tests/docs).

### 6c. Anti AI Slop (Tier-1 — prose/docs, phased enforcement)

- **Scope:** `README`, `docs/*.md` prose, deck 10 slide. Exclude `docs/arsitektur.md`/`docs/decisions/`/`tests/` yang butuh presisi teknis.
- **Prose:** WAJIB `skill://no-ai-slop` detect sebelum merge — larang `Words to cut` (`delve, leverage, robust, cutting-edge` dll) + `Patterns to cut` (binary contrast `It's not X it's Y`, colon reveals, throat-clearing, puffery, em-dash crutch, formatting slop).
- **Flow:** Langflow canvas WAJIB rapih, naming `Action+Input`, tidak ada node menggantung.
- **Enforcement phased:** Minggu 1-2 PR checklist warn; H-1 pra-freeze grep banned-words hard fail + manual audit. Tier-1 = tidak block velocity, tapi `seith-phase-gate` wajib cek.

## 7. Phase Workflow & Definition of Done

Workflow: `Understand → Plan → Todo → Implement → Verify → Refactor → Document` — `todowrite` WAJIB dibuka setelah Plan, exactly-one `in_progress`, update realtime.

Fase dinyatakan done HANYA jika semua hijau (refactor tidak bisa diskip):

1. Test relevan lulus (output nyata, bukan asersi kosong) — `uv run python tools/pii_sanitizer.py` + `python -m json.tool tests/test_scenarios.json` hijau.
2. `uv run ruff check .` bersih di file yang disentuh.
3. `tree /F` 7 zones rapih, tidak ada file liar di root.
4. Review gate lewat (skill `seith-warden-compliance` atau `code-reviewer` + `security-reviewer` paralel).
5. Dokumentasi ter-update (ADR untuk keputusan, prd/arsitektur/security untuk requirement berubah).
6. Accountability Block terisi dengan output nyata + `♻️ Refactor: <apa>` wajib.
7. Refactor gate lewat: `fn <50`, `file 200-400`, `nesting ≤4`, `no dead code` — `refactor-cleaner` scan pass.
8. Todo trace ada (`todowrite`: pending→in_progress→completed, exactly-one `in_progress`) — klaim done tanpa jejak todo = FAIL.

## 8. Tim & Delegasi (struktur lengkap — WAJIB dipatuhi semua harness)

### Lapisan 1 — Kepemimpinan

| Peran | Eksekutor | Tanggung jawab |
|:---|:---|:---|
| Lead / Orchestrator | opencode (T0) | Pegang semuanya; semua output delegasi diverifikasi lead |
| Founder / Owner | User (founder) | Keputusan strategis: positioning RegTech, threshold 0,1%/Lock 100%, go-live/freeze, monetisasi |
| Project Manager | `seith-warden-pm` (autonomous, `.opencode/agents/seith-warden-pm/`) | Orkestrasi handoff/branch/worktree, gate `ruff check + json.tool`, **veto merge ke `main` jika gate/reviewer fail** |
| Arsitek reviewer | sub-agent `architect` | Audit struktur SEBELUM fase besar dimulai |
| Perencana fase kompleks | sub-agent `planner` | Forward-test wiring Langflow, refactor lintas tools/docs |

> Governance eksklusif: repo `source-available, NOT community` sampai founder membuka. Semua kolaborasi (PR/issue) ditutup sampai eksplisit dibuka. Track Financial: KB PADK core + no auto legal + disclaimer.

### Lapisan 2 — Kualitas & Keamanan (gate wajib)

| Peran | Agent | Kapan |
|:---|:---|:---|
| Auditor kode Python | `code-reviewer` | Tiap tools baru; audit pii_sanitizer/flow wiring |
| Auditor keamanan | `security-reviewer` | Secrets, PII, MCP bearer, input validation; MANDATORY sebelum freeze |
| Desainer test | `tdd-guide` | Matrix 10 skenario + edge `PERLU_VERIFIKASI_MANUAL` |

### Lapisan 3 — Governance & Dokumentasi

| Peran | Eksekutor | Kapan |
|:---|:---|:---|
| Penjaga dokumentasi | `doc-updater` | Setiap merge: sinkron README/ADR/docs dengan realita kode |
| Penjaga GitHub | LEAD langsung | Konvensi commit + audit drift repo-vs-dokumen |
| Penjaga memori | skill `remember` + `handoff` | Fakta penting → memory; konteks sesi → handoff |
| Gate fase | skill `seith-warden-compliance` + `verification-loop` | Protokol penutupan fase (dual-review) |

### Lapisan 4 — Dukungan Teknis (on-demand, kecuali refactor)

| Peran | Agent | Kapan |
|:---|:---|:---|
| Fix build/boot error | `build-error-resolver` | `uv run` fail, ruff, langflow boot |
| Riset vendor/library | `docs-lookup` / `deep-research` | Langflow/MCP/Gemini berubah |
| Eksplorasi cepat | `explorer` | Debug area kode luas |
| **Refactoring** | **`refactor-cleaner` (WAJIB)** | **Pasca tiap handoff + tiap task Boy Scout — gate wajib** |
| E2E flow | `e2e-runner` | Langflow + MCP Playwright (H-1) |

### Tata Tertib Cadence (WAJIB)

```
Tiap commit   : conventional commit (feat/fix/test/chore/docs) + doc-updater cek dampak docs
Tiap fase     : seith-warden-compliance gate (code-reviewer + security-reviewer paralel) + verification-loop
Tiap minggu   : audit drift repo-vs-docs + laporan status founder
Pra-freeze    : security-reviewer MANDATORY + architect sign-off + deck 10 slide check
```

Aturan delegasi: tugas paralel/independen boleh paralel; hasil selalu ditriage oleh lead; temuan valid difix, tolakan didokumentasikan alasannya.

### 8b. Branch & Worktree Strategy (Wajib untuk 2-3 terminal paralel)

```
main (protected, solo) ← only Lead merge after seith-warden-compliance gate
 └─ handoff/NN-topic (1 fase = 1 branch, lifespan pendek, dari main)
     ├─ handoff/NN-topic/t1-<subtask> (opsional, jika 2 terminal kerjakan subtask beda paralel)
     └─ handoff/NN-topic/t2-<subtask>
test/<topic> (ephemeral, hanya chaos/load test, bukan fitur)
chore/docs/fix/* (hanya jika di luar handoff, tetap via PR)

.handoff/ (docs — phase-folder, branch tetap flat):
 └─ phase-NN-topic/                  ← 1 fase = 1 folder
     ├─ 00-overview.md                ← Goal phase, WBS, dependency, DoD phase, peran+skill+sub-agent
     ├─ 01-task-slice.md              ← task slice
     └─ 02-task-slice.md
```

- **Branch tetap flat** `handoff/NN-topic` (tidak jadi `phase/NN`); folder `.handoff/phase-NN-topic/` hanya organisasi docs per phase → task = file `NN-task.md` di dalam folder.
- **Default:** 1 handoff = 1 branch `handoff/NN-topic` + 2 worktree (`../warden-wt/handoff-NN-*`) agar 2 terminal tidak tabrak `cwd`. Gunakan `git worktree add`.
- **Sub-branch `handoff/NN/topic/t1` hanya jika T1/T2 garap file beda paralel** (mis. `t1-sanitizer` vs `t2-scenarios` di fase 00) — merge balik ke parent `handoff/NN` via PR + `code-reviewer` sebelum ke `main`.
- **Naming:** branch `handoff/00-agents-sync`, `handoff/01-langflow-chain`; folder `.handoff/phase-00-agents-sync/` + tasks `01-..md`; `test/mcp-load`.
- **Commit:** `type: desc` (feat/fix/test/chore/docs), no `push --force` ke `main`/`handoff/*`, rebase before merge, Accountability Block tiap task ubah file.
- **Lifecycle:** `git worktree add ../warden-wt/handoff-NN -b handoff/NN-topic` → implement (TDD) → `uv run ruff check . && uv run python tools/pii_sanitizer.py && python -m json.tool tests/test_scenarios.json` → dual-review → Lead squash-merge ke `main` → hapus worktree/branch.
- **Skill:** `git-worktree-manager` untuk orkestrasi worktree; setiap session eksekutor wajib `skill://seith-warden-compliance` di awal agar 1 tujuan. Doc `00-overview.md` wajib baca sebelum task `01-`.
- **Worktree gitignore:** `/.wt/` wajib di `.gitignore` (worktree di `../warden-wt/handoff-NN-*` atau `/.wt/`).

### 8c. Agent Code Ownership — Semua AI Agent Bertanggung Jawab Penuh (WAJIB Terstruktur & Rapih)

Setiap AI agent (T0/T1/T2 + `seith-warden-pm` + `architect/planner/tdd-guide/code-reviewer/security-reviewer/refactor-cleaner/doc-updater`) **BERTANGGUNG JAWAB PENUH** atas:

1. **Code** — `fn <50 baris`, `file 200-400 typical max 800`, `nesting ≤4`, `no dead code`, `no silent swallow`, `no duplication`, `immutable return`. Cross-zona import dilarang (§3c).
2. **Logic** — correctness sesuai `docs/prd.md` + `docs/arsitektur.md` + `docs/security.md` + `docs/CONTEXT.md` + `tests/test_scenarios.json`; `PERLU_VERIFIKASI_MANUAL` exact string, `daily_rate_percent` number, `risk_level` enum; tidak tebak — baca SSOT dulu.
3. **Testing** — TDD red→green→refactor; `uv run python tools/pii_sanitizer.py` + `python -m json.tool` hijau dengan assertion meaningful; critical path `sanitizer/contract/mcp` ≥80% meaningful; `Accountability Block ✅/⚠️/🔻/♻️` paste output nyata — no fabrikasi.
4. **Structure & Rapih** — ikuti **7 Zones §3c**; file baru wajib di zona benar; `uv run ruff check .` 0; `refactor-cleaner` scan pass; `skill://no-ai-slop` Tier-1 prose + `skill://seith-warden-compliance` gate; `Accountability Block` + `♻️ Refactor: <apa>` wajib tiap task.

Pelanggaran = **PM veto merge ke `main`** + `seith-warden-compliance` FAIL. Lead (T0) verifikasi ulang semua delegasi — delegasi bukan alasan lepas tanggung jawab.

### 8d. Todo Wajib (`todowrite`) — Biasakan Pakai ToDo

- Setiap task ≥3 langkah WAJIB buka `todowrite` setelah Plan, sebelum Implement: exactly-one `in_progress`, update realtime, `completed` hanya setelah verifikasi nyata.
- Tiap session T1/T2: `skill://seith-warden-compliance` → `todowrite` → Implement → `verification-loop` → `completed`.
- PM veto + `seith-warden-compliance` FAIL jika tanpa jejak todo (`pending→in_progress→completed`).

## 9. Docs Map

- `docs/prd.md` — requirement produk (dual ingestion, 3-agent, Sheets/Webhook, monetisasi SaaS Rp4,9/12,5/24,9jt)
- `docs/arsitektur.md` — arsitektur Langflow+MCP + dual-vector + tool-calling + env matrix free tier + flow contract
- `docs/security.md` — Responsible AI (PII strip, grounding KB, HITL, fallback, transport TLS)
- `docs/CONTEXT.md` — lexicon SEOJK/PADK/Lock Cap/P2SK
- `docs/setup.md` — `uv sync → langflow run :7860 → test 10 skenario`
- `docs/hacktiv8_hackathon_national.md` — panduan kompetisi + checklist submission
- `docs/ide_finance.md` — ide awal Financial + prompt layering 3-agent
- `docs/decisions/ADR-001-dual-store-local.md` — `chroma-local` vs Astra
- `docs/AGENTS.local.md` — keputusan lokal project + Decision Log + H-1 secret policy
- `docs/AGENTS.prev.md` — backup AGENTS.md sebelum refactor rumus
- `.handoff/phase-NN-topic/` — handoff per phase: `00-overview.md` + `01-*.md` per task slice
- `flows/seith_warden_flow.json` — kontrak verifiable Langflow (3 prompt terkunci + dual retriever + 2 tool)
- Skill: `.opencode/skills/seith-warden-compliance/SKILL.md` → pointer ke dokumen di atas (auto-load `docs/CONTEXT.md`)

## 10. Skill Proyek (auto-discovery via opencode.json)

| Skill | Kapan dimuat |
|:---|:---|
| `seith-warden-compliance` | **SSOT — WAJIB tiap session T1/T2 di awal** (pointer ke AGENTS→docs) |
| `handoff` | Akhir sesi/topik — tulis `.handoff/phase-NN-topic/*.md` |
| `no-ai-slop` | Prose/docs sebelum merge — banned words/patterns |
| `verification-loop` | WAJIB di akhir tiap handoff (ruff + pii + json) |
| `tdd-workflow` / `tdd-guide` | Saat tulis fitur/bug (red-green-refactor) |
| `git-worktree-manager` | Saat 2-3 terminal paralel (worktree lifecycle) |
| `impeccable` / `design-taste-frontend` | Deck 10 slide + README prose |

> Skill global lain (60+): `code-reviewer`, `security-reviewer`, `refactor-cleaner`, `understand`, `handoff` — boleh dipakai sebagai helper, tapi narasi produk tetap ikut `seith-warden-compliance`.
