# Phase 02 — Security Hardening, Data Quality & Prompt Resilience

**Goal:** Memperketat ketahanan sistem terhadap prompt injection, membenahi kualitas data audit trail Sheets, dan mengunci keamanan transport serta token endpoint sesuai standar Responsible AI (15%) dan Technical Execution (10%).

## 1. Konteks & Ringkasan Perubahan

Berdasarkan pengujian live pada runtime Langflow Desktop dan Google Sheets Apps Script, fase ini menyelesaikan perbaikan nyata tanpa overclaim:

1. **Perbaikan Kualitas Data Audit Trail (Sheets & Report):**
   * **Deduplikasi Label Klausul:** Mengatasi duplikasi label (`Pasal Pasal 1` → `Pasal 1`).
   * **Ekstraksi Persentase Dinamis:** Kolom `Found_Value` kini mengekstrak nilai riil dari temuan regulasi secara otomatis (`0.25%/hari`, bukan lagi `-`).
2. **Mitigasi Prompt Injection (Defense-in-Depth):**
   * **Framing Jujur:** Mitigasi ini bersifat reduksi risiko berlapis (*defense-in-depth*), bukan perlindungan absolut 100%.
   * **Batas Delimiter:** Teks SOP diisolasi sebagai data pasif untuk diaudit, bukan instruksi yang dieksekusi.
   * **Hierarki Instruksi:** Aturan sistem (`SYSTEM INSTRUCTIONS`) diutamakan secara mutlak di atas instruksi pengguna/dokumen SOP. Instruksi berbahaya (seperti *"ignore previous instructions"* atau *"print HACKED"*) diabaikan dan tetap dievaluasi sebagai data audit kepatuhan.
   * **Input Length Cap:** Node PII Sanitizer membatasi panjang input maksimal 4.000 karakter untuk mencegah payload flooding DoS pada LLM.
3. **Keamanan Endpoint & Token Unifikasi:**
   * Token autentikasi endpoint Google Apps Script diseragamkan menjadi `SEITH_WARDEN_2026` di seluruh komponen, dokumentasi, dan query parameter.
   * Komponen dispatcher menyematkan `?token=SEITH_WARDEN_2026` secara otomatis dan menangani kode status `401` dan `403` secara faktual.

---

## 2. Rincian Perubahan Komponen

| Komponen | Node ID | Tindakan Hardening |
|:---|:---|:---|
| **PII Sanitizer** | `CustomComponent-pii` | Sanitasi NIK, rekening, email + pemotongan batas 4.000 karakter (`MAX_CHARS`). |
| **RefMapper Agent** | `Agent-RefMapper` | Instruksi sistem terkunci + perlakuan teks input sebagai data pasif non-eksekusi. |
| **RuleAuditor Agent** | `Agent-RuleAuditor` | Validasi numerik PADK 2026 Pasal 12 + isolasi instruksi embedded. |
| **RiskSynthesizer Agent** | `Agent-RiskSynthesizer` | Penegakan output Strict JSON murni untuk mencegah prompt jailbreak format. |
| **Sheets & Webhook Dispatcher** | `CustomComponent-sheets_webhook` | Deduplikasi `Pasal`, ekstraksi dinamis `found_value`, dan penyematan token `SEITH_WARDEN_2026`. |

---

## 3. Verifikasi & Pengujian Runtime

* **Kompilasi Graph Langflow:** `lfx.graph.graph.base.Graph.from_payload` → 10/10 Vertices SUCCESS.
* **Eksekusi Komponen:**
  * PII Sanitizer: String panjang > 4.000 karakter terpotong aman dengan marker `[TRUNCATED_AT_4000_CHARS_SECURITY_BOUNDARY]`.
  * Verifier: Ekstraksi nilai numerik `0.25%/hari` terverifikasi akurat vs plafon `0.10%/hari`.
  * Sheets Dispatcher: Payload 9 kolom terkirim via HTTP POST dengan query token `SEITH_WARDEN_2026`.
* **PM Gate:** Script `scripts/verify.ps1` menghasilkan status **GATE GREEN**.

---

## 4. Referensi
* `docs/setup.md §9` (Panduan Deploy Google Apps Script dengan token).
* `docs/security.md` (Spesifikasi Keamanan & Responsible AI).
* `flows/seith_warden_flow.json` (Flow Langflow Terpadu).
