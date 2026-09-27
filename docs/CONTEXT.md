# CONTEXT — Leksikon Domain SEITH-WARDEN

Sumber kebenaran tunggal istilah OJK dan kontrak audit. Rujuk dokumen ini di semua prompt dan docs agar tidak ada makna ganda. Repo ini full Bahasa Indonesia kecuali README yang bilingual.

| Istilah | Definisi & Aturan Kontrak |
|:---|:---|
| **SEOJK** | Surat Edaran OJK — format regulasi lama, dinyatakan usang dan wajib migrasi ke PADK pada 2026. Enum `format_type: "SEOJK"` dengan `status: "DEPRECATED"` di output Agent 1. |
| **PADK** | Peraturan Anggota Dewan Komisioner OJK — format baru 2026 pengganti SEOJK. Koleksi `collection_ojk_padk2026` ber-grounding ke `data/kb/padk_2026_curated.md`. |
| **POJK** | Peraturan OJK — regulasi tingkat OJK yang tetap berlaku (contoh: POJK 40/2024). Enum `format_type: "POJK"` dengan `status: "ACTIVE"` bila masih berlaku. |
| **Lock Cap 100%** | Ketentuan mutlak: total akumulasi bunga harian + denda keterlambatan + biaya platform/administrasi tidak boleh melampaui 100% dari nilai pokok pinjaman. Sitasi: PADK 2026 Pasal 12 Ayat 3. Pelanggaran → `risk_level: "HIGH"`. |
| **Bunga 0,1%/hari** | Plafon batas maksimum manfaat ekonomi untuk pinjaman konsumtif: maksimal 0,1% per hari kalender dari pokok (produktif 0,2%). Sitasi: PADK 2026 Pasal 12 Ayat 1. `daily_rate_percent: 0.10` adalah batas; `0.25` → violation. |
| **P2SK / UU 4/2026** | UU Pengembangan dan Penguatan Sektor Keuangan — berlaku 17 Juni 2026, dasar integrasi data OJK. |
| **PMK 8/2026** | Peraturan Menteri Keuangan tentang integrasi data OJK ke DJP untuk verifikasi kepatuhan pajak otomatis. |
| **PERLU_VERIFIKASI_MANUAL** | Fallback tunggal yang wajib dipakai seluruh agen bila teks SOP tidak mencantumkan angka eksplisit (misal hanya "bunga kompetitif"). Dilarang menebak angka. Enum `status: "PERLU_VERIFIKASI_MANUAL"` di Agent 2 dan JSON fallback §6. |
| **SOP** | Standard Operating Procedure internal fintech/BNPL/bank digital — 150–400 halaman, target audit SEITH-WARDEN. Di-vector ke `collection_sop_internal` setelah PII sanitizing. |
| **HITL** | Human-in-the-Loop — output SEITH-WARDEN berstatus Preliminary Advisory; keputusan final di Compliance Officer manusia. Webhook `HIGH` tetap butuh sign-off manusia. |
| **Preliminary Advisory** | Disclaimer wajib di setiap JSON output Agent 3 — bukan opini hukum resmi. Teks: "Laporan ini ... wajib divalidasi oleh tim Legal & Compliance..." |
| **RATE_CAP_BREACH** | Kategori temuan Agent 3 bila bunga melampaui 0,1%/hari. Contoh: Pasal 1 `0,25%/hari` → `RATE_CAP_BREACH`, `severity: HIGH`. |
| **DEPRECATED_REGULATORY_CODE** | Kategori temuan bila SOP masih merujuk kode SEOJK usang. Severity `MEDIUM` bila angka belum terbukti melanggar. |
| **Action + Input** | Konvensi penamaan tool MCP wajib Hacktiv8 (PDF Hal 27-29): kata kerja + informasi input. Contoh `audit_sop_regulatory_reference` (audit + sop_text), `evaluate_rate_cap_substance` (evaluate + daily_rate_percent), `generate_compliance_remediation_log` (generate + clause_id/risk_level). Bob menemukan tool via nama & deskripsi ini. |

**Konteks Bisnis:** Target pengguna adalah tim Compliance/Legal & Risk Management di fintech lending/BNPL/bank digital skala kecil-menengah tanpa tim compliance besar. Pain: audit SOP manual 10–14 hari rentan human error → SEITH-WARDEN memotong 85% menjadi hitungan jam dan mencegah denda miliaran serta pembekuan izin OJK. Judging: 30% Innovation+Monetisasi (SaaS Rp4,9/12,5/24,9jt), 20% Problem Clarity, 20% User Impact, 15% Responsible AI, 10% Technical. Integrasi: Langflow + Bob via MCP `streamablehttp` (Bob formalitas, runtime `opencode`) — detail `docs/assets/bob-integration.md`.
