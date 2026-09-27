PADK Migration & Rate-Cap Compliance Radar
AI Agent untuk Deteksi Gap Kepatuhan Regulasi OJK di Fintech Lending/BNPL
1. Latar Belakang & Masalah

Konteks regulasi:
Sejak awal 2026, OJK mengganti format regulasi lama (SEOJK — Surat Edaran OJK) menjadi format baru bernama PADK (Peraturan Anggota Dewan Komisioner). Bersamaan dengan itu, ada perubahan substansi yang signifikan: batas maksimal bunga pinjaman konsumtif fintech lending turun menjadi 0,1% per hari (dari sebelumnya 0,4%/hari di 2023), disertai ketentuan Lock Cap 100%. UU Nomor 4 Tahun 2026 yang memperbarui UU P2SK juga mulai berlaku 17 Juni 2026, dan integrasi data OJK ke DJP lewat PMK 8/2026 membuat kepatuhan pajak terverifikasi otomatis.

Masalah nyata:
Perusahaan fintech lending/BNPL/bank digital di Indonesia punya dokumen SOP internal (kebijakan bunga, proses penagihan, tata kelola data) yang ditulis merujuk regulasi lama. Ketika format regulasi berubah (SEOJK → PADK) dan substansinya berubah (batas bunga turun drastis), tim compliance/legal harus:

Membaca ratusan halaman SOP secara manual.
Mencari klausul mana yang masih merujuk kode SEOJK usang.
Mengecek apakah angka bunga/aturan operasional di SOP masih sesuai batas baru.
Menyusun rekomendasi revisi — semuanya manual, lambat, dan rawan human error.

Dampak kalau tidak ditangani: sanksi administratif dari OJK (peringatan tertulis, pembekuan kegiatan usaha, hingga denda), reputasi rusak, dan risiko konsumen dirugikan karena SOP yang tidak update.

Target pengguna: tim Compliance/Legal & Risk Management di perusahaan fintech lending, BNPL, atau bank digital skala kecil-menengah yang tidak punya tim compliance besar/dedicated legal-tech tool mahal.

2. Objektif

Membangun AI agent yang secara otomatis:

Mendeteksi klausul SOP internal yang masih merujuk kode regulasi lama (SEOJK) yang seharusnya sudah bermigrasi ke PADK.
Mendeteksi ketidaksesuaian angka/ketentuan operasional (misal bunga masih di atas 0,1%/hari) terhadap regulasi terbaru.
Memberi rekomendasi revisi dengan level risiko (rendah/sedang/tinggi).
Mencatat hasil temuan ke sistem tracking eksternal dan mengeskalasi temuan berisiko tinggi secara otomatis.
3. Arsitektur Sistem (Multi-Agent + Tool-Calling)
[Dokumen SOP Internal (PDF)]        [Knowledge Base Regulasi (curated)]
          │                                      │
          ▼                                      ▼
   Document Loader                        Document Loader
          │                                      │
          ▼                                      ▼
   Text Splitter                          Text Splitter
          │                                      │
          ▼                                      ▼
  Embedding Model  ──────────────►  Vector Store (Astra DB)
                                              │
[Chat Input: "cek SOP bagian bunga pinjaman"] │
          │                                    │
          ▼                                    ▼
   ┌─────────────────────────────────────────────┐
   │   AGENT 1 — Regulation Reference Checker      │
   │   Tugas: cari apakah teks SOP merujuk kode    │
   │   SEOJK lama, map ke kode PADK yang sesuai    │
   └───────────────────┬───────────────────────────┘
                        ▼
   ┌─────────────────────────────────────────────┐
   │   AGENT 2 — Substantive Gap Analyzer          │
   │   Tugas: bandingkan angka/ketentuan di SOP    │
   │   (bunga, lock cap, dsb) vs batas regulasi    │
   │   terbaru → flag jika melanggar                │
   └───────────────────┬───────────────────────────┘
                        ▼
   ┌─────────────────────────────────────────────┐
   │   AGENT 3 — Risk & Recommendation Drafter     │
   │   Tugas: gabungkan temuan Agent 1 & 2, beri   │
   │   level risiko + draf rekomendasi revisi       │
   └───────────────────┬───────────────────────────┘
                        ▼
              Structured Output (JSON)
                        ▼
        ┌───────────────┴────────────────┐
        ▼                                ▼
  Tool-Call: Google Sheets       Tool-Call: Email/Slack API
  (tulis baris: klausul,         (kirim notifikasi otomatis
   status, risiko, rekomendasi)   jika risiko = TINGGI)
        │
        ▼
   Chat Output (ringkasan ke user)
4. Detail Komponen Langflow
Komponen	Fungsi
Document Loader (PDF) x2	Load SOP internal & knowledge base regulasi
Text Splitter x2	Pecah dokumen jadi chunk kecil untuk embedding
Embedding Model (Google Generative AI Embedding)	Ubah teks jadi vektor
Astra DB (Vector Store) x2 collection	Simpan embedding SOP & embedding regulasi terpisah
Chat Input	Terima pertanyaan/perintah user (misal: "audit bagian bunga pinjaman")
Retriever x2	Ambil chunk relevan dari masing-masing vector store
Prompt Template — Agent 1	Instruksi untuk deteksi rujukan kode lama
Prompt Template — Agent 2	Instruksi untuk bandingkan angka/ketentuan
Prompt Template — Agent 3	Instruksi untuk sintesis risiko & rekomendasi
Language Model x3 (chained)	Eksekusi tiap agent
Structured Output	Paksa Agent 3 keluarkan JSON terstruktur (klausul, status, risiko, rekomendasi)
Tool/Custom Component — Google Sheets API	Tulis hasil ke spreadsheet tracker
Tool/Custom Component — Webhook/Email API	Kirim notifikasi kalau risiko tinggi
Chat Output	Tampilkan ringkasan hasil audit ke user
5. Prompt Layering (3-Layer, per Agent)

Agent 1 — Regulation Reference Checker

Role & Context: "Kamu adalah asisten compliance yang ahli memetakan referensi regulasi OJK lama (SEOJK) ke format baru (PADK)."
Task: "Dari potongan SOP berikut, identifikasi setiap rujukan ke kode SEOJK. Untuk tiap temuan, sebutkan kode lama, dan apakah ada padanan PADK berdasarkan knowledge base yang diberikan."
Constraint & Output: "Jika tidak ditemukan rujukan, kembalikan 'tidak ada temuan'. Output dalam format list: {kode_lama, kode_baru, lokasi_klausul}."

Agent 2 — Substantive Gap Analyzer

Role & Context: "Kamu adalah auditor kepatuhan bunga pinjaman fintech."
Task: "Bandingkan angka bunga/ketentuan operasional di SOP dengan batas regulasi terbaru (0,1%/hari, Lock Cap 100%). Tandai jika SOP masih mencantumkan angka lama atau tidak sesuai."
Constraint & Output: "Jangan berasumsi jika data tidak eksplisit disebut di SOP — tandai sebagai 'perlu verifikasi manual', bukan langsung 'melanggar'."

Agent 3 — Risk & Recommendation Drafter

Role & Context: "Kamu adalah manajer risiko compliance yang menyusun rekomendasi actionable."
Task: "Gabungkan temuan Agent 1 dan Agent 2. Untuk tiap temuan, tentukan level risiko (Rendah/Sedang/Tinggi) dan tulis draf rekomendasi revisi singkat."
Constraint & Output: "Output HARUS JSON valid dengan field: klausul, jenis_masalah, level_risiko, rekomendasi. Tidak boleh ada teks di luar JSON."
6. Peran opencode + MCP Langflow

Karena flow ini punya 3 agent berantai + 2 tool-call eksternal, membangunnya manual lewat drag-drop GUI rawan salah wiring. Dengan opencode:

Generate & edit .json flow Langflow secara terprogram (komponen, koneksi antar-node, konfigurasi prompt) lebih presisi dan cepat.
Jalankan automated testing: siapkan 5-10 skenario SOP dummy (ada yang jelas melanggar, ada yang ambigu, ada yang aman) → jalankan lewat script → cek apakah tiap agent menghasilkan output yang benar.
Iterasi terarah: kalau Agent 2 sering salah flag, revisi prompt Agent 2 saja tanpa ubah Agent 1 & 3 (pola targeted refinement).
Dokumentasikan versi prompt awal vs final + alasan revisi — ini nilai plus besar di kriteria dokumentasi.
7. Data yang Perlu Disiapkan (untuk demo)
1 dokumen SOP internal dummy (bisa buat sendiri: "SOP Kebijakan Bunga Pinjaman PT Fintech X", isi beberapa klausul, beberapa sengaja dibuat melanggar/usang untuk demo).
1 dokumen knowledge base regulasi (ringkasan poin kunci: PADK vs SEOJK mapping, batas bunga 0,1%/hari, Lock Cap 100%, kewajiban escrow, kewajiban DPO) — bisa disusun manual dari sumber resmi OJK.
8. Kesesuaian dengan Rubrik Penilaian
Kriteria	Bagaimana project ini memenuhi
Completeness & Feasibility	Alur end-to-end: input SOP → 3 agent berantai → output JSON → tulis ke Sheets → notifikasi. Semua komponen bisa didemo hidup.
Creativity & Innovation	Bukan RAG-QA biasa; deteksi gap regulasi 2-arah (format + substansi) dengan isu yang sangat spesifik & baru (migrasi SEOJK→PADK 2026) — belum ada precedent yang menyasar ini.
System Design & Architecture	3 agent dengan peran terpisah jelas, modular, tool-calling ke sistem eksternal — bukan 1 prompt monolitik.
Background & Impact	Masalah nyata dengan angka & regulasi konkret (POJK 40/2024, batas bunga 0,1%/hari, PMK 8/2026), target user jelas (tim compliance fintech), dampak terukur (waktu audit manual vs otomatis).
9. Responsible AI & Batasan
Agent 2 dirancang untuk tidak langsung memvonis "melanggar" — hanya menandai untuk verifikasi manusia (human-in-the-loop), karena keputusan compliance final harus tetap oleh manusia.
Disclaimer eksplisit di output: "Hasil ini adalah bantuan awal, bukan opini hukum resmi."
Guardrail: kalau LLM tidak yakin/informasi SOP ambigu, agent wajib jawab "perlu verifikasi manual" — bukan mengarang jawaban (kontrol hallucination).
10. Ide Pengembangan Lanjutan (untuk form "rencana ke depan")

"AI Compliance Monitor — Perluasan ke Multi-Regulator": mengembangkan sistem agar bisa memonitor regulasi dari BI (PBI, PADG) dan Komdigi (UU PDP) sekaligus OJK, dengan agent tambahan yang otomatis update knowledge base begitu ada regulasi baru terbit.
