# Phase 03 — Seller Payout & PPh 22 Guard (PMK 37/2025)

**Goal:** Membangun modul compliance baru "Seller Payout & PPh 22 Guard" untuk mengawal kepatuhan pemungutan PPh 22 marketplace (0,5%) dan melindungi hak bebas pungut UMKM/OP (ambang Rp500 juta) sesuai PMK 37/2025, dengan integritas kalkulasi finansial deterministik (`Decimal`), enkripsi/hashing SHA-256 anti-tamper, isolasi flow tanpa modifikasi `database.db`, serta mitigasi celah keamanan menyeluruh (Judging 30/20/20/15/10/5).

---

## 1. WBS & Tahapan Pelaksanaan

| Tahap | Topik / Slice | Dokumen Handoff | Deliverables Utama | Gate Verifikasi | Status |
|:---|:---|:---|:---|:---|:---|
| **0** | Verifikasi Regulasi & Oracle Tangan | `01-tahap0-regulatory-verification.md` | `data/kb/pmk37_rules.json`<br>`data/kb/pmk37_config.json`<br>`tests/fixtures/config_test.json`<br>`tests/expected_seller_guard.json` | 7 Kasus hitungan tangan tervalidasi kalkulator, config `UNVERIFIED` aman, no pasal liar | pending |
| **1** | Engine Deterministik & SHA-256 | `02-tahap1-deterministic-engine.md` | `tools/seller_guard_engine.py`<br>`tests/test_seller_guard.py` | Pytest 100% pass (Decimal exact, SHA-256 hash valid, boundary rules lulus) | pending |
| **2** | Data Dummy Realistis & Oracle Final | `03-tahap2-data-fixtures-oracle.md` | `data/sop_dummy/sales_export_dummy.csv`<br>`data/sop_dummy/seller_profile_dummy.json` | 60–120 baris CSV multi-marketplace (A, B, C) cocok 100% dengan expected oracle | pending |
| **3** | Langflow Custom Component & Flow | `04-tahap3-langflow-canvas.md` | `flows/seith_warden_seller_guard.json` (Stage 3) | `Graph.from_payload` sukses: semua vertex build sukses dan semua edge tersambung | pending |
| **4** | Agent Explainer, Drafter & Numeric Validator | `05-tahap4-agent-numeric-validator.md` | `flows/seith_warden_seller_guard.json` (Final)<br>`tools/seller_guard_validator.py` | Halusinasi angka diblokir 100%, injection di nama produk diabaikan, fallback aktif | pending |
| **5** | Sheets Dispatcher & Webhook Isolation | `06-tahap5-sheets-dispatcher.md` | `tools/sheets_seller_dispatcher.py`<br>`docs/setup_seller_guard_sheets.md` | Row muncul di Sheet baru (9 kolom), token env terpisah, status jujur LIVE/FAILED/SKIPPED | pending |
| **6** | E2E Security Verification & Reporting | `07-tahap6-e2e-security-verification.md` | `tests/test_e2e_seller_guard.py`<br>`docs/seller_guard_verification.md` | Matrix S1–S12 PASS lengkap (ethical refusal, truncation 5000 rows, SHA-256 tamper test) | pending |

---

## 2. Dependency & Arsitektur Terisolasi

1. **Prinsip Isolasi Mutlak:**
   - Flow inti lama `flows/seith_warden_flow.json` **TIDAK DIUBAH**.
   - Dilarang menulis langsung ke SQLite `database.db`. Flow baru disimpan mandiri di `flows/seith_warden_seller_guard.json` dan di-import via API/UI Langflow.
   - Google Sheet lama untuk audit SOP tidak disentuh. Seller Guard memakai URL dan token terpisah: `SELLER_GUARD_SHEETS_URL` dan `SELLER_GUARD_TOKEN`.
2. **Arsitektur Pipeline:**
   ```
   [sales_export.csv + seller_profile.json]
                     │
                     ▼
        [1. SHA-256 Ingestion Hash & Normalizer] ──► Menghitung sha256(input) -> input_sha256
                     │                                Validasi kolom wajib & konversi ke Decimal
                     ▼
        [2. PII Sanitizer & Pseudonymization]    ──► NIK/NPWP/Rekening/Nama/HP/Alamat -> [REDACTED_*]
                     │                                SellerRef = sha256(NIK)[:12]
                     ▼
        [3. Threshold Guard (Deterministik)]     ──► Hitung kumulatif omzet, rasio Rp500jt, proyeksi 60 hari
                     │
                     ▼
        [4. Withholding Auditor (Deterministik)] ──► Evaluasi PPh 22 0,5% vs Aturan (pmk37_config.json)
                     │
                     ▼
        [5. Findings Aggregator]                 ──► Produksi findings.json + metadata SHA-256
                     │
                     ├─────────────────────────────────────────────────┐
                     ▼                                                 ▼
        [6. Agent-FindingExplainer (0.0)]               [8. Agent-ClaimDrafter (0.1)]
                     │ (Hanya untuk temuan klaim)                      │
                     ▼                                                 ▼
        [7. NumericConsistencyValidator]                [Suntik Tabel Bukti via Kode Python]
       (Verifikasi angka/tanggal vs findings)                          │
                     │                                                 │
                     └────────────────────────┬────────────────────────┘
                                              ▼
                                 [9. Sheets Dispatcher]
                            (SELLER_GUARD_SHEETS_URL + TOKEN)
                                              │
                                              ▼
                             [10. ChatOutput (Formal, No Emoji)]
   ```

---

## 3. Matriks Keamanan Finansial Berlapis (Defense-in-Depth)

| Vektor Ancaman / Celah | Mekanisme Pertahanan (Mitigasi) | Lapisan Penegakan |
|:---|:---|:---|
| **Manipulasi File Input / Tampering** | Pembangkitan `SHA-256` dari konten mentah file CSV + JSON profil saat *ingestion*. Hash disematkan ke dalam `findings.json` dan dicatat ke Google Sheets kolom `Input_SHA256`. Jika file diubah 1 karakter, hash berubah nyata. | `ReportNormalizer` (Python) |
| **Kebocoran Data Finansial & PII** | Deteksi regex untuk NIK (16 digit), NPWP (15-16 digit), No Rekening (9-18 digit), No HP (08xx), Nama Pembeli, dan Alamat Pengiriman. Disamarkan menjadi `[REDACTED_*]`. Identitas seller di-pseudonimkan menjadi `sha256(NIK)[:12]`. | `PIISanitizer` (Python) |
| **Ketidakakuratan Numerik (Float Drift)** | Seluruh perhitungan uang, omzet, pemotongan pajak, selisih (delta), dan persentase wajib memakai `Decimal(str(val))` dengan pembulatan pasti `ROUND_HALF_UP` (toleransi Rp1 dicatat eksplisit). Dilarang memakai tipe data `float`. | Seluruh Engine Python |
| **Halusinasi Angka oleh LLM** | `NumericConsistencyValidator` memindai seluruh angka dan tanggal di output LLM. Jika ada angka/tanggal yang tidak terdapat di `findings.json`, output LLM ditolak dan ditimpa template deterministik `EXPLANATION_FALLBACK`. | Pasca-LLM Validator |
| **Prompt Injection via CSV/Catatan Toko** | Data CSV dibungkus pembatas ketat `### DATA START ###` dan `### DATA END ###`. Prompt LLM menegaskan data adalah payload pasif untuk dianalisis, bukan perintah eksekusi. Perintah berbahaya diabaikan. | Agent System Prompt |
| **Permintaan Penghindaran Pajak (Etika)** | Guardrail etika keras menolak rekomendasi pemecahan omzet, rekayasa entitas, atau penundaan pencatatan untuk menghindari batas Rp500 juta. Respon langsung dialihkan ke konsultan pajak resmi. | Agent System Prompt |
| **Kebocoran Kredensial / Secret Exposure** | URL dan Token Sheets disimpan eksklusif pada `.env` server lokal (`SELLER_GUARD_SHEETS_URL`, `SELLER_GUARD_TOKEN`). Dilarang keras hardcode di flow JSON atau repositori git. Transaksi HTTP via TLS 1.3. | Dispatcher Component |
| **Overclaim & Fabrikasi Regulasi** | Status aturan bertanda `UNVERIFIED` secara otomatis memunculkan banner peringatan formal di atas laporan. Status pengiriman audit trail hanya boleh bernilai `LIVE`, `FAILED`, atau `SKIPPED`. | Report Generator |
| **Denial of Service (DoS) / Memory Exhaustion** | Batasan masukan ketat: maksimal 4.000 karakter untuk teks bebas dan 5.000 baris untuk data transaksi CSV. Kelebihan baris dipotong dan diberi penanda `[TRUNCATED_AT_5000_ROWS_SECURITY_BOUNDARY]`. | ReportNormalizer |

---

## 4. Definisi Selesai (DoD Phase 03)

1. **Verifikasi Regulasi:** `pmk37_rules.json` memiliki rujukan sumber dan level confidence untuk setiap aturan; tidak ada kutipan nomor pasal tanpa teks sumber.
2. **Kesesuaian Oracle:** 100% hasil engine deterministik cocok identik dengan `tests/expected_seller_guard.json` (7 kasus hitungan tangan awal + skenario lengkap).
3. **Kualitas Kode:** `uv run ruff check .` menghasilkan 0 error/warning; fungsi < 50 baris; tidak ada *floating-point math*.
4. **Validasi Langflow:** `flows/seith_warden_seller_guard.json` dapat di-load via script verifikasi Langflow (`Graph.from_payload`), semua vertex build sukses, dan semua edge terhubung.
5. **Integritas Output:** LLM agent tidak memunculkan angka yang berbeda dari `findings.json`; validator fallback teruji aktif saat simulasi injeksi.
6. **Audit Trail Real:** Transaksi uji coba berhasil masuk ke Google Sheets khusus Seller Guard dan menampilkan status `LIVE` (atau `SKIPPED` bila URL kosong).
7. **Keamanan Finansial:** Uji SHA-256 tamper-proof, PII sanitization, dan ethical refusal (S10–S12) lulus 100%.

---

## 5. Referensi Regulasi & Arsitektur
- Siaran Pers DJP SP-14/2026 (1 Juli 2026) mengenai implementasi PMK 37/2025.
- Artikel Edukasi DJP (31 Juli 2026) terkait tata cara pemungutan PPh 22 dan surat pernyataan Rp500 juta.
- Berita Periskop.id (18 Sep 2026) mengenai jadwal penundaan implementasi 1 November 2026.
- `AGENTS.md` (Tata kelola repositori, Boy Scout rule, dan Verification Gate).
