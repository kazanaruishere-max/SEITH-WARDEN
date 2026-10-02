# 03 — Input Validation & Length Capping

**Goal:** Mencegah eksploitasi Denial-of-Service (DoS) dan payload flooding raksasa pada LLM dengan menerapkan batasan panjang teks masukan (*input length cap*) maksimal 4.000 karakter pada node pertama pipeline (`CustomComponent-pii`).

**Owner:** T1 | **Skill:** `security-reviewer` + `refactor-cleaner` | **Zone:** `flows/seith_warden_flow.json` (`CustomComponent-pii`)

## 1. Input -> Output Real

```text
// Input Uji: Teks klausul sepanjang 5.008 karakter
"Pasal 1 " + "A" * 5000

// Output Sanitizer
"Pasal 1 AAAA... [TRUNCATED_AT_4000_CHARS_SECURITY_BOUNDARY]" (Panjang: 4.048 karakter)
```

## 2. Implementasi Teknis
* Konstanta `MAX_CHARS = 4000` di dalam metode `sanitize()` pada `PIISanitizerComponent`.
* Jika `len(text) > MAX_CHARS`, teks otomatis dipotong dan disematkan penanda `... [TRUNCATED_AT_4000_CHARS_SECURITY_BOUNDARY]`.
* Pemotongan dilakukan **sebelum** regex NIK, nomor rekening, dan email diproses agar komputasi regex tidak mengalami catastrophic backtracking akibat payload tak terbatas.

## 3. Verifikasi Nyata
* `& "C:\Users\Lenovo\AppData\Local\com.LangflowDesktop\.langflow-venv\Scripts\python.exe" scripts/test_final_security_phase.py` -> `PII truncation test passed! Output length: 4048`.

## 4. Accountability
* ✅ Terverifikasi: String 5.008 karakter terpotong aman pada batas 4.000 karakter dengan penanda boundary.
* ⚠️ Catatan Operasional: Batas 4.000 karakter cukup untuk 1–3 halaman klausul audit satuan di Playground; dokumen 400 halaman penuh tetap diproses via chunking terpisah di pipeline vector store.
* 🔻 Risiko: Klausul legal yang secara alami melebihi 4.000 karakter dalam 1 paragraf akan terpotong bagian akhirnya.
* ♻️ Refactor: Penambahan capping hanya 5 baris kode tanpa dependensi pihak ketiga.
