# PANDUAN UTAMA HACKATHON NASIONAL HACKTIV8 X IBM 2026
**Program:** IBM SkillsBuild University Education  
**Nama Proyek:** SEITH - WARDEN (PADK Migration & Rate-Cap Compliance Radar)  
**Tema Terpilih:** Financial  
**Batas Pengumpulan (Deadline):** 4 Oktober 2026  

---

## 1. Ringkasan Eksekutif & Ketentuan Kompetisi

### 1.1 Persyaratan Peserta & Tim
1. **Format Keanggotaan:** Individu atau Tim maksimal **2 orang**.
2. **Syarat Kelulusan Mutlak:** Seluruh anggota tim wajib telah menyelesaikan program dan memegang sertifikat resmi **IBM SkillsBuild University Education 2026**.
3. **Link Operasional Utama:**
   * **Absensi & Pengajuan Ide:** `bit.ly/absensi-hackathon` (Wajib diisi pada setiap sesi kegiatan hackathon camp).
   * **Portal Pengumpulan Final (Submission):** `bit.ly/submit-hackathon` (Deadline: 4 Oktober 2026).

### 1.2 Ketentuan Teknologi & Arsitektur Solusi
* **Backend Engine:** Menggunakan **Langflow** untuk membangun workflow AI Agent terstruktur berbasis Large Language Model (LLM), Document Ingestion, Vector Retrieval (RAG), Chained Reasoning, dan External Tool-Calling.
* **Protokol Integrasi (MCP):** Langflow dikonfigurasi dan di-expose sebagai **MCP (Model Context Protocol) Server**. Hal ini memungkinkan tools kepatuhan (compliance tools) dipanggil oleh client eksternal berbasis standar terbuka model context protocol.
* **Standar Penamaan Tool (Tool Naming Convention):** Mengikuti format wajib `Action + Input`, deskriptif dan eksplisit (contoh: `audit_sop_regulatory_reference`, `evaluate_rate_cap_substance`, `export_compliance_report`).

---

## 2. Matriks Bobot Penilaian (Preliminary Round)

Berdasarkan silabus resmi penilaian preliminary, evaluasi berfokus utama pada **Validasi Ide, Inovasi, Model Bisnis, dan Partisipasi Camp**.

| No | Elemen Penilaian | Bobot | Kriteria Kunci yang Dievaluasi | Strategi Unggul SEITH - WARDEN |
|:---|:---|:---:|:---|:---|
| **1** | **Innovation, Creativity, Feasibility & Monetization** | **30%** | Orisinalitas konsep, diferensiasi dari kompetitor, kelayakan teknis implementasi, roadmap eksekusi terukur, serta **model bisnis dan monetisasi yang jelas**. | Menyasar isu terkini 2026: Migrasi SEOJK ke PADK dan batas bunga 0,1%/hari + Lock Cap 100%. Dilengkapi model bisnis **B2B SaaS RegTech** dengan tiering langganan bulanan yang realistis untuk fintech/P2P lending. |
| **2** | **Problem Clarity & Relevance** | **20%** | Definisi masalah spesifik dengan konteks numerik/regulatori, urgensi tinggi, keselarasan masalah dengan solusi AI, serta adanya data/bukti pendukung. | Problem statement berakar pada regulasi riil OJK (POJK 40/2024, PADK 2026, UU P2SK No. 4/2026). Ratusan halaman SOP manual rentan denda sanksi administratif dan pencabutan izin operasional. |
| **3** | **User Impact & Benefits** | **20%** | Nilai manfaat terukur (efisiensi waktu, reduksi biaya, mitigasi risiko sanksi), identifikasi target user spesifik, serta dampak positif terhadap ekosistem industri. | Memangkas durasi review kepatuhan SOP internal hingga **85%** (dari 14 hari kerja menjadi hitungan jam), mencegah denda kepatuhan hingga miliaran rupiah, dan melindungi hak debitur dari predatory lending. |
| **4** | **Responsible AI Implementation** | **15%** | Etika AI, privasi data, mitigasi bias/halusinasi, transparansi rujukan keputusan, mekanisme *Human-in-the-Loop* (HITL), dan perlindungan data sensitif. | AI tidak pernah memutus vonis legal secara sepihak (hanya preliminary advisory). Dilengkapi *PII Stripping Layer* sebelum data di-embed, sitasi pasal berbasis bukti dokumen, dan fallback *"Perlu Verifikasi Manual"* jika ambigu. |
| **5** | **Technical Execution & Prototype Functionality** | **10%** | Kematangan arsitektur, stabilitas prototipe fungsional, penggunaan modular Langflow + MCP Server, kode bersih, dan kesiapan demonstrasi. | Workflow multi-agent 3-layer di Langflow yang modular, skema output JSON terstruktur, integrasi tool eksternal (Sheets API & Webhook Escalation), serta ready-to-run. |
| **6** | **Hackathon Class Participation** | **5%** | Kehadiran aktif dalam hackathon camp dan konsistensi progres. | Rekam jejak presensi melalui `bit.ly/absensi-hackathon`. |

---

## 3. Checklist Berkas Submission (5 Bagian Utama)

Sesuai dengan standar formulir pengumpulan final (*Slide 86*), berikut 5 bagian wajib yang harus dipersiapkan:

### Bagian 1: Informasi Tim
- [ ] Nama Tim & Anggota (maksimal 2 orang).
- [ ] Email & Kontak aktif ketua tim.
- [ ] Bukti/Screenshot Sertifikat Kelulusan **IBM SkillsBuild University Education 2026** per anggota tim.

### Bagian 2: Project Overview
- [ ] **Judul Proyek:** SEITH - WARDEN (Supervisory Engine for Institutional Trust & Hazard-mitigation — Workflow Automation & Regulatory Detection Engine Network).
- [ ] **Tema:** Financial.
- [ ] **Deskripsi Singkat (Elevator Pitch):** AI Agent audit kepatuhan regulasi OJK otomatis yang mendeteksi klausul usang (SEOJK → PADK) dan pelanggaran batas bunga pinjaman 0,1%/hari pada SOP internal fintech lending/BNPL.
- [ ] **Problem Statement & Target User:** Tim Compliance, Legal Counsel, dan Risk Management pada industri P2P Lending / Multifinance / Bank Digital.
- [ ] **Fitur Utama Solusi:** Dual-knowledge ingestion, cross-regulatory code mapping, substantive numerical gap audit, dan automated risk escalation.

### Bagian 3: Bukti Teknis (Technical Proof)
- [ ] File Export Workflow Langflow (`seith_warden_flow.json`).
- [ ] Dokumentasi Arsitektur Sistem (`arsitektur.md`).
- [ ] Konfigurasi MCP Server Langflow (`Action + Input`).
- [ ] Log / Output eksekusi validasi JSON.

### Bagian 4: Pitching Deck & Bukti Visual
- [ ] Slide Pitch Deck PDF (maksimal 10 slide: Problem, Solution, Market/Monetization, Architecture, Responsible AI, Roadmap, Team).
- [ ] 3–5 Screenshot Prototipe Berkualitas Tinggi:
  1. Kanvas alur kerja Langflow (Multi-Agent chaining).
  2. Input SOP dummy vs Knowledge Base PADK.
  3. Hasil eksekusi terstruktur (JSON output dengan tingkat risiko).
  4. Bukti tool-calling (pencatatan audit log ke Google Sheets & alert Webhook/Slack).

### Bagian 5: Pernyataan Akhir (Final Declaration)
- [ ] Verifikasi seluruh checklist orisinalitas proyek.
- [ ] Memastikan hak akses file (Google Drive / GitHub repository) telah diset ke **Public / Anyone with the link can view**.

---

## 4. Rencana Kerja Taktis Menuju Deadline 4 Oktober 2026

```
[Minggu 1: Pemadatan Fondasi]
├── Finalisasi Dokumen (hacktiv8, arsitektur, prd, security, agents)
├── Penyusunan Dummy SOP & Knowledge Base PADK OJK 2026
└── Setup Environment Langflow + Vector Store

[Minggu 2: Implementasi Teknis & MCP]
├── Pembangunan 3-Layer Agent Workflow di Langflow
├── Konfigurasi Tool Calling (Spreadsheet API & Webhook)
├── Validasi Pengujian 10 Skenario Kepatuhan (Edge Cases)
└── Expose Langflow Flow sebagai MCP Server Tool

[Minggu 3: Asset Packaging & Submission]
├── Pengambilan 5 Screenshot Prototipe Berkualitas Tinggi
├── Pembuatan Slide Pitch Deck (Format Standar IBM/Hacktiv8)
├── Rekaman Video Demo Walkthrough (3-5 Menit)
└── Final Submission di bit.ly/submit-hackathon
```
