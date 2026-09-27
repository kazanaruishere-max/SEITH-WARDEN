# SPESIFIKASI KEAMANAN & RESPONSIBLE AI: SEITH-WARDEN
**Sistem:** Supervisory Engine for Institutional Trust & Hazard-mitigation — Workflow Automation & Regulatory Detection Engine Network  
**Standar:** IBM Responsible AI Guidelines, ISO/IEC 42001 (AIMS), UU PDP No. 27/2022 — Selaras PDF Hal 80-85

## 1. Framework Responsible AI (PDF Hal 81)

Risiko etis muncul dalam pengumpulan data, output model, tindakan otomatis, dan cara pengguna menafsirkan sistem. Perlindungan yang benar bergantung pada kerugian jika sistem salah.

| Data Responsibility (Minimalisasi & Privasi) | Output Responsibility (Grounding & Anti-Halusinasi) | Action Responsibility (Human-in-the-Loop) |
|:---|:---|:---|
| PII Sanitizer Layer — hanya klausul perlu | Strict Vector Grounding — sitasi PADK wajib | Preliminary Advisory Only — bukan vonis hukum |
| No Escrow/Customer Storage | Zero Creative Generation — jangan karang pasal | Mandatory Human Sign-off — Compliance Officer putuskan |
| Session-only Vectoring — hapus setelah export | Fallback `PERLU_VERIFIKASI_MANUAL` bila ambigu | Conditional Webhook HIGH only — LOW/MEDIUM skipped |

## 2. Tanggung Jawab Data — Minimalisasi & Privasi (PDF Hal 84)

- **Kumpulkan seminim mungkin:** Hanya proses teks klausul regulatori dan ketentuan operasional. Dilarang masukkan data nasabah, transaksi perorangan, NIK, nomor rekening escrow, identitas pengurus ke pipeline embedding. Prototipe tidak perlu data skala produksi untuk tunjukkan workflow bertanggung jawab.
- **PII Stripping (regex stdlib) sebelum chunk & embedding:**
```python
import re
def sanitize_sop_text(raw_text: str) -> str:
    text = re.sub(r'\b\d{16}\b', '[REDACTED_NIK]', raw_text)
    text = re.sub(r'\b(?:\d[ -]*?){13,19}\b', '[REDACTED_ACCOUNT_NO]', raw_text)
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', text)
    return text
```
Urutan `NIK → rekening → email` (NIK 16 digit dulu agar tidak tertelan regex 13-19). Lihat `tools/pii_sanitizer.py` — `fn <50`.

- **Kontrol akses:** Kredensial di luar flow (`${env}`), batasi file bersama, hindari ekspos konten pribadi di log/demo. `flows/*.json` tidak hardcode secret. `opencode.json` → `.opencode/opencode.json` dengan `${LANGFLOW_API_KEY}`.
- **Rencanakan penghapusan data:** Vector store SOP bersifat ephemeral/session-based — dapat dihapus seketika setelah laporan diekspor. Tentukan retensi: input SOP di `chroma_db/` hanya sesi, dokumen hasil di Sheets adalah audit trail (9 kolom) dengan akses terbatas reviewer. Lihat `docs/arsitektur.md §2`.

## 3. Tanggung Jawab Output — Grounding & Anti-Halusinasi (PDF Hal 81-82,85)

- **Mendasarkan klaim penting:** Larang merekomendasikan pasal atau angka di luar data yang berhasil ditarik dari `collection_ojk_padk2026` (`data/kb/padk_2026_curated.md`). Cabut KB = produk mati.
- **Circuit-breaker tunggal:** Jika teks SOP tidak menyebutkan parameter finansial eksplisit (misal hanya "bunga kompetitif") → agen DILARANG berasumsi melanggar → wajib:
```json
{"status": "PERLU_VERIFIKASI_MANUAL", "catatan": "Klausul ambigu: angka spesifik suku bunga per hari tidak dicantumkan secara eksplisit."}
```
Fallback tunggal sinkron di `docs/CONTEXT.md` + `AGENTS.md` + `docs/arsitektur.md §6`.

- **Sitasi wajib:** Nama peraturan + Bab/Pasal/Ayat (contoh: PADK OJK No. 12/PADK.05/2026 Bab III Pasal 8 Ayat 2). Setiap temuan tanpa sitasi = FAIL. Sumber ditampilkan transparan: apakah jawaban berasal dari catatan upload (SOP), hasil tool (PADK retrieval), atau penalaran model umum (PDF Hal 85).

## 4. Tanggung Jawab Tindakan & Human-in-the-Loop (PDF Hal 81-82)

- Status hukum keluaran adalah **Preliminary Advisory**, bukan fatwa hukum atau sertifikat kepatuhan. Sistem memerlukan konfirmasi manusia sebelum menyampaikan pesan/keputusan/tindakan eksternal berdampak besar.
- AI mengidentifikasi celah dan merekomendasikan draf perbaikan; keputusan akhir ratifikasi SOP dan pelaporan ke OJK berada 100% di Compliance Officer manusia.
- **Pertahankan kontrol (PDF Hal 85):** Izinkan pengguna meninjau konten consequential dan mengonfirmasi tindakan eksternal sebelum irreversible. Webhook `HIGH` hanya `sent` setelah JSON ditampilkan; `LOW/MEDIUM` → `skipped`.
- Disclaimer wajib di setiap export:
> "Laporan ini disusun oleh sistem otomasi SEITH-WARDEN untuk tujuan audit kepatuhan internal. Seluruh temuan dan rekomendasi wajib divalidasi oleh tim Legal & Compliance berwenang sebelum diimplementasikan secara operasional."

## 5. Keadilan & Anti-Diskriminasi — Bias dan Fairness (PDF Hal 83)

- **Identifikasi kelompok:** Daftar siapa yang akan pakai (compliance, legal, risk) dan siapa terdampak tidak langsung (debitur fintech, UMKM) meski tidak interaksi langsung.
- **Bandingkan hasilnya:** Uji apakah bahasa (Indonesia formal vs typo), disabilitas, konektivitas, lokasi, atau latar belakang mengubah kualitas jawaban/akses. Agent 2 dilengkapi aturan deteksi klausul diskriminatif berbasis SARA, gender, atau domisili yang melanggar inklusi keuangan OJK.
- **Tanggapi jelas:** Tingkatkan data dan desain jika mungkin, dokumentasikan keterbatasan di deck (slide Responsible AI), dan berikan alternatif manusia (HITL) untuk kasus penting.

Rencana uji bias skor 15%: uji SOP klausul identik dengan variasi ejaan vs sitasi PADK tetap sama; `PERLU_VERIFIKASI_MANUAL` tidak bias ke `violation`.

## 6. Transparansi yang Membantu Pengguna Percaya (PDF Hal 85)

- **Jelaskan sumbernya:** Tunjukkan apakah jawaban berasal dari catatan upload (SOP `collection_sop_internal`), hasil tool (PADK `collection_ojk_padk2026`), atau penalaran model umum. JSON `legal_reference` wajib isi.
- **Berikan disclaimer akan randomness:** Gunakan batasan jelas dan pesan penolakan daripada sajikan output dengan keyakinan sama. Temp `0.0/0.0/0.1` lock + `Preliminary Advisory`.
- **Pertahankan kontrol:** Izinkan review sebelum kirim Sheets/Webhook. Log `sheets_status/webhook_status` transparan di `generate_compliance_remediation_log`.

## 7. Manajemen Secret & Kredensial (PDF Hal 42-47)

- Kredensial (`GOOGLE_API_KEY`, `LANGFLOW_API_KEY`, `SHEETS_*`, `COMPOSIO_API_KEY`) tidak pernah hardcode di flow JSON — injeksi via environment variables dan Langflow Global Variables (PDF Hal 47: Global Variables → Add New).
- Policy solo free (H-1 Rule): key plaintext lokal di `.opencode/opencode.json` diizinkan dev-only; wajib revoke/ganti `${env}` sebelum submit public link 2026-10-03. `.env` tidak pernah commit.
- `.env.example` adalah placeholder; `.gitignore` memblokir `.env` dan `flows/*.json` berisi secret.

## 8. Transport Security

- Komunikasi client ↔ Langflow MCP Server wajib HTTPS/TLS 1.3.
- Endpoint MCP menerapkan bearer `x-api-key` (`LANGFLOW_API_KEY`) — tanpa key → 401. Verifikasi pra-demo: `Invoke-WebRequest http://localhost:7860/api/v1/flows -Headers @{"x-api-key"="$env:LANGFLOW_API_KEY"}` harus 200.
- Detail integrasi Bob formalitas: `docs/assets/bob-integration.md` Hal 56-60.

## 9. Verification Gate

Lulus `uv run ruff check .` + sitasi PADK ter-grounding + fallback test (klausul ambigu → `PERLU_VERIFIKASI_MANUAL`) + transparansi sumber sebelum klaim selesai. Lihat `AGENTS.md §7 DoD`.
