# Phase 03 — Task 01: Tahap 0 — Verifikasi Regulasi, Skema Konfigurasi & Oracle Hitungan Tangan

**Goal:** Menetapkan dasar hukum kepatuhan PMK 37/2025 yang terverifikasi, mengunci skema konfigurasi tanpa nilai asumsi liar, dan menyusun oracle data uji awal dari 7 kasus hitungan tangan yang diverifikasi manual sebelum sebaris kode pun ditulis.

---

## 1. Protokol Verifikasi Sumber Primer (`docs/sources/`)

1. **Persyaratan Dokumen Sumber:**
   - User meletakkan teks salinan resmi di folder `docs/sources/`:
     - `docs/sources/pmk_37_2025.txt`: Salinan lengkap PMK Nomor 37 Tahun 2025.
     - `docs/sources/peng_46_2026.txt`: Salinan Pengumuman DJP PENG-46/PJ.09/2026 (atau regulasi penundaan terkait).
2. **Aturan Ekstraksi & Anti-Fabrikasi:**
   - **Nomor Pasal:** Hanya boleh dicantumkan jika nomor pasal dan ayat tersebut terbaca secara literal pada teks di `docs/sources/`. Jika hanya berasal dari artikel berita atau sumber sekunder, nomor pasal diisi `"BELUM_DIVERIFIKASI"`.
   - **Tingkat Keyakinan (Confidence):**
     - `PRIMARY`: Diverifikasi langsung ke salinan regulasi di `docs/sources/`.
     - `SECONDARY`: Berdasarkan siaran pers resmi DJP atau artikel edukasi pegawai DJP (pajak.go.id).
     - `UNVERIFIED`: Berdasarkan artikel media pihak ketiga atau forum komunitas.
3. **Penanganan Jika PENG-46 Belum Ada:**
   - `data/kb/pmk37_config.json` **WAJIB** memasang `suspension_window: null`, `effective_date: null`, dan `status: "UNVERIFIED"`.
   - Dilarang keras mengarang tanggal efektif atau rentang waktu suspensi pada konfigurasi utama.
   - Skenario suspensi hanya boleh diuji menggunakan file fixture test khusus: `tests/fixtures/config_test.json`.

---

## 2. Skema Kontrak Konfigurasi & Aturan

### A. `data/kb/pmk37_config.json` (Produksi — Strict Default)
```json
{
  "status": "UNVERIFIED",
  "effective_date": null,
  "suspension_window": null,
  "threshold_idr": "500000000",
  "rate_cap_percent": "0.5",
  "verified_at": null,
  "source": "BELUM_DIVERIFIKASI",
  "notes": "Menunggu verifikasi salinan resmi PMK 37/2025 dan PENG-46/PJ.09/2026 di docs/sources/"
}
```

### B. `tests/fixtures/config_test.json` (Fixture Pengujian — ASSUMPTION_FOR_TEST)
```json
{
  "label": "ASSUMPTION_FOR_TEST",
  "scenario_a": {
    "description": "Skenario A: Berlaku efektif 1 November 2026 tanpa periode suspensi (mengacu pernyataan Dirjen Pajak di Periskop 18 Sep 2026)",
    "status": "ASSUMED",
    "effective_date": "2026-11-01",
    "suspension_window": null,
    "threshold_idr": "500000000",
    "rate_cap_percent": "0.5"
  },
  "scenario_b": {
    "description": "Skenario B: Simulasi suspensi awal Agustus (2026-08-01 s.d. 2026-08-05) untuk pengujian hak pengembalian dana (REFUND_PENDING)",
    "status": "ASSUMED",
    "effective_date": "2026-08-01",
    "suspension_window": ["2026-08-01", "2026-08-05"],
    "threshold_idr": "500000000",
    "rate_cap_percent": "0.5"
  }
}
```

### C. `data/kb/pmk37_rules.json` (Struktur Aturan)
```json
[
  {
    "rule_id": "R-RATE-CAP",
    "description": "Pemungutan PPh Pasal 22 oleh marketplace sebesar 0,5% dari peredaran bruto (invoice) tidak termasuk PPN/PPnBM",
    "source_title": "Siaran Pers DJP SP-14/2026",
    "source_url": "https://www.pajak.go.id/en/node/120146",
    "pasal": "BELUM_DIVERIFIKASI",
    "verified_at": "2026-10-01",
    "confidence": "SECONDARY"
  },
  {
    "rule_id": "R-EXEMPT-OP-500M",
    "description": "Wajib Pajak orang pribadi dengan omzet sampai dengan Rp500 juta dalam satu tahun pajak tidak dipungut PPh 22 jika menyampaikan surat pernyataan",
    "source_title": "Siaran Pers DJP SP-14/2026",
    "source_url": "https://www.pajak.go.id/en/node/120146",
    "pasal": "BELUM_DIVERIFIKASI",
    "verified_at": "2026-10-01",
    "confidence": "SECONDARY"
  },
  {
    "rule_id": "R-THRESHOLD-NEXT-MONTH",
    "description": "Jika omzet melewati Rp500 juta pada bulan M, seller memberitahukan paling lambat akhir bulan M; pemungutan berlaku mulai bulan M+1",
    "source_title": "Artikel Edukasi DJP (Eka Ardi Handoko)",
    "source_url": "https://www.pajak.go.id/en/node/120342",
    "pasal": "BELUM_DIVERIFIKASI",
    "verified_at": "2026-10-01",
    "confidence": "SECONDARY"
  },
  {
    "rule_id": "R-BADAN-NO-THRESHOLD",
    "description": "Wajib Pajak Badan dipungut 0,5% tanpa fasilitas ambang batas Rp500 juta kecuali memiliki SKB valid",
    "source_title": "Siaran Pers DJP SP-14/2026",
    "source_url": "https://www.pajak.go.id/en/node/120146",
    "pasal": "BELUM_DIVERIFIKASI",
    "verified_at": "2026-10-01",
    "confidence": "SECONDARY"
  },
  {
    "rule_id": "R-SUSPENSION-REFUND",
    "description": "Pemungutan pada masa suspensi wajib dikembalikan kepada seller",
    "source_title": "Laporan Periskop.id / Pengumuman DJP",
    "source_url": "https://periskop.id/perdagangan/20260918/pph-marketplace-05-berlaku-1-november-seller-omzet-hingga-rp500-juta-dikecualikan",
    "pasal": "BELUM_DIVERIFIKASI",
    "verified_at": "2026-10-01",
    "confidence": "UNVERIFIED"
  }
]
```

---

## 3. Tujuh Kasus Hitungan Tangan Oracle (`tests/expected_seller_guard.json`)

Semua kalkulasi dilakukan dengan presisi manual `Decimal` rupiah:

### Kasus T01: OP Bebas PPh 22 tapi Dipungut (`OVER_WITHHELD`)
- **Konfigurasi Uji:** Skenario A (efektif 2026-11-01)
- **Profil WP:** OP, `statement_status: UNDER_500`, `statement_date: 2026-10-01`, `other_channel_ytd_gross: 50.000.000`
- **Data Transaksi:** `ORD-001` | Marketplace A | bayar: `2026-11-05` | gross: `10.000.000` | withheld: `50.000` | status: `COMPLETED`
- **Langkah Hitung:**
  1. Total omzet = $50.000.000 + 10.000.000 = 60.000.000 \le 500.000.000$ (Status: AMAN, 12,0%).
  2. Surat berlaku (`2026-10-01` $\le$ `2026-11-05`) $\rightarrow$ `expected_withholding = 0`.
  3. $\Delta = 50.000 - 0 = +50.000$.
- **Expected Finding:**
  `{"finding_id": "F-T01", "type": "OVER_WITHHELD", "order_ids": ["ORD-001"], "observed_idr": "50000", "expected_idr": "0", "delta_idr": "50000", "confidence": "SECONDARY"}`

### Kasus T02: OP Tanpa Surat Pernyataan (`STATEMENT_MISSING`)
- **Konfigurasi Uji:** Skenario A (efektif 2026-11-01)
- **Profil WP:** OP, `statement_status: NONE`, `other_channel_ytd_gross: 0`
- **Data Transaksi:** `ORD-002` | Marketplace B | bayar: `2026-11-10` | gross: `2.000.000` | withheld: `10.000` | status: `COMPLETED`
- **Langkah Hitung:**
  1. Tidak ada surat pernyataan $\rightarrow$ fasilitas bebas tidak berlaku. Pungutan 0,5% secara matematis sah.
  2. `expected_withholding = 0,005 x 2.000.000 = 10.000`.
  3. $\Delta = 10.000 - 10.000 = 0$.
- **Expected Finding:**
  `{"finding_id": "F-T02", "type": "STATEMENT_MISSING", "order_ids": ["ORD-002"], "observed_idr": "10000", "expected_idr": "10000", "delta_idr": "0", "confidence": "SECONDARY"}`

### Kasus T03: Ambang Terlampaui di Tengah Bulan (`THRESHOLD_CROSSED_NOTIFY_REQUIRED`)
- **Konfigurasi Uji:** Skenario A (efektif 2026-11-01)
- **Profil WP:** OP, `statement_status: UNDER_500`, `statement_date: 2026-10-01`, `other_channel_ytd_gross: 495.000.000`
- **Data Transaksi:** `ORD-003` | Marketplace A | bayar: `2026-11-15` | gross: `10.000.000` | withheld: `0` | status: `COMPLETED`
- **Langkah Hitung:**
  1. Total omzet = $495.000.000 + 10.000.000 = 505.000.000 > 500.000.000$ (Status: TERLAMPAUI, 101,0%).
  2. Batas terlewati pada bulan November. Sesuai aturan, pemungutan baru berlaku bulan berikutnya (1 Desember).
  3. Transaksi November tetap `expected_withholding = 0`, $\Delta = 0$.
  4. Batas notifikasi = hari terakhir bulan saat ambang terlampaui (`2026-11-30`).
- **Expected Finding:**
  `{"finding_id": "F-T03", "type": "THRESHOLD_CROSSED_NOTIFY_REQUIRED", "order_ids": ["ORD-003"], "observed_idr": "0", "expected_idr": "0", "delta_idr": "0", "notify_deadline": "2026-11-30", "confidence": "SECONDARY"}`

### Kasus T04: Pungutan Masa Suspensi Belum Dikembalikan (`REFUND_PENDING`)
- **Konfigurasi Uji:** Skenario B (suspensi `2026-08-01` s.d. `2026-08-05`)
- **Profil WP:** OP, `statement_status: UNDER_500`, `statement_date: 2026-07-25`, `other_channel_ytd_gross: 20.000.000`
- **Data Transaksi:** `ORD-004` | Marketplace C | bayar: `2026-08-03` | gross: `4.000.000` | withheld: `20.000` | refunded: `0` | status: `COMPLETED`
- **Langkah Hitung:**
  1. Tanggal bayar `2026-08-03` berada dalam rentang suspensi $\rightarrow$ `expected_withholding = 0`.
  2. Pungutan terpotong `20.000`, refund tercatat `0`.
  3. $\Delta = 20.000 - 0 = +20.000$ (dana tertahan yang wajib dikembalikan).
- **Expected Finding:**
  `{"finding_id": "F-T04", "type": "REFUND_PENDING", "order_ids": ["ORD-004"], "observed_idr": "20000", "expected_idr": "0", "delta_idr": "20000", "confidence": "UNVERIFIED"}`

### Kasus T05: WP Badan Pungutan 0,5% Sesuai Aturan (`COMPLIANT`)
- **Konfigurasi Uji:** Skenario A (efektif 2026-11-01)
- **Profil WP:** BADAN, `skb_valid: false`, `other_channel_ytd_gross: 1.000.000.000`
- **Data Transaksi:** `ORD-005` | Marketplace B | bayar: `2026-11-20` | gross: `20.000.000` | withheld: `100.000` | status: `COMPLETED`
- **Langkah Hitung:**
  1. Badan usaha tanpa SKB $\rightarrow$ tarif 0,5% tanpa ambang bebas pajak.
  2. `expected_withholding = 0,005 x 20.000.000 = 100.000`.
  3. $\Delta = 100.000 - 100.000 = 0$.
- **Expected Finding:** (Tidak ada temuan anomali / transaksi berstatus `COMPLIANT`).

### Kasus T06: Transaksi Retur Barang (`PERLU_VERIFIKASI_MANUAL`)
- **Konfigurasi Uji:** Skenario A (efektif 2026-11-01)
- **Profil WP:** OP, `statement_status: UNDER_500`
- **Data Transaksi:** `ORD-006` | Marketplace A | bayar: `2026-11-22` | gross: `1.000.000` | withheld: `5.000` | status: `RETURNED`
- **Langkah Hitung:**
  1. Transaksi berstatus `RETURNED` membutuhkan dokumen pembatalan tagihan / bukti pemungutan tambahan di Coretax.
  2. Berada di luar batasan otomasi MVP.
- **Expected Finding:**
  `{"finding_id": "F-T06", "type": "PERLU_VERIFIKASI_MANUAL", "order_ids": ["ORD-006"], "reason": "Transaksi retur memerlukan verifikasi bukti potong pembetulan", "confidence": "SECONDARY"}`

### Kasus T07: Omzet Mendekati Ambang Batas 85% (`THRESHOLD_NEAR`)
- **Konfigurasi Uji:** Skenario A (efektif 2026-11-01)
- **Profil WP:** OP, `statement_status: UNDER_500`, `other_channel_ytd_gross: 400.000.000`
- **Data Transaksi:** `ORD-007` | Marketplace A | bayar: `2026-11-25` | gross: `25.000.000` | withheld: `0` | status: `COMPLETED`
- **Langkah Hitung:**
  1. Total omzet berjalan = $400.000.000 + 25.000.000 = 425.000.000$.
  2. Rasio ambang = $425.000.000 / 500.000.000 = 85,0\%$.
  3. Masuk rentang peringatan dini (80% s.d. <100%).
  4. Sisa batas omzet bebas pajak = $500.000.000 - 425.000.000 = 75.000.000$.
- **Expected Finding:**
  `{"finding_id": "F-T07", "type": "THRESHOLD_NEAR", "pct": "85.0", "cumulative_gross": "425000000", "remaining_idr": "75000000", "confidence": "SECONDARY"}`

---

## 4. Gate Verifikasi Tahap 0

Sebelum melangkah ke penulisan kode mesin pada Tahap 1, gerbang berikut wajib dipenuhi:
1. `data/kb/pmk37_config.json` terverifikasi memiliki field `effective_date: null` dan `status: "UNVERIFIED"`.
2. File `tests/fixtures/config_test.json` terdaftar dengan label eksplisit `ASSUMPTION_FOR_TEST`.
3. 7 kasus di atas disetujui sebagai kontrak acuan absolut untuk `tests/expected_seller_guard.json`.
4. User mengonfirmasi secara tertulis bahwa Gate Tahap 0 telah lulus.
