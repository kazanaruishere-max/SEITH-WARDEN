# SEITH-WARDEN — Dual Compliance Engine for OJK & Marketplace Tax

**ID:** Mesin kepatuhan ganda untuk fintech di Indonesia — (1) **PADK Migration & Rate-Cap Radar** untuk audit SOP lending (SEOJK→PADK, bunga 0,1%/hari, Lock Cap 100%) dan (2) **Seller Payout & PPh 22 Guard** untuk rekonsiliasi pungutan marketplace (PMK 37/2025, 0,5%, ambang Rp500jt). Deterministik `Decimal`, jejak audit `SHA-256/HMAC`, dua flow Langflow terpisah.

**EN:** Dual compliance engine for Indonesian fintech — (1) **PADK Migration & Rate-Cap Radar** for lending SOP audit (SEOJK→PADK, 0.10%/day, 100% Lock Cap) and (2) **Seller Payout & PPh 22 Guard** for marketplace withholding reconciliation (PMK 37/2025, 0.5%, Rp500M threshold). Deterministic `Decimal`, auditable `SHA-256/HMAC`, two isolated Langflow flows.

> **Stack 100% Free Tier:** Gemini 1.5 Flash (`GOOGLE_API_KEY`) + `text-embedding-004` + `chroma-local` + Langflow `:7860` + Google Sheets API + `urllib` stdlib. No vendor lock for MVP.
> **Free Stack EN:** Same — free tier only, zero paid infra for MVP.
> **Integrasi / Integration:** Langflow MCP `streamablehttp :7860` + IBM Bob (formalitas, protocol identik dengan opencode). Lihat `docs/assets/bob-integration.md` (PDF Hal 21, 30).

![Build](https://img.shields.io/badge/build-verify.ps1%20GREEN-brightgreen) ![Tests](https://img.shields.io/badge/tests-8%2B13%20PASS-brightgreen) ![Graph](https://img.shields.io/badge/graph-10v13e%20x2%20OK-blue) ![Oracle](https://img.shields.io/badge/oracle-533jt%20106.60%25%20%7C%2070k-blue) ![License](https://img.shields.io/badge/license-source--available-lightgrey)

---

## Daftar Isi | Table of Contents

1. [Ringkasan Eksekutif](#ringkasan-eksekutif--executive-summary) · 2. [Masalah](#masalah--problem) · 3. [Solusi & Modul](#solusi--solution) · 4. [Arsitektur](#arsitektur--architecture) · 5. [Tumpukan Teknologi](#tumpukan-teknologi--tech-stack) · 6. [Struktur Repositori](#struktur-repositori--repository-structure) · 7. [Flow](#flow) · 8. [Data & Oracle](#data--oracle) · 9. [Keamanan](#keamanan--security) · 10. [Mulai Cepat](#mulai-cepat--quick-start) · 11. [Verifikasi](#verifikasi--verification) · 12. [Dokumentasi](#dokumentasi--docs) · 13. [Tata Kelola](#tata-kelola--governance) · 14. [Peta Jalan](#peta-jalan--roadmap) · 15. [Pengumpulan](#pengumpulan--submission)

---

## Ringkasan Eksekutif | Executive Summary

**ID:** SEITH-WARDEN memotong audit manual 10–14 hari menjadi hitungan jam. Modul SOP memastikan 100% migrasi rujukan regulasi dan kepatuhan plafon numerik. Modul Seller Guard menghitung posisi ambang UMKM, mendeteksi lebih-pungut dan refund tertahan, serta menghasilkan draf klaim siap salin dengan jejak audit 11 kolom dan `Bar ASCII capped`. Semua angka dihitung kode `Decimal`, bukan LLM; setiap file di-fingerprint `SHA-256`.

**EN:** SEITH-WARDEN cuts 10–14 day manual audits to hours. The SOP module ensures 100% regulatory reference migration and numeric ceiling compliance. The Seller Guard computes UMKM threshold position, detects over-withholding and pending refunds, and produces copy-ready claim drafts with 11-column audit trail and `capped ASCII Bar`. All numbers are computed by `Decimal` code, not LLM; every input is fingerprinted with `SHA-256`.

**Hipotesis monetisasi (belum divalidasi) / Monetization hypothesis (unvalidated):**
**ID:** B2B SaaS untuk tim compliance tanpa retainer konsultan. Belum diuji willingness-to-pay; harga ditetapkan setelah pilot.
**EN:** B2B SaaS for compliance teams without consultant retainers. Willingness-to-pay not yet tested; pricing after pilot.

---

## Masalah | Problem

**ID:**
- Transisi regulasi OJK Q1 2026: seluruh SEOJK menjadi PADK. SOP 150–400 halaman tersebar; rujukan usang luput.
- Plafon bunga konsumtif 0,1%/hari + Lock Cap 100% — deviasi 0,15% = pelanggaran HIGH, sanksi pembekuan/denda.
- PMK 37/2025: marketplace memungut PPh 22 0,5%; UMKM OP ≤Rp500jt bebas dengan surat pernyataan; ambang lintas-channel, efektif `M+1`, jendela suspensi, dan retur memerlukan verifikasi manual.

**EN:**
- OJK Q1 2026 transition: all SEOJK → PADK. 150–400 page SOPs scattered; deprecated references missed.
- Consumer rate cap 0.10%/day + 100% Lock Cap — 0.15% deviation = HIGH violation, freezing/fine risk.
- PMK 37/2025: marketplace withholds 0.5% PPh 22; OP UMKM ≤Rp500M exempt with declaration; cross-channel threshold, `M+1` effective, suspension window, returns need manual review.

---

## Solusi | Solution

### Modul 1 — PADK Migration & Rate-Cap Radar (SOP)

**ID:** `tools/pii_sanitizer.py` (NIK→rek→email) → chunk SOP 800/150 vs PADK hierarchical → `RefMapper (0.0)` + `RuleAuditor (0.0) + Code+GraphLookup` → `RiskSynthesizer (0.1)` → Sheets 9 kolom + Webhook HIGH-only → `Preliminary Advisory`.

**EN:** Same pipeline — `RefMapper (0.0)` detects deprecated codes, `RuleAuditor (0.0) + deterministic Code+Graph` checks 0.10%/100%, `RiskSynthesizer (0.1)` scores HIGH/MEDIUM/LOW with JSON fallback `PERLU_VERIFIKASI_MANUAL`.

### Modul 2 — Seller Payout & PPh 22 Guard

**ID:** CSV `order_id,gross_invoice_value,...` (66 baris DUMMY, `as_of 2026-10-01`) → `ReportNormalizer` (BOM strip, `,`/`;` case-insensitive, header strict) → `ThresholdGuard` (kumulatif + `other_channel`, `pct`, `crossed_date`, `notify_deadline`, `Bar capped 20 blok + overflow`) → `WithholdingAuditor` (`suspension > effective`, `HMAC SellerRef`, `Decimal 0,5%`) → `findings.json` → `Sheets 11 kolom + SHA-256`.

**EN:** Same — strict CSV header validation, threshold tracking, withholding audit with `HMAC SellerRef`, 11-column Sheets with `SHA-256` integrity.

**Pemisahan / Isolation:** Dua flow terpisah — `seith_warden_flow.json` (SOP, `4DCB`, 10v13e, restore `8F1C` clean) dan `seith_warden_seller_guard.json` (Seller, `4621`, 10v13e, `HMAC/BOM/Bar`). Import sebagai **dua flow berbeda**, jangan menimpa. Oracle 66 anda: `tests/fixtures/ORACLE_manual_2026-11-01.md`.

---

## Arsitektur | Architecture

```
                ┌─────────────────────────────────────────────┐
                │        Langflow :7860  (dua flow terpisah)  │
  SOP CSV/txt ──┤  seith_warden_flow.json (SOP 10v13e 4DCB)    ├──► Chat Output SOP
  Seller CSV ───┤  seith_warden_seller_guard.json (4621)      ├──► Chat Output Seller Guard
                │  MCP streamablehttp a760286c.../streamable  │
                │  Global Variables: SELLER_REF_KEY (HMAC)    │
                └──────────────┬──────────────────────────────┘
                               │ Sheets 9/11 cols + LIVE/SKIPPED
                               ▼
                         Google Sheets (dua sheet terpisah)
```

**ID:** SOP: dual-vector `collection_sop_internal` (800/150) vs `collection_ojk_padk2026` (hierarchical) — isolasi anti `context-bleeding`. Seller: `ThresholdGuard` + `WithholdingAuditor` deterministik `Decimal`. Keduanya berbagi `SELLER_REF_KEY` Global Variable (fail-closed `ValueError` jika tidak disetel) dan `SELLER_GUARD_SHEETS_URL/TOKEN` terpisah dari `SHEETS_WEBHOOK_URL`.

**EN:** SOP: dual-vector isolated. Seller: deterministic `Decimal` guards. Both share `SELLER_REF_KEY` (fail-closed) and isolated Sheets env vars. Banner `[PERINGATAN UNVERIFIED]` + `[DUMMY DATASET]` tetap tampil sampai `docs/sources/` terisi → `pmk37_rules.json` `PRIMARY`.

Detail: `docs/arsitektur.md` §1–§9, `docs/setup_seller_guard_sheets.md`, `docs/assets/bob-integration.md`.

---

## Tumpukan Teknologi | Tech Stack

| Lapisan / Layer | Teknologi | Keterangan / Notes |
|---|---|---|
| Orchestrator | Langflow + MCP `streamablehttp` | `:7860`, `Action+Input`, `project a760286c...` |
| LLM | Gemini 1.5 Flash (`GOOGLE_API_KEY`) | `temp 0.0 / 0.0 / 0.1` locked |
| Embedding | `text-embedding-004` | free tier |
| Vector | `chroma-local` | dual-collection isolated (`astra` opsional) |
| Sanitizer | Python `re` + `hmac` + `hashlib` | stdlib only, HMAC SellerRef |
| Transport | `urllib.request` | stdlib, `allow_redirects`, `SKIPPED` honest |
| Sheets | Google Apps Script `doPost(e)` | `?token=SEITH_WARDEN_...`, 9/11 cols |
| Python | `uv` | `uv sync`, `uv run ...` |

Env matrix: `docs/arsitektur.md` §7. **ID:** `.env` tidak pernah di-commit (`check-ignore` OK). **EN:** `.env` never committed.

---

## Struktur Repositori | Repository Structure

**7 Zones Lock — AGENTS.md §3c**

```
flows/                          Flow Langflow (jangan taruh Python di sini)
  seith_warden_flow.json         SOP flow (10v13e, SHA 4DCB, restore 8F1C)
  seith_warden_seller_guard.json Seller flow (10v13e, SHA 4621, HMAC/BOM/Bar)
  README.md
tools/                          Python uv (fn <50, file 200-400)
  pii_sanitizer.py               re NIK→rek→email
  ceiling_verify.py              re + Graph reVerify
  seller_guard_engine.py         Decimal + SHA-256 + Threshold/Withholding + HMAC
  seller_guard_validator.py      NumericConsistency + EvidenceTable
  sheets_seller_dispatcher.py    urllib SKIPPED/LIVE
data/kb/                        KB SSOT grounding
  padk_2026_curated.md           PADK curriculum
  padk_graph.json                ceiling 0.10/100
  pmk37_config.json              UNVERIFIED null (menunggu docs/sources/)
  pmk37_rules.json               SECONDARY (naik PRIMARY setelah kutip baris sumber)
data/sop_dummy/
  sop_bunga_dummy.md             10 klausul SOP (HIGH3/MED3/LOW2/COMP2)
  sales_export_dummy.csv         66 rows DUMMY as_of 2026-10-01 SHA 4deb
  seller_profile_dummy.json      OP UNDER_500 other 125jt
tests/
  test_scenarios.json            10+3 oracle SOP (S01-S13)
  expected_seller_guard.json     7 cases T01-T07 + dataset_66_rows
  fixtures/config_test.json      scenario_a/b ASSUMPTION_FOR_TEST
  fixtures/config_demo.json      effective 2026-11-01 suspend 08-01..05 ASSUMPTION
  fixtures/ORACLE_manual_2026-11-01.md  533jt 106.60% hand calc
  test_seller_guard.py           8 tests
  test_e2e_seller_guard.py       13 tests S1-S12
docs/ + docs/decisions/          Knowledge SSOT (prd/arsitektur/security/CONTEXT/setup/adr)
.handoff/phase-NN-topic/          Governance (1 fase=1 folder, 00-overview + 01-*.md)
scripts/ + .opencode/ + .github/  Ops & harness
```

**ID:** Cross-zona import liar dilarang — `tools/` tidak import `flows/`; `data/` tidak berisi kode.
**EN:** Cross-zone imports forbidden.

---

## Flow

| Flow | File | Nodes | SHA | Deskripsi |
|---|---|---|---|---|
| SOP | `flows/seith_warden_flow.json` | 10v13e | `4DCB` | `PII → RefMapper → RuleAuditor (+Code+Graph) → RiskSynthesizer → Sheets 9 kolom + Webhook HIGH` — patched `cost_avoided→impact_note`, `hits 35jt=0` |
| Seller Guard | `flows/seith_warden_seller_guard.json` | 10v13e | `4621` | `Seller PII (BOM/,;/strict head) → Verifier (HMAC fail-closed, config_demo ASSUMED, Bar capped, DUMMY/UNVERIFIED banner) → Sheets 11 cols + potential_claim 70k` |

**ID:** Kedua flow `Graph.from_payload` 10v13e `OK`. Import **jangan menimpa**; set Global Variable `SELLER_REF_KEY` (fail-closed `ValueError` jika kosong).
**EN:** Both `Graph.from_payload` 10v13e `OK`. Import as two flows; set `SELLER_REF_KEY` Global Variable.

---

## Data & Oracle

### SOP Dummy
- `data/sop_dummy/sop_bunga_dummy.md` — 10 klausul: `HIGH` 3 (`0,25%`, `0,30%+compound`, `Lock 120%`), `MEDIUM` 3 (SEOJK tanpa pelanggaran), `LOW` 2 (typo), `COMPLIANT` 2 (`0,08%`, `0,10%`).
- Oracle: `tests/test_scenarios.json` S01-S13 + S11 `PROMPT_INJECTION_DEFENSE` + S12 `SECRET_LEAK` + S13 `PAYLOAD_FLOODING 4000`.

### Seller Guard Dummy (DUMMY)
- `data/sop_dummy/sales_export_dummy.csv` — **66 rows** (`67` dengan header) `SHA 4deb` — komposisi: `42×6jt +13×8jt =356jt` baseline + `2×4jt` suspend (074/075) + `3×2jt` over (071-073) + `35jt` crossing 056 + `2` manual (076/077) + `2` DQ + `3jt` injection 080. Semua tanggal `≤2026-10-01` (`as_of 2026-10-01`), label `[DUMMY]` di laporan.
- `seller_profile_dummy.json` — `OP UNDER_500 2026-09-15 skb false other 125jt NIK 3201...`.
- `ORACLE_manual_2026-11-01.md` — hitungan teks tangan:
  `125jt →133jt (074/075) →489jt (baseline) →495jt (071-073) →530jt (056 crossing 2026-10-01 notify 2026-10-31) →533jt (080)` = **106,60% TERLAMPAUI**, `Bar [████████████████████ +6,60%] 106,60%` (20 blok penuh `min(pct,100)/100*20`), `observed 70.000 (40k suspend+30k over)`, `expected 0`, `potential_claim 70.000 (total delta OVER+REFUND)`, `10 temuan (2 DQ +1 crossed +3 over +2 refund +2 manual)`. `total_orders 64` (excl 2 DQ), `total_gross COMPLETED 408jt` (`533−125`), `total_observed 70k`, `total_expected 0`.
- `config_demo.json` — `ASSUMPTION_FOR_TEST` `effective 2026-11-01 suspend 2026-08-01..05` terpisah dari `data/kb/pmk37_config.json` (`UNVERIFIED null`, hapus banner hanya jika `docs/sources/` terisi → `PRIMARY` kutip baris).

**ID:** `potential_claim = Σ delta_idr` `OVER_WITHHELD+REFUND_PENDING`. Formula diverifikasi ke `findings.json`, bukan `0,5%×kumulatif`.
**EN:** `potential_claim = Σ delta_idr` — sum of findings, not `0.5%×cumulative`.

---

## Keamanan | Security

| Prinsip | Implementasi | Status |
|---|---|---|
| Fingerprint integritas | `SHA-256(raw_bytes)` input file + `HMAC-SHA256(SELLER_REF_KEY, NIK)[:12]` | `seller_ref` pseudonim, `input_sha256` di Sheets |
| Presisi finansial | `Decimal(str(v))` + `ROUND_HALF_UP`, toleransi `Rp1`, `RATE_CAP 0,5%` | 100% code, bukan LLM |
| Strict input | `4000 chars + 5000 rows [TRUNCATED]`, `BOM \ufeff` strip, `,/`; case-insensitive header `order_id,gross_invoice_value` atau `ERROR` jelas | `DATA_QUALITY` tidak silent-drop |
| Anti-halusinasi | `NumericConsistencyValidator` — angka di luar `findings.json` → `EXPLANATION_FALLBACK` | `tools/seller_guard_validator.py` |
| Anti-injection | Delimiter `### FINDINGS ###`, `HACKED` diabaikan (080), `P2B` injection `S11` | 13 tests E2E |
| Etika | Menolak saran `memecah omzet/menghindari pajak` → `Preliminary Advisory` + `human_review_required true` | S11 guardrail |
| Banner jujur | `[PERINGATAN UNVERIFIED]` + `[DUMMY]` + `SKIPPED/LIVE` (bukan klaim sukses tanpa bukti) | `config_status UNVERIFIED` |
| Fail-closed | `SELLER_REF_KEY` hanya Global Variable Langflow, `.env` gitignore, `ValueError` jika kosong | `tools/seller_guard_engine.py:414` |

Detail: `docs/security.md`, `docs/arsitektur.md` §6.

---

## Mulai Cepat | Quick Start

```bash
cp .env.example .env  # isi GOOGLE_API_KEY & LANGFLOW_API_KEY (+ SELLER_GUARD_* jika butuh Seller)
uv sync
uv run ruff check .
uv run python tools/pii_sanitizer.py  # → ok
uv run python tools/ceiling_verify.py  # → ok
uv run python -m json.tool tests/test_scenarios.json
uv run langflow run --host 127.0.0.1 --port 7860
# MCP: Invoke-WebRequest http://localhost:7860/api/v1/flows -Headers @{"x-api-key"="$env:LANGFLOW_API_KEY"}  → 200
```

**Seller Guard:**
```bash
uv run python -m json.tool tests/fixtures/config_demo.json  # ASSUMPTION_FOR_TEST
uv run python tests/test_seller_guard.py  # 8 tests
uv run python tests/test_e2e_seller_guard.py  # 13 tests S1-S12
powershell -ExecutionPolicy Bypass -File scripts/verify_seller_guard.ps1  # 5 gates GREEN
```

**Import Flow:** Langflow → Import **dua file terpisah** (`seith_warden_flow.json` + `seith_warden_seller_guard.json`) → set Global Variable `SELLER_REF_KEY` (generate aman) + `SELLER_GUARD_SHEETS_URL` + `SELLER_GUARD_TOKEN`. Ikuti `docs/setup.md` §4 dan `docs/setup_seller_guard_sheets.md` (Apps Script `doPost(e)` + `?token=SEITH_WARDEN...` auto-append).

---

## Verifikasi | Verification

```bash
uv run ruff check .
uv run python tools/pii_sanitizer.py        # NIK→rek→email ok
uv run python tools/ceiling_verify.py       # re + Graph 0,1% ok
uv run python -m json.tool flows/seith_warden_flow.json
uv run python -m json.tool flows/seith_warden_seller_guard.json
powershell -ExecutionPolicy Bypass -File scripts/verify.ps1              # SOP gate GREEN
powershell -ExecutionPolicy Bypass -File scripts/verify_seller_guard.ps1 # Seller 5 gates GREEN (8+13 + Graph 10v13e x2 + SHA 4deb)
```

- SOP: `Graph.from_payload` `10v13e OK` + `verify.ps1` `GATE GREEN`.
- Seller: `threshold 533jt 106,60% + bar [████ +6,60%] + claim 70k` cocok `expected vs engine` (bukan sebaliknya).
- Sheets LIVE: POST nyata `HTTP 200 Row #N` (Row #3 verified), `SKIPPED` jika URL kosong (bukan error).
- Tidak ada fabrikasi angka — `BELUM_DIVERIFIKASI` jika sumber belum ada.

---

## Dokumentasi | Docs

| Dokumen | Isi / Contents |
|---|---|
| `AGENTS.md` | Kontrak 10§ agent + Tier-0 + DoD |
| `docs/arsitektur.md` | Arsitektur dual-flow + MCP + dual-vector (§8 kontrak pisah) |
| `docs/security.md` | Responsible AI, HMAC/PII, HITL, fallback |
| `docs/CONTEXT.md` | Leksikon SEOJK/PADK/Lock Cap/PMK 37 |
| `docs/setup.md` | Setup lengkap 2 flow (`uv sync → :7860 → 8+13 tests`) |
| `docs/setup_seller_guard_sheets.md` | Sheets 11 kolom Seller + Apps Script `SEITH_SELLER_2026` |
| `docs/prd.md` | Requirement + acceptance (§3.7) + monetisasi hipotesis |
| `docs/hacktiv8_hackathon_national.md` | Checklist submission 4 Okt 2026 |
| `docs/AGENTS.local.md` | Keputusan lokal + Decision Log P0 |
| `data/kb/pmk37_*` | KB PMK 37 grounding SSOT + config UNVERIFIED + rules SECONDARY |
| `tests/fixtures/ORACLE_manual...md` | Hand calc 533jt 106,60% |
| `docs/assets/bob-integration.md` | Bob MCP client — protocol identik opencode |

Skill: `.opencode/skills/seith-warden-compliance/SKILL.md` — SSOT loader.

---

## Tata Kelola | Governance

Branch `main` protected. `handoff/NN-topic` dari `main` + worktree `../warden-wt/`. Lifecycle: `git worktree add → TDD → ruff+tests+Graph → dual-review → squash-merge → hapus worktree`. Skill `git-worktree-manager`.

- **Awal sesi:** `Read docs/AGENTS.local.md + .handoff/phase-NN/00-overview.md` + `skill://seith-warden-compliance`
- **Akhir sesi:** `skill://handoff` + `todowrite` + `Accountability ✅/⚠️/🔻/♻️`
- **Fase Aktif:** Phase 00 done + Phase 01 done (SOP `4DCB`) + Phase 02 hardening done + Phase 03 P0 oracle 66 `[4621]` — `verify_seller_guard.ps1` GREEN.
- **Tracer:** `.handoff/README.md` SSOT.

---

## Peta Jalan | Roadmap

**MVP Hackathon (kini):** SOP dual-ingest + Graph 0,1/100 + Code deterministik + 3-agent + Sheets HITL + Seller 66-row Decimal + HMAC/BOM/Bar + Oracle 533jt `4deb`. Pisah flow agar Playground terisolasi. YAGNI OCR/BI/ISO Q2-Q4.

**Q2–Q4:** OCR, multi-tenant, BI/PDP, OJK auto-sync. Free infra MVP = margin tinggi; upgrade Astra/Composio di Q2 saat SOM tertentu. `docs/sources/pmk_37_2025.txt` + `peng_46_2026.txt` belum ada → banner tetap.

---

## Pengumpulan | Submission

**ID:** Tim solo + sertifikat IBM SkillsBuild. Public link `bit.ly/submit-hackathon` Anyone with link + absensi `bit.ly/absensi-hackathon` tiap camp. Revoke H-1 **2026-10-03**: `sk-...` → `${env}` di `.opencode/opencode.json`, `SELLER_REF_KEY` hanya Global Variable (tidak di repo). Deck 10 slide + 5 screenshot HQ 2 flow + video 3–5m dual mode. `commit 1a95d46 + 9133ca7` pushed `7295395` ke `origin/main`. Freeze saat submit (no commit setelah freeze kecuali rotate key via support).

**EN:** Solo team + certificate. Same public link + attendance. Same H-1 revoke. Same deck/video/screenshot. Freeze on submit.

**Responsible AI 15%:** `re + hmac` PII + `HITL Preliminary Advisory` + `PERLU_VERIFIKASI_MANUAL` + grounding `padk_2026_curated.md` + banner `[DUMMY][UNVERIFIED]` — lihat `docs/security.md` Hal 81-85.

---

## Referensi Cepat | Quick Links

`AGENTS.md` · `docs/arsitektur.md` · `docs/security.md` · `docs/CONTEXT.md` · `docs/setup.md` · `docs/setup_seller_guard_sheets.md` · `docs/prd.md` · `docs/AGENTS.local.md` · `flows/seith_warden_flow.json` (4DCB) · `flows/seith_warden_seller_guard.json` (4621) · `data/sop_dummy/sales_export_dummy.csv` (66, 4deb) · `tests/fixtures/ORACLE_manual_2026-11-01.md`
