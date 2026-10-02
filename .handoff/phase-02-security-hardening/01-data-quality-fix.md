# 01 — Data Quality Fix (Found_Value & Clause Deduplication)

**Goal:** Menghilangkan bug duplikasi nama klausul (`Pasal Pasal 1` -> `Pasal 1`) dan mengekstrak nilai persentase temuan riil (`Found_Value = 0.25%/hari`, bukan `-`) agar audit trail di Google Sheets akurat dan siap dipresentasikan.

**Owner:** T1 | **Skill:** `tdd-guide` + `seith-warden-compliance` | **Zone:** `flows/seith_warden_flow.json` (`CustomComponent-sheets_webhook`)

## 1. Input -> Output Real

```json
// Input dari Agent-RiskSynthesizer
{
  "clause_id": "Pasal 1",
  "evidence": ["Pengenaan bunga sebesar 0,25% per hari melampaui batas maksimum 0,1% per hari"],
  "risk_level": "HIGH",
  "category": "RATE_CAP_BREACH"
}

// Payload yang dikirim ke Google Sheets (9 Kolom)
{
  "timestamp": "2026-09-30 13:49:27 UTC",
  "document": "SOP-Internal-Fintech",
  "clause": "Pasal 1",             // SEBELUMNYA: "Pasal Pasal 1" -> SEKARANG: deduplikasi aman
  "category": "RATE_CAP_BREACH",
  "found_value": "0.25%/hari",      // SEBELUMNYA: "-" -> SEKARANG: regex extract dari evidence
  "limit": "0.10%/hari (PADK 12:1)",
  "risk_level": "HIGH",
  "recommendation": "Ganti klausul menjadi: 'Manfaat ekonomi/bunga harian ditetapkan maksimal 0,1%...'",
  "reviewer": "Pending Compliance Officer Review"
}
```

## 2. Implementasi Teknis
* Regex ekstraksi nilai temuan di `CustomComponent-sheets_webhook`:
  `re.search(r"(\d+(?:[.,]\d+)?\s*%)", all_content)`
* Normalisasi spasi dan koma ke titik, serta menambahkan akhiran `/hari` bila teks klausul bertipe pinjaman harian.
* Sanitasi prefix `clause_id`: cek `raw_clause.lower().startswith("pasal")` sebelum menambahkan prefix `Pasal`.

## 3. Verifikasi Nyata
* `& "C:\Users\Lenovo\AppData\Local\com.LangflowDesktop\.langflow-venv\Scripts\python.exe" scripts/test_dq_fix.py` -> `Extracted found_value: 0.25%/hari`
* Sheet Baris Live -> Tercatat `Pasal 1` dan `0.25%/hari`

## 4. Accountability
* ✅ Terverifikasi: Output `found_value: 0.25%/hari` dan `clause: Pasal 1` terbukti via tes komponen runtime Langflow.
* ⚠️ Belum terverifikasi: Klausul tanpa persentase tetap menghasilkan `found_value: -` (perilaku yang diharapkan).
* 🔻 Risiko: Jika evidence memuat lebih dari 1 angka persentase, regex mengambil persentase pertama yang cocok.
* ♻️ Refactor: Logika ekstraksi dipusatkan di metode `dispatch()` tanpa menambah node baru di kanvas.
