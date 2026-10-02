# 04 — Google Sheets Endpoint Hardening & Token Authentication

**Goal:** Mengamankan endpoint Google Apps Script Web App dengan shared token autentikasi `SEITH_WARDEN_2026`, validasi 9 kolom data, serta pelaporan status HTTP riil (bukan status palsu/hardcoded) dengan penanganan redirect 302 dan error 401/403 yang transparan.

**Owner:** T2 | **Skill:** `security-reviewer` + `docs-lookup` | **Zone:** `flows/seith_warden_flow.json` + `docs/setup.md §9`

## 1. Input -> Output Real

```json
// Panggilan HTTP POST ke Google Apps Script:
POST https://script.google.com/macros/s/.../exec?token=SEITH_WARDEN_2026
Content-Type: application/json

{
  "timestamp": "2026-09-30 13:49:54 UTC",
  "document": "SOP-Internal-Fintech",
  "clause": "Pasal 1",
  "category": "RATE_CAP_BREACH",
  "found_value": "0.25%/hari",
  "limit": "0.10%/hari (PADK 12:1)",
  "risk_level": "HIGH",
  "recommendation": "Ganti klausul menjadi: 'Manfaat ekonomi/bunga harian ditetapkan maksimal 0,1%...'",
  "reviewer": "Pending Compliance Officer Review"
}

// Respons dari Apps Script (Follow 302 Redirect):
HTTP 200 OK
{"status": "ok", "row": 3}
```

## 2. Implementasi Teknis
* Token `SEITH_WARDEN_2026` diseragamkan di:
  1. Apps Script validator: `if (e.parameter.token !== "SEITH_WARDEN_2026") return 403 Forbidden`.
  2. Dispatcher component: auto-append `?token=SEITH_WARDEN_2026` jika parameter belum ada pada URL.
  3. Dokumentasi `docs/setup.md §9`.
* Penanganan status kode eksplisit:
  * `200/201/302`: `[LIVE - HTTP 200 OK] Baris audit trail berhasil dicatat ke Google Sheets (Tercatat pada Baris #X)`.
  * `401`: `[FAILED - HTTP 401 Unauthorized] Redeploy Web App: Anyone (bukan 'Anyone with Google account')`.
  * `403`: `[FAILED - HTTP 403 Forbidden] Token tidak cocok (Pastikan token=SEITH_WARDEN_2026)`.
  * URL Kosong: `[SKIPPED] Endpoint URL belum disetel (Menunggu konfigurasi Google Sheets URL)`.

## 3. Verifikasi Nyata
* Pengujian langsung di Google Sheets live menghasilkan baris riil di spreadsheet dengan status HTTP 200.

## 4. Accountability
* ✅ Terverifikasi: Live call ke Google Sheets terbukti menulis 9 kolom data riil.
* ⚠️ Batasan Jujur: Penggunaan shared token via query param adalah kompromi pragmatis untuk kemudahan demo hackathon; bukan pengganti OAuth2 mutual TLS untuk skala produksi enterprise.
* 🔻 Risiko: Jika Apps Script di-deploy dengan akses terbatas (*Anyone with Google account*), request tanpa cookie sesi akan memicu 401.
* ♻️ Refactor: Menggunakan library `requests` bawaan Langflow Desktop dengan opsi `allow_redirects=True`.
