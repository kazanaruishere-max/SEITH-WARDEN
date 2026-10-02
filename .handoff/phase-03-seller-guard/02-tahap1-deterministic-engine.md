# Phase 03 — Task 02: Tahap 1 — Engine Deterministik Finansial & Hashing SHA-256

**Goal:** Mengimplementasikan mesin kalkulasi kepatuhan deterministik `tools/seller_guard_engine.py` berbasis Python `Decimal` (bebas *float drift*), dilengkapi kalkulasi integritas SHA-256, normalisasi input tahan kesalahan, dan pengujian unit `tests/test_seller_guard.py` yang lulus 100% pada 7 kasus oracle awal.

---

## 1. Struktur Komponen Engine (`tools/seller_guard_engine.py`)

Engine dirancang modular mengikuti konvensi batas ukuran kode (`fn < 50 baris`, `file 200-400 baris`, `nesting <= 4`):

```
tools/seller_guard_engine.py
├── calculate_sha256(raw_bytes: bytes) -> str
├── parse_decimal(value: Any) -> Decimal
├── class ReportNormalizer
│   ├── normalize_headers(headers: List[str]) -> Dict[str, str]
│   ├── validate_row(row: Dict[str, Any], row_idx: int) -> Tuple[Optional[NormalizedTx], Optional[Finding]]
│   └── process_csv(csv_content: str) -> Tuple[List[NormalizedTx], List[Finding], str]
├── class ThresholdGuard
│   ├── calculate_cumulative_gross(txs: List[NormalizedTx], initial_gross: Decimal) -> Decimal
│   ├── evaluate_threshold_status(cumulative: Decimal, threshold: Decimal) -> Dict[str, Any]
│   └── project_crossing_date(txs: List[NormalizedTx], cumulative: Decimal, threshold: Decimal) -> Dict[str, Any]
├── class WithholdingAuditor
│   ├── audit_transaction(tx: NormalizedTx, profile: SellerProfile, config: PMKConfig) -> Tuple[Decimal, List[Finding]]
│   └── evaluate_batch(txs: List[NormalizedTx], profile: SellerProfile, config: PMKConfig) -> List[Finding]
└── class FindingsAggregator
    └── build_payload(txs: List[NormalizedTx], findings: List[Finding], profile: SellerProfile, input_hash: str) -> Dict[str, Any]
```

---

## 2. Spesifikasi Teknis & Logika Deterministik

### A. Integritas SHA-256 & Pembatasan Ukuran
1. **Fungsi Hashing:**
   ```python
   import hashlib

   def calculate_sha256(raw_bytes: bytes) -> str:
       """Menghasilkan representasi hex SHA-256 dari konten mentah file."""
       return hashlib.sha256(raw_bytes).hexdigest()
   ```
2. **Boundary Cap (Anti-DoS):**
   - Panjang teks bebas maksimal 4.000 karakter.
   - Maksimal 5.000 baris transaksi CSV. Jika baris ke-5.001 terdeteksi, pemrosesan dihentikan dan dicatat temuan:
     `{"type": "DATA_QUALITY", "detail": "[TRUNCATED_AT_5000_ROWS_SECURITY_BOUNDARY]"}`.

### B. Normalisasi & Sanitasi Nilai Uang (`Decimal`)
- Dilarang keras menggunakan tipe data `float` untuk seluruh representasi uang dan persentase:
  ```python
  from decimal import Decimal, ROUND_HALF_UP

  IDR_ROUND = Decimal("1")
  PCT_ROUND = Decimal("0.01")
  RATE_CAP = Decimal("0.005")  # 0,5%
  ```
- Kolom wajib CSV:
  - `order_id` (string non-kosong)
  - `marketplace` (string: "Marketplace A", "Marketplace B", "Marketplace C")
  - `order_date` (ISO `YYYY-MM-DD`)
  - `payment_received_date` (ISO `YYYY-MM-DD`)
  - `gross_invoice_value` (angka positif)
  - `pph22_withheld` (angka non-negatif)
  - `pph22_refunded` (angka non-negatif)
  - `status` (`COMPLETED`, `RETURNED`, `CANCELLED`)
- Baris dengan nilai yang tidak dapat di-parse atau kolom wajib yang hilang tidak dibuang secara diam-diam (*no silent dropping*), melainkan dikompilasi menjadi temuan bertipe `DATA_QUALITY`.

### C. Logika Threshold Guard (Ambang Rp500 Juta)
- **Kumulatif Omzet:**
  $$Kumulatif(t) = \sum_{i=1}^t Gross_{COMPLETED} + OtherChannelGross$$
- **Klasifikasi Rasio Ambang ($R = Kumulatif / 500.000.000$):**
  - $R < 80,0\% \rightarrow$ `AMAN`
  - $80,0\% \le R < 100,0\% \rightarrow$ `MENDEKATI` (memicu temuan `THRESHOLD_NEAR`)
  - $R \ge 100,0\% \rightarrow$ `TERLAMPAUI` (memicu temuan `THRESHOLD_CROSSED_NOTIFY_REQUIRED`)
- **Proyeksi Tanggal Terlampaui:**
  - Menghitung rata-rata omzet harian 60 hari terakhir transaksi `COMPLETED`.
  - Jika riwayat data kurang dari 30 hari kalender: Proyeksi mengembalikan nilai `null` dan mencatat alasan `"PERLU_VERIFIKASI_MANUAL: Riwayat data transaksi < 30 hari"`.
  - Jika ambang terlampaui di bulan $M$: Batas pemberitahuan (`notify_deadline`) ditetapkan otomatis pada hari kalender terakhir bulan $M$ (`YYYY-MM-last_day`).

### D. Logika Withholding Auditor (Evaluasi PPh 22 0,5%)
Untuk setiap transaksi $tx$:
1. Jika $status \neq \text{"COMPLETED"}$:
   $\rightarrow$ Terbitkan temuan `PERLU_VERIFIKASI_MANUAL` (klausul retur/batal).
2. Jika $payment\_date < effective\_date$:
   $\rightarrow Expected = 0$.
3. Jika $payment\_date \in suspension\_window$ dan $withheld > 0$:
   $\rightarrow Expected = 0$. Jika $refunded < withheld$, terbitkan temuan `REFUND_PENDING` dengan $\Delta = withheld - refunded$.
4. Jika WP adalah `BADAN`:
   - Jika $skb\_valid == True \rightarrow Expected = 0$.
   - Selain itu $\rightarrow Expected = (gross \times 0,005).quantize(IDR\_ROUND, ROUND\_HALF\_UP)$.
5. Jika WP adalah `OP` (Orang Pribadi):
   - Jika $skb\_valid == True \rightarrow Expected = 0$.
   - Jika $statement\_status == \text{"UNDER\_500"}$:
     - Jika $statement\_date \le payment\_date$:
       - Jika transaksi terjadi di bulan $\le M$ (bulan saat batas terlampaui) $\rightarrow Expected = 0$.
       - Jika transaksi terjadi di bulan $> M$ (bulan berikutnya setelah batas terlampaui) $\rightarrow Expected = (gross \times 0,005)$.
     - Jika $statement\_date > payment\_date \rightarrow Expected = (gross \times 0,005)$.
   - Jika $statement\_status == \text{"NONE"}$:
     - $Expected = (gross \times 0,005)$ dan terbitkan temuan `STATEMENT_MISSING`.
6. Evaluasi Selisih:
   - $\Delta = withheld - Expected$.
   - Toleransi selisih: $|\Delta| \le 1$ Rupiah dianggap variasi pembulatan matematis (`COMPLIANT`).
   - Jika $\Delta > 1 \rightarrow$ Terbitkan temuan `OVER_WITHHELD` (potensi klaim pengembalian).
   - Jika $\Delta < -1 \rightarrow$ Terbitkan temuan `UNDER_WITHHELD` (kekurangan pungut).

---

## 3. Struktur Pengujian Unit (`tests/test_seller_guard.py`)

Pengujian unit menggunakan `pytest` dengan eksekusi mandiri tanpa ketergantungan jaringan:
- `test_sha256_hashing()`: Verifikasi determinisme hash SHA-256 terhadap string dan file bytes.
- `test_normalizer_truncation()`: Verifikasi pemotongan batas 5.000 baris dan penandaan `DATA_QUALITY`.
- `test_decimal_rounding()`: Verifikasi presisi pembulatan Rupiah dan eliminasi float drift.
- `test_oracle_cases_t01_to_t07()`: Pengujian 7 kasus oracle (T01 s.d. T07) yang dicocokkan langsung terhadap `tests/expected_seller_guard.json`.
- `test_next_month_withholding_boundary()`: Verifikasi ketat aturan "pemungutan baru berlaku bulan berikutnya" setelah ambang terlewati.

---

## 4. Gate Verifikasi Tahap 1
1. Perintah: `uv run pytest tests/test_seller_guard.py -v`
2. Kriteria Lulus:
   - 100% tests PASS (0 failure, 0 error).
   - Selisih antara perhitungan engine vs `tests/expected_seller_guard.json` = Rp0.
   - `uv run ruff check tools/seller_guard_engine.py` bersih tanpa peringatan.
