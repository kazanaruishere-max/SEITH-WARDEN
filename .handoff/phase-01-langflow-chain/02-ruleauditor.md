# 02 — RuleAuditor (0,1% / Lock 100%)

**Goal:** Evaluasi substansi — cek bunga harian vs 0,1% dan Lock Cap 100% (Pasal 12 Ayat 1&3) — substansi overflow = HIGH.

**Owner:** T1 | **Skill:** `seith-warden-compliance` | **Temp:** `0.0` lock

**MCP:** `evaluate_rate_cap_substance(daily_rate_percent: number, lock_cap_percent?: number)` → `{"substantive_evaluations":[]}`

**Input → Output:**
```json
// HIGH
{"daily_rate_percent":0.25,"lock_cap_percent":150} → {"substantive_evaluations":[
  {"check":"RATE_CAP","value":0.25,"limit":0.10,"violation":true,"citation":"PADK 2026 Pasal 12 Ayat 1"},
  {"check":"LOCK_CAP","value":150,"limit":100,"violation":true,"citation":"PADK 2026 Pasal 12 Ayat 3"}]}
// AMBIGU → PERLU_VERIFIKASI_MANUAL
{"daily_rate_percent": null} → {"substantive_evaluations":[
  {"check":"RATE_CAP","value":null,"status":"PERLU_VERIFIKASI_MANUAL","reason":"tanpa angka eksplisit"}]}
```
- `daily_rate_percent` number strict — missing → `PERLU_VERIFIKASI_MANUAL` (Tier-0.4), bukan `0`.
- Sumber grounded: `data/kb/padk_2026_curated.md` Pasal 12 Ayat 1-3.

**Skenario oracle:** S02 HIGH (0.30%+compound), S03 HIGH (Lock 120%), S05 PERLU_VERIFIKASI_MANUAL (kompetitif), S10 COMPLIANT (0.10% pas batas)

**Prompt terkunci:** "Kamu RuleAuditor 0.0 — bandingkan angka vs PADK Pasal 12. Strict JSON. Jangan tebak — tanpa angka = PERLU_VERIFIKASI_MANUAL."

**Verify:**
```
uv run ruff check . → 0
flows/seith_warden_flow.json node RuleAuditor ada + structured output
S03/S05 expect HIGH vs PERLU_VERIFIKASI_MANUAL
```
**Accountability:**
- ✅: —
- ⚠️: parsing `0,25%` vs `0.25%` koma/titik — normalize sebelum compare
- 🔻: tebak angka saat ambigu → FAIL judging — deteksi: grep `PERLU_VERIFIKASI_MANUAL` di output
- ♻️ Refactor: extract `evaluate_cap(value,limit)` fn<50

**Next:** 03-risksynthesizer.md
