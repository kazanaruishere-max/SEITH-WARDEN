# Phase 03 — Task 04: Tahap 3 — Arsitektur Canvas Langflow & Verifikasi Graph

**Goal:** Membangun flow mandiri `flows/seith_warden_seller_guard.json` di Langflow tanpa menyentuh flow lama dan tanpa memodifikasi `database.db` secara langsung, memastikan seluruh vertex dan edge terkompilasi sukses (`Graph.from_payload`), serta menerapkan arsitektur model bahasa terpusat (*Centralized LM Component*).

---

## 1. Topologi Node & Arsitektur Canvas

Flow Seller Guard dirancang modular dengan 8 node utama yang saling terhubung:

```
[1. ChatInput / File Trigger]
              │
              ▼
[2. CustomComponent-normalizer_pii]
    - Hitung sha256(input)
    - PII Redaction (NIK, NPWP, Rekening, dsb)
    - Boundary Cap (4.000 chars / 5.000 baris)
              │
              ▼
[3. CustomComponent-seller_engine]
    - Threshold Guard + Withholding Auditor
    - Output: findings_json + summary_json
              │
              ├────────────────────────────────────────┐
              ▼                                        ▼
[5. Agent-FindingExplainer]              [7. Agent-ClaimDrafter]
    - Suhu: 0.0                              - Suhu: 0.1
    - Penjelasan 1-3 kalimat                 - Draf surat klaim marketplace
              ▲                                        ▲
              │                                        │
    [4. LanguageModelComponent-global (Centralized Gemini)]
              │
              ▼
[6. CustomComponent-numeric_validator]
    - Firewall halusinasi angka
    - Fallback template jika deviasi
              │
              └───────────────────┬────────────────────┘
                                  ▼
                     [8. CustomComponent-dispatcher]
                         - Google Sheets 9 Kolom
                         - Status LIVE / FAILED / SKIPPED
                                  │
                                  ▼
                         [9. ChatOutput]
                             - Laporan B2B formal tanpa emoji
```

---

## 2. Rincian Komponen Khusus (Custom Component Python)

### Node 2: `CustomComponent-normalizer_pii`
- **Tanggung Jawab:** Ingestion, sanitasi PII berlapis, hashing integritas input, dan mitigasi DoS.
- **Inputs:** `file_path_csv` (MessageTextInput), `file_path_profile` (MessageTextInput).
- **Outputs:** `sanitized_csv` (Output), `seller_profile` (Output), `input_sha256` (Output).
- **Logika Keamanan:**
  - Menghitung SHA-256 dari raw bytes kedua file input.
  - Memotong baris jika melebihi 5.000 baris dengan penanda keamanan `[TRUNCATED_AT_5000_ROWS_SECURITY_BOUNDARY]`.
  - Menerapkan regex PII strip pada nama pembeli, nomor telepon, alamat, dan nomor rekening.

### Node 3: `CustomComponent-seller_engine`
- **Tanggung Jawab:** Menjalankan engine deterministik `tools/seller_guard_engine.py`.
- **Inputs:** `sanitized_csv` (MessageTextInput), `seller_profile` (MessageTextInput), `config_mode` (MessageTextInput: default/test_a/test_b).
- **Outputs:** `findings_json` (Output), `summary_json` (Output), `evidence_table_markdown` (Output).
- **Logika Finansial:**
  - Eksekusi murni berbasis `Decimal`.
  - Mengelompokkan temuan ke dalam enum resmi (`OVER_WITHHELD`, `STATEMENT_MISSING`, dsb).
  - Menyertakan banner peringatan jika konfigurasi berstatus `UNVERIFIED`.

### Node 4: `LanguageModelComponent-global`
- **Tanggung Jawab:** Menjadi provider LLM terpusat (*DRY pattern*) untuk kedua agent.
- **Konfigurasi:** Google Generative AI (`gemini-3.5-flash`), `api_key` merujuk ke environment server (`GOOGLE_API_KEY`), temperature dasar `0.0`.

### Node 6: `CustomComponent-numeric_validator`
- **Tanggung Jawab:** Firewall validasi numerik pasca-LLM.
- **Inputs:** `llm_output` (MessageTextInput), `findings_json` (MessageTextInput).
- **Outputs:** `validated_output` (Output).
- **Logika:** Mengekstrak seluruh angka dari `llm_output`. Jika ditemukan angka yang tidak terdaftar pada `findings_json`, seluruh output ditolak dan diganti dengan template deterministik `EXPLANATION_FALLBACK`.

### Node 8: `CustomComponent-dispatcher`
- **Tanggung Jawab:** Pengiriman rekonsiliasi audit trail ke Google Sheets Seller Guard.
- **Inputs:** `summary_json` (MessageTextInput), `findings_json` (MessageTextInput), `input_sha256` (MessageTextInput).
- **Outputs:** `dispatch_status` (Output).
- **Logika Keamanan:** Membaca `SELLER_GUARD_SHEETS_URL` dan `SELLER_GUARD_TOKEN` langsung dari `os.environ`. Menangani status honest: `LIVE` (HTTP 200), `FAILED` (HTTP error), atau `SKIPPED` (jika URL kosong).

---

## 3. Standar Kompatibilitas Langflow Runtime

Untuk mencegah kegagalan deserialisasi pada Langflow Desktop:
1. **Atribut Wajib Komponen:** Seluruh template custom component wajib memiliki `_type: "Component"` dan `field_order` tersinkronisasi.
2. **Import Cleanliness:** Seluruh import SDK Langflow menggunakan:
   ```python
   from lfx.custom import Component
   from lfx.io import MessageTextInput, Output
   ```
3. **Penyimpanan File Flow:** Flow disimpan bertahap:
   - `flows/seith_warden_seller_guard_stage3.json`: Versi intermediate struktur canvas.
   - `flows/seith_warden_seller_guard.json`: Versi final terintegrasi penuh.

---

## 4. Gate Verifikasi Tahap 3

1. **Perintah Validasi Runtime:**
   ```powershell
   & "C:\Users\Lenovo\AppData\Local\com.LangflowDesktop\.langflow-venv\Scripts\python.exe" -c "
   import json
   from lfx.graph.graph.base import Graph
   with open('flows/seith_warden_seller_guard.json', 'r', encoding='utf-8') as f:
       data = json.load(f)
   g = Graph.from_payload(data)
   print(f'Graph Nodes: {len(g.vertices)}, Edges: {len(g.edges)}')
   "
   ```
2. **Kriteria Lulus (Sesuai Revisi 4):**
   - **Semua vertex build sukses dan semua edge tersambung** tanpa ada komponen yang terputus (disconnected dangling node).
   - Validasi sintaks JSON lulus `python -m json.tool flows/seith_warden_seller_guard.json`.
   - Tidak ada kredensial (`sk-...` atau API key plain) yang bocor di dalam flow JSON.
