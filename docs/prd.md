# PRODUCT REQUIREMENTS DOCUMENT — SEITH-WARDEN
**Nama Produk:** SEITH-WARDEN (Supervisory Engine for Institutional Trust & Hazard-mitigation — Workflow Automation & Regulatory Detection Engine Network)  
**Versi:** 1.0.0 MVP Release  
**Kategori:** B2B RegTech / Automated Compliance Radar  
**Target Pasar:** Fintech P2P Lending, PayLater/BNPL, Bank Digital berlisensi OJK  
**Stack:** Langflow + MCP `streamablehttp` `:7860` + Gemini 1.5 Flash free tier + `chroma-local` dual-vector + Sheets/Webhook free

> Dokumen ini adalah SSOT bisnis. Kontrak teknis rinci ada di `AGENTS.md §2` (prompt & MCP) dan `docs/arsitektur.md §2-4` (pipeline & dual-vector) — PRD tidak menduplikasi kontrak, hanya menunjuk.

---

## 1. Latar Belakang & Identifikasi Masalah

### 1.1 Konteks Regulasi Finansial 2026
1. **Transisi Format Dokumen Hukum:** OJK menggantikan seluruh instrumen Surat Edaran OJK (SEOJK) menjadi Peraturan Anggota Dewan Komisioner (PADK). SOP internal yang merujuk kode SEOJK lama dinyatakan usang.
2. **Penurunan Batas Bunga Konsumtif:** Maksimal 0,1% per hari (turun dari 0,4% 2023 dan 0,3% 2024), disertai Lock Cap 100% — total bunga + denda + biaya admin tidak boleh melebihi 100% pokok pinjaman.
3. **Pemberlakuan UU P2SK No. 4/2026 & PMK 8/2026:** Integrasi data OJK ke DJP membuat audit kepatuhan near-instant.

### 1.2 Masalah Nyata di Industri
- **Audit Manual 150–400 Halaman:** Membaca dan menandai klausul usang butuh 10–14 hari kerja per siklus regulasi.
- **Human Error & Blind Spots:** Angka minor pada sub-klausul denda luput, menyebabkan pelanggaran Lock Cap tidak sengaja.
- **Sanksi Katastropik:** Peringatan bertahap, pembekuan izin penyaluran dana, denda Rp100jt–1M, hingga pencabutan izin.

### 1.3 Canvas Masalah yang Baik (PDF Hal 73)

| Elemen | SEITH-WARDEN |
|:---|:---|
| **User + Kondisi** | Compliance officer fintech lending/BNPL kecil-menengah mencari kebijakan bunga sebelum audit OJK, SOP 150–400 halaman tersebar. |
| **Needs + Tantangan** | Butuh jawaban cepat apakah SOP masih SEOJK usang dan bunga ≤0,1%/hari, namun dokumen tersebar dan angka minor luput. |
| **Insight (mengapa gagal)** | Audit manual 10–14 hari, tidak ada tool mapping SEOJK→PADK terotomatisasi. |
| **Evidence** | SOP dummy 10 klausul (HIGH 3, MEDIUM 3, LOW 2, COMPLIANT 2) + sitasi PADK 2026 Pasal 12 Ayat 1-3 + POJK 40/2024 + UU P2SK 4/2026 yang dapat diuji juri selama hackathon. |
| **Measure** | Potong waktu 85% (14 hari→jam), hemat retainer Rp35–60jt→SaaS Rp4,9jt, 0 pelanggaran Lock Cap terlewat. |
| **How Might We** | Bagaimana kita bantu compliance officer mencapai audit PADK tuntas meskipun SOP ratusan halaman dan aturan baru 0,1%/hari? |

**Momen tertentu (PDF Hal 74):** Pergantian regulasi Q1 2026 sebelum tenggat audit triwulan. **Konsekuensi nyata:** Denda Rp100jt–1M + pembekuan izin + trust debitur hilang. **Bukti terjangkau:** Upload SOP dummy → 3-agent chain → JSON risk → Sheets + Webhook `HIGH`.

---

## 2. Profil Pengguna Sasaran

| Persona | Peran & Tanggung Jawab | Kebutuhan Utama | Nilai SEITH-WARDEN |
|:---|:---|:---|:---|
| **Head of Compliance** | Legalitas operasional & pelaporan OJK | Pastikan 100% SOP bermigrasi ke PADK sebelum audit | Visibilitas skor kepatuhan, pemetaan otomatis, audit trail 9 kolom |
| **Legal & Regulatory Counsel** | Draf revisi klausul & kontrak pinjaman | Draf klausul sesuai nomenklatur OJK | Draf pengganti siap pakai, potong drafting 80% |
| **Risk Management Officer** | Kalkulasi bunga/denda di core lending | Tahu pasti apakah bunga >0,1%/hari | Deteksi deviasi numerik + eskalasi HIGH instan |

### 2.1 User Journey & Alur End-to-End (PDF Hal 79 — Input → Keputusan → Hasil)

```
Input: Upload SOP dummy (data/sop_dummy/sop_bunga_dummy.md Pasal 1 `0,25%/hari`) + KB PADK curated (data/kb/padk_2026_curated.md)
  → Keputusan 1: PII sanitizing (NIK→rekening→email) + chunk SOP 800/150 vs PADK hierarchical Bab→Pasal→Ayat → dual retriever isolated
  → Keputusan 2: RefMapper (0.0) deteksi SEOJK usang | RuleAuditor (0.0) bandingkan 0,1%/Lock100% | RiskSynthesizer (0.1) skor HIGH/MEDIUM/LOW
  → Keputusan 3: Tool gate — Sheets selalu tulis, Webhook hanya HIGH
  → Hasil: JSON terstruktur (audit_summary + findings + draft_recommendation + Preliminary Advisory) + baris Sheets + alert Slack/webhook.site bila HIGH + Chat Output ringkasan
  → Fallback: Bila klausul tanpa angka eksplisit → PERLU_VERIFIKASI_MANUAL (jangan tebak)
```

Kriteria sukses journey: juri dapat replikasi dalam 5 menit via `docs/setup.md` — upload → chain → JSON → Sheets terlihat.

---

## 3. Fitur Utama Produk

### 3.1 Dual-Knowledge Ingestion & Vector Indexing
- **Input:** SOP internal (PDF/txt) dan KB regulasi PADK 2026.
- **Capabilities:** PII sanitizing regex stdlib (`tools/pii_sanitizer.py` urutan NIK→rekening→email, `fn <50`), ekstraksi hierarki, indexing dual-vector isolated `chroma-local`.
- **Rujukan Teknis:** `docs/arsitektur.md §2` — chunk SOP 800/150 recursive vs PADK hierarchical.

### 3.2 Automated Regulatory Code Cross-Mapping (SEITH-RefMapper)
- **Capabilities:** Deteksi rujukan kode lama (misal `19/SEOJK.05/2023`) dan pemetaan presisi ke PADK 2026.
- **Output:** `detected_references[]` — lihat kontrak SSOT §3.8.
- **Prompt Terkunci:** `AGENTS.md §2.1` temp `0.0`.

### 3.3 Substantive Numerical Compliance Engine (SEITH-RuleAuditor)
- **Capabilities:** Ekstrak bunga harian, denda, biaya admin, akumulasi total dan konfrontasi ke 0,1%/hari & Lock Cap 100%.
- **Output:** `substantive_evaluations[]` + `PERLU_VERIFIKASI_MANUAL` bila ambigu — lihat §3.8.
- **Prompt Terkunci:** `AGENTS.md §2.2` temp `0.0`.

### 3.4 Risk Scoring & Clause Recommendation Drafter (WARDEN-RiskSynthesizer)
- **Capabilities:** Klasifikasi TINGGI (pelanggaran 0,1%/Lock100%/denda ganda), SEDANG (SEOJK tanpa pelanggaran angka), RENDAH (typo/istilah minor) + draf klausul pengganti legal drafting.
- **Output:** JSON baku `audit_summary + findings + draft_recommendation + disclaimer` — lihat §3.8.
- **Prompt Terkunci:** `AGENTS.md §2.3` temp `0.1`.

### 3.5 Automated Audit Trail & High-Risk Alert Escalation
- **Capabilities:** Tulis ke Google Sheets (9 kolom SSOT — lihat `docs/arsitektur.md §5`) dan Webhook Slack/`webhook.site` free hanya bila `risk_level=="HIGH"` (conditional node).
- **MCP Tool:** `generate_compliance_remediation_log` — `sheets_status/webhook_status`.

### 3.6 Batasan MVP — Yang TIDAK Dikerjakan (OUT)

Agar fokus dan tidak scope-creep selama hackathon:

| OUT di MVP | Alasan | Kapan |
|:---|:---|:---|
| OCR dokumen scan buram (Vision OCR) | Butuh pipeline tambahan, YAGNI hackathon | Q2 2026 |
| Multi-regulator BI (PBI/PADG) + UU PDP Komdigi | Perlu KB tambahan, pecah fokus PADK | Q3 2026 |
| Real-time sync situs OJK (auto-monitor PADK baru) | Butuh crawler & scheduler | Q4 2026 |
| Multi-tenant & dashboard kuartal komparatif | Butuh auth & storage cross-tenant | Q2 2026 |
| ISO 27001 certification | Butuh audit eksternal | Q3 2026 |
| Astra DB persistent cloud (ganti chroma-local) | Free tier MVP cukup, no vendor lock | Q2 saat SOM >20 klien |

Apa pun di luar §3.1-3.5 adalah OUT sampai Phase 01 selesai dan lolos DoD.

### 3.7 Acceptance Criteria — Given / When / Then (Siap Jadi Test)

| Fitur | Given | When | Then |
|:---|:---|:---|:---|
| **3.1 Ingestion** | SOP `sop_bunga_dummy.md` Pasal 1 berisi `NIK 1234567890123456` dan `4111 1111 1111 1111` | Di-ingest via PII sanitizer + chunk 800/150 | `sanitize_sop_text` → `[REDACTED_NIK]` & `[REDACTED_ACCOUNT_NO]`, chunk tidak bocor PII, `uv run python tools/pii_sanitizer.py → ok` |
| **3.2 RefMapper** | SOP Pasal 1 `19/SEOJK.05/2023`, Pasal 9 `12/PADK.05/2026` | `audit_sop_regulatory_reference(sop_text)` dipanggil | Pasal 1 → `format_type SEOJK status DEPRECATED migration_required true`; Pasal 9 → `format_type PADK status ACTIVE migration_required false`; tanpa kode → `detected_references: []` |
| **3.3 RuleAuditor** | Pasal 1 `0,25%/hari`, Pasal 5 `bunga kompetitif` tanpa angka, Pasal 9 `0,08%/hari` | `evaluate_rate_cap_substance(daily_rate_percent, sop_text)` | `0,25% → violation true breach +0,15% status VIOLATION`; `kompetitif → status PERLU_VERIFIKASI_MANUAL`; `0,08% → violation false COMPLIANT`; Lock Cap `120% → violation true` |
| **3.4 RiskSynthesizer** | Gabungan RefMapper `DEPRECATED` + RuleAuditor `violation true` (Pasal 1) vs `DEPRECATED + violation false` (Pasal 6) vs `COMPLIANT` (Pasal 9) | `WARDEN-RiskSynthesizer` sintesis | Pasal 1 → `risk_level HIGH requires_escalation true legal_reference PADK 2026 Pasal 12 Ayat 1 + draft klausul 0,1%+100%`; Pasal 6 → `MEDIUM`; Pasal 9 → `overall_status COMPLIANT risk_level LOW` + disclaimer `Preliminary Advisory` |
| **3.5 Sheets+Webhook** | Risk HIGH vs MEDIUM | `generate_compliance_remediation_log(risk_level)` | HIGH → `sheets_status ok + webhook_status sent`; MEDIUM/LOW → `sheets_status ok + webhook_status skipped`; Sheets gagal → `sheets_status failed` tapi JSON tetap return (graceful degradation) |

Semua Then di atas harus hijau di `tests/test_scenarios.json` 10 skenario (HIGH 3, MEDIUM 3, LOW 2, COMPLIANT 2).

### 3.8 Kontrak JSON — SSOT Terkunci (Hukum)

Kontrak berikut adalah SSOT — tidak boleh diubah tanpa ADR dan sinkron ke `AGENTS.md §2` + `docs/arsitektur.md §4.1` + `docs/CONTEXT.md`.

| Field | Enum / Type | Sumber |
|:---|:---|:---|
| `detected_references[].format_type` | `SEOJK \| PADK \| POJK` | AGENTS.md §2.1 |
| `detected_references[].status` | `DEPRECATED \| ACTIVE \| UNKNOWN` | AGENTS.md §2.1 |
| `substantive_evaluations[].status` | `VIOLATION \| COMPLIANT \| PERLU_VERIFIKASI_MANUAL` | AGENTS.md §2.2 |
| `substantive_evaluations[].violation` | `boolean` — true bila `found_value > regulatory_ceiling` | arsitektur.md §3 |
| `audit_summary.risk_level` | `HIGH \| MEDIUM \| LOW` | AGENTS.md §2.3 — HIGH=violation numerik, MEDIUM=SEOJK tanpa pelanggaran angka, LOW=typo minor |
| `audit_summary.overall_status` | `NON_COMPLIANT \| COMPLIANT` |  |
| `generate_compliance_remediation_log.risk_level` | `LOW \| MEDIUM \| HIGH` | arsitektur.md §4.1 |
| Fallback tunggal | `PERLU_VERIFIKASI_MANUAL` — exact string di semua agen bila ambigu | CONTEXT.md |

MCP tool naming wajib `Action+Input` (PDF Hal 27-29): `audit_sop_regulatory_reference`, `evaluate_rate_cap_substance`, `generate_compliance_remediation_log` — Bob menemukan tool via nama+deskripsi.

### 3.9 NFR & KPI Terukur

| KPI / NFR | Target MVP | Cara Ukur |
|:---|:---|:---|
| **Waktu audit** | Potong 85% — 14 hari → hitungan jam per SOP 10 pasal | Bandingkan manual 10–14 hari vs run 3-agent chain di Langflow Playground |
| **Akurasi HIGH** | >90% di 10 skenario dummy (3 HIGH harus HIGH, 2 COMPLIANT harus COMPLIANT) | `tests/test_scenarios.json` hijau |
| **Grounding PADK** | 100% temuan wajib sitasi `PADK OJK No. 12/PADK.05/2026 Bab III Pasal 12` dari `data/kb/padk_2026_curated.md` | Audit `findings[].legal_reference` tidak kosong |
| **Latensi per klausul** | <5 detik di Langflow Playground (Gemini Flash free) | Hitung Playground Chat Output |
| **Fallback benar** | 100% klausul ambigu → `PERLU_VERIFIKASI_MANUAL` (tidak tebak) | S05 `bunga kompetitif` di scenarios |
| **PII tidak bocor** | 0 NIK/rekening/email masuk vector | `tools/pii_sanitizer.py` self-check `ok` |
| **Format JSON** | 100% valid, regex fallback bila markdown bocor | `python -m json.tool` di `flows/seith_warden_flow.json` + output Chain |

---

## 4. Model Bisnis & Rencana Monetisasi (Bobot 30%)

### 4.1 Paket Berlangganan

```
┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐
│      TIER STARTER      │  │    TIER PROFESSIONAL   │  │    TIER ENTERPRISE     │
│   Rp 4.900.000 / bln   │  │   Rp 12.500.000 / bln  │  │   Rp 24.900.000 / bln  │
│ (Fintech P2P Seed/PreA)│  │ (Fintech P2P Menengah) │  │  (Fintech Tier 1 & Bank)│
├────────────────────────┤  ├────────────────────────┤  ├────────────────────────┤
│• Kuota 10 Dokumen SOP  │  │• Kuota 35 Dokumen SOP  │  │• Unlimited Dokumen SOP │
│• 2 User Seat Compliance│  │• 5 User Seat           │  │• Unlimited User Seats  │
│• Export Google Sheets  │  │• Export Sheets & PDF   │  │• Dedicated MCP Server  │
│• Basic Rule Checking   │  │• Webhook Slack Alert   │  │• Real-time OJK Sync    │
│• Standard Email Support│  │• Support Prioritas     │  │• Custom LLM Deployment │
│                        │  │                        │  │• Dedicated Legal Eng.  │
└────────────────────────┘  └────────────────────────┘  └────────────────────────┘
```

### 4.2 Market Sizing Indonesia
- **TAM:** ~1.400 lembaga jasa keuangan berlisensi OJK (100+ P2P, 200+ Multifinance, 100+ Bank, 1.000+ BPR).
- **SAM:** ~145 institusi wajib update PADK 2026 (100 P2P + 30 BNPL + 15 Bank Digital).
- **SOM:** 20 platform tahun pertama → **Rp2,5 Miliar ARR**.

### 4.3 Value Proposition & ROI
- Konsultan retainer Rp35–60jt/bulan vs SaaS Rp4,9jt → hemat >70%.
- Denda OJK Rp100jt–1M + pembekuan izin terhindari; lapor 2 pekan → 1 hari.

### 4.4 Diferensiasi vs Kompetitor (PDF Hal 78)

| Kompetitor | Kelemahan | SEITH-WARDEN |
|:---|:---|:---|
| Konsultan manual / spreadsheet | 10–14 hari, human error, tanpa sitasi otomatis | 3-agent chain + sitasi PADK Pasal 12 + JSON terstruktur |
| RAG chatbot generik | Hanya Q&A, tidak deteksi 2-arah format+substansi | Deteksi SEOJK→PADK + evaluasi 0,1%/Lock100% |
| Langflow tanpa MCP/Bob | Tidak callable eksternal | Expose MCP `streamablehttp` + Bob formalitas via opencode (PDF Hal 30-31) |

### 4.5 Risiko, Limitasi & Roadmap Terukur (PDF Hal 66 — untuk 30% Innovation)

**Risiko/Limitasi (jujur di deck):** Hallucinate angka → mitigasi `PERLU_VERIFIKASI_MANUAL` + grounding PADK + `Preliminary Advisory`. Scan buram → YAGNI OCR Q2. `chroma-local` tidak scale enterprise → upgrade Astra Q2 saat SOM >20 klien.

**Roadmap Eksekusi Terukur:**

```
Q1 2026 MVP Validasi ◄ hackathon ini — 3-agent + Sheets+Webhook + 10 skenario + MCP Bob formalitas
Q2 2026 PDF OCR + multi-tenant + dashboard kuartal + beta 5 mitra
Q3 2026 Multi-regulator BI (PBI/PADG) + UU PDP Komdigi + ISO 27001
Q4 2026 Enterprise auto-sync OJK (monitor PADK baru) + ekspansi multifinance/BPR
```

> Strategi jualan: MVP gratis-infra (`chroma-local` + Gemini Flash free) = margin SaaS tinggi untuk fintech kecil; upgrade Astra/Composio di Q2 sebagai scale path — no vendor lock di MVP.

---

## 5. Roadmap Produk (Execution Timeline)

Detail milestone sama — lihat §4.5. Gudang eksekusi: Phase 00 (docs) → Phase 01 (Langflow chain + MCP + Bob formalitas) → Packaging deck + 5 screenshot (PDF Hal 86 §4).

---

## 6. Asumsi, Dependensi & Risiko Teknis

| # | Asumsi / Dependensi | Dampak Jika Gagal | Mitigasi |
|:---|:---|:---|:---|
| 1 | Gemini 1.5 Flash free tier quota tersedia (`text-embedding-004` + `0.0/0.0/0.1`) | Chain tidak jalan | Fallback `PERLU_VERIFIKASI_MANUAL`; dokumentasi `GOOGLE_API_KEY` di `docs/setup.md` |
| 2 | `chroma-local` dual-collection isolated (`collection_sop_internal` 800/150 vs `collection_ojk_padk2026` hierarchical) | Context bleeding SOP↔PADK | Validasi retriever terpisah — `docs/arsitektur.md §2` |
| 3 | Langflow `:7860` never-kill, MCP `streamablehttp` + `x-api-key` | Bob/opencode tidak discover tools | Check `Invoke-WebRequest http://localhost:7860/api/v1/flows` 200 — `AGENTS.md §4 Hard Rules` |
| 4 | Google Sheets API free + `webhook.site`/Slack free | Audit trail/webhook gagal | Graceful degradation — `sheets_status failed` tapi JSON tetap return (`docs/arsitektur.md §6`) |
| 5 | SOP input adalah teks jelas (bukan scan buram) di MVP | OCR diperlukan | OUT di §3.6 — Q2 OCR |
| 6 | KB `data/kb/padk_2026_curated.md` sebagai SSOT grounding | Hallucinate sitasi | Cabut KB = produk mati — `AGENTS.md §4 Hard Rules` |

---

## 7. Referensi SSOT & Traceability

| Dokumen PRD Ini Menunjuk Ke | Untuk |
|:---|:---|
| `AGENTS.md §2` (3 prompt terkunci) | Prompt & temp lock `0.0/0.0/0.1` |
| `AGENTS.md §4` + `§6` | Tier-0 Hard Rules + Contract Rules enum SSOT |
| `docs/arsitektur.md §2-4` | Pipeline PII + chunk + dual-vector + MCP 3 tool schema |
| `docs/arsitektur.md §5-6` | Sheets 9 kolom + webhook HIGH-only + fault tolerance |
| `docs/security.md` Hal 81-85 | Responsible AI — data/output/action + bias + deletion plan |
| `docs/CONTEXT.md` | Lexicon SEOJK/PADK/Lock Cap/P2SK/`PERLU_VERIFIKASI_MANUAL` |
| `docs/setup.md` | Langkah `uv sync → langflow run :7860 → test 10 skenario` |
| `docs/assets/bob-integration.md` | Bob formalitas via opencode — protocol `streamablehttp` identik |
| `docs/hacktiv8_hackathon_national.md` + PDF `docs/assets/Hacktiv8...pdf` | Checklist 5 bagian submission + scoring 30/20/20/15/10/5 |
| `tests/test_scenarios.json` + `data/sop_dummy/sop_bunga_dummy.md` | 10 skenario oracle HIGH/MEDIUM/LOW/COMPLIANT/PERLU_VERIFIKASI |
