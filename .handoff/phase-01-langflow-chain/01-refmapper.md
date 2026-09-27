# 01 — RefMapper (SEOJK→PADK)

**Goal:** Deteksi 2-arah format usang SEOJK→PADK dengan sitasi pasal — qualifying test Financial.

**Owner:** T1 | **Skill:** `seith-warden-compliance` + `tdd-guide` | **Temp:** `0.0` lock

**MCP:** `audit_sop_regulatory_reference(sop_text: string)` → `{"detected_references":[]}`

**Retriever:** PADK `collection_ojk_padk2026` hierarchical Bab→Pasal→Ayat (`data/kb/padk_2026_curated.md`)

**Input → Output:**
```json
// input
{"sop_text": "Pasal 1 ... sesuai SEOJK No.5/2023 ... bunga 0,25%/hari"}
// output
{"detected_references": [
  {"clause_id":"1","format_type":"SEOJK","code":"SEOJK 5/2023","status":"DEPRECATED","citation":"PADK 2026 Pasal 12 Ayat 1","severity":"MEDIUM"},
  {"clause_id":"1","format_type":"PADK","code":"PADK 2026 Pasal 12 Ayat 1","status":"ACTIVE","citation":"PADK 2026 Pasal 12 Ayat 1","severity":"-"}
]}
```
- `SEOJK` → `DEPRECATED` | `POJK/PADK` → `ACTIVE` — grounded gate (§4.1), no tebak.
- SOP chunk 800/150 recursive, PII sudah strip `sanitize_sop_text` NIK→rek→email.

**Skenario oracle:** S01 HIGH (SEOJK+0.25%), S04 MEDIUM (SEOJK tanpa angka), S06 MEDIUM (usang aman), S09 COMPLIANT (PADK 0.08%)

**Prompt terkunci (ringkas):** "Kamu RefMapper 0.0 — hanya sitasi `data/kb/padk_2026_curated.md`. Kembalikan strict JSON `detected_references[]`. Fallback `PERLU_VERIFIKASI_MANUAL` jika tanpa kode regulasi eksplisit."

**Verify:**
```
uv run ruff check . → 0
python -m json.tool flows/seith_warden_flow.json → valid (node RefMapper ada)
tests/test_scenarios.json S01/S04 expect sesuai
```
**Accountability:**
- ✅: —
- ⚠️: retriever PADK belum ter-index `chroma-local` — mock vector dulu
- 🔻: context bleeding jika SOP/PADK campur — deteksi: dual-collection isolated check
- ♻️ Refactor: extract `parse_regulatory_code()` fn<50

**Next:** 02-ruleauditor.md
