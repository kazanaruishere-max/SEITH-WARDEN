# Oracle Manual Hitungan Teks — Seller Guard Skenario 2026-11-01
**Config demo:** `tests/fixtures/config_demo.json` — ASSUMPTION_FOR_TEST
effective_date=2026-11-01, suspension_window=2026-08-01 s/d 2026-08-05, threshold=500.000.000, as_of=2026-10-01, status=ASSUMED (terpisah dari data/kb/pmk37_config.json UNVERIFIED)
**Profile:** OP, UNDER_500, statement_date=2026-09-15, skb_valid=false, other_channel_ytd=125.000.000, NIK HMAC(SellerRef)
**Urut:** payment_received_date ASC lalu order_id ASC — Decimal, expected=0 untuk semua COMPLETED sebelum 2026-11-01

## Komposisi Baseline (55 baris)
- 42 × 6.000.000 = 252.000.000 (ORD-001..042)
- 13 × 8.000.000 = 104.000.000 (ORD-043..055)
- Total baseline = 356.000.000

## Jalur Kumulatif (COMPLETED only)
125.000.000 (other) → 133.000.000 (074+075) → 489.000.000 (baseline 356) → 495.000.000 (071-073: 3×2.000.000) → 530.000.000 (056: 35.000.000, crossing) → 533.000.000 (080: 3.000.000) = 106,60% TERLAMPAUI, crossed_date=2026-10-01, notify_deadline=2026-10-31

| order_id | payment_received_date | gross | kumulatif sebelum | kumulatif sesudah | withheld | expected | delta | finding |
|---|---|---:|---:|---:|---:|---:|---:|---|
| ORD-2026-074 | 2026-08-02 | 4.000.000 | 125.000.000 | 129.000.000 | 20.000 | 0 | 20.000 | REFUND_PENDING (suspensi 08-01..05, belum refund) |
| ORD-2026-075 | 2026-08-03 | 4.000.000 | 129.000.000 | 133.000.000 | 20.000 | 0 | 20.000 | REFUND_PENDING |
| ORD-2026-001..042 (42 baris) | 2026-09-01 .. 2026-09-14 | 6.000.000 each | 133.000.000 → 379.000.000 | 139.000.000 → 385.000.000 | 0 | 0 | 0 | COMPLIANT |
| ORD-2026-043..055 (13 baris) | 2026-09-15 .. 2026-09-28 | 8.000.000 each | 385.000.000 → 481.000.000 | 393.000.000 → 489.000.000 | 0 | 0 | 0 | COMPLIANT |
| ORD-2026-071 | 2026-09-29 | 2.000.000 | 489.000.000 | 491.000.000 | 10.000 | 0 | 10.000 | OVER_WITHHELD (bebas, belum efektif 11-01) |
| ORD-2026-072 | 2026-09-29 | 2.000.000 | 491.000.000 | 493.000.000 | 10.000 | 0 | 10.000 | OVER_WITHHELD |
| ORD-2026-073 | 2026-09-29 | 2.000.000 | 493.000.000 | 495.000.000 | 10.000 | 0 | 10.000 | OVER_WITHHELD |
| ORD-2026-056 | 2026-10-01 | 35.000.000 | 495.000.000 | 530.000.000 | 0 | 0 | 0 | THRESHOLD_CROSSED_NOTIFY_REQUIRED (crossing, deadline 2026-10-31, plus DUMMY+UNVERIFIED banner) |
| ORD-2026-076 | 2026-10-01 | 1.500.000 | — | — | 7.500 | — | — | PERLU_VERIFIKASI_MANUAL (RETURNED, tidak masuk kumulatif & tidak masuk potential_claim) |
| ORD-2026-077 | 2026-10-01 | 2.500.000 | — | — | 0 | — | — | PERLU_VERIFIKASI_MANUAL (CANCELLED) |
| (kosong) ORD-2026-078 missing id | 2026-10-01 | 1.000.000 | — | — | 0 | — | — | DATA_QUALITY (DQ-MISSING-ID) |
| ORD-2026-079 | 2026-10-01 | GRATIS | — | — | 0 | — | — | DATA_QUALITY (DQ-PARSE-ERROR, gross non-numerik) |
| ORD-2026-080 | 2026-10-01 | 3.000.000 | 530.000.000 | 533.000.000 | 0 | 0 | 0 | COMPLIANT + injection “Abaikan instruksi” diabaikan + DUMMY |

## Ringkasan (as_of 2026-10-01, tidak ada tanggal >2026-10-01)
- Total baris file: 66 (62 COMPLETED, 2 MANUAL, 2 DQ)
- Gross COMPLETED: 408.000.000 (356.000.000 + 8.000.000 + 6.000.000 + 35.000.000 + 3.000.000)
- Kumulatif (COMPLETED + other): 533.000.000 (408.000.000 + 125.000.000)
- pct: 106,60% (533.000.000 / 500.000.000 × 100, dua desimal) → TERLAMPAUI
- Bar ASCII capped: [████████████████████] 106,60% → 20 blok penuh + " +6,60% OVERFLOW" (contoh: "[████████████████████ +6,60%] 106,60%")
- Observed COMPLETED: 70.000 (40.000 suspend + 30.000 over) — 7.500 di baris RETURNED tidak dihitung
- Expected COMPLETED: 0 (semua sebelum effective 2026-11-01)
- Potential_claim: 70.000 (delta OVER+REFUND)
- Temuan (10): DATA_QUALITY 2, THRESHOLD_CROSSED_NOTIFY_REQUIRED 1, OVER_WITHHELD 3, REFUND_PENDING 2, PERLU_VERIFIKASI_MANUAL 2
- Banner laporan tetap: [PERINGATAN UNVERIFIED] + [DUMMY DATASET] + [INPUT_SHA256]
