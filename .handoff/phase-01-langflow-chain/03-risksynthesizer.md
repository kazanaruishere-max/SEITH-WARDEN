# 03 — RiskSynthesizer (HIGH/MEDIUM/LOW + Draft Klausul)

**Goal:** Gabung RefMapper+RuleAuditor → `risk_level` + `draft_recommendation` + `Preliminary Advisory` disclaimer — HITL final.

**Owner:** T2 | **Skill:** `seith-warden-compliance` | **Temp:** `0.1` lock

**Chain:** `RefMapper{detected_references} + RuleAuditor{substantive_evaluations} → RiskSynthesizer`

**Output Strict JSON:**
```json
{
  "clause_id": "1",
  "risk_level": "HIGH",
  "category": "RATE_CAP_BREACH",
  "evidence": ["SEOJK 5/2023 DEPRECATED","0.25% >0.10% Pasal 12 Ayat 1"],
  "citations": ["PADK 2026 Pasal 12 Ayat 1"],
  "draft_recommendation": "Ganti: 'Bunga harian maksimal 0,1% dari pokok; total akumulasi bunga+denda+biaya ≤100% pokok (PADK 2026 Pasal 12 Ayat 3).'",
  "disclaimer": "Preliminary Advisory — wajib divalidasi Legal & Compliance.",
  "human_review_required": true
}
```
- Enum: `HIGH` (violation true), `MEDIUM` (SEOJK tanpa violation angka), `LOW` (typo), `PERLU_VERIFIKASI_MANUAL` (ambigu), `COMPLIANT`
- `draft_recommendation` sitasi PADK — grounded gate, auto legal verdict dilarang.

**Skenario oracle:** S01 RATE_CAP_BREACH HIGH, S04 DEPRECATED_CODE MEDIUM, S07 LOW, S05 PERLU_VERIFIKASI_MANUAL, S09-10 COMPLIANT

**Prompt terkunci:** "Kamu RiskSynthesizer 0.1 — sintesa 2 input, strict JSON `risk_level+draft_recommendation+disclaimer`. Regex fallback jika markdown bocor. HITL `human_review_required:true` selalu."

**Verify:**
```
uv run ruff check . → 0
flows/seith_warden_flow.json node RiskSynthesizer + Chat Output strict JSON
tests/test_scenarios.json 10 skenario expect sesuai
```
**Accountability:**
- ✅: —
- ⚠️: markdown bocor → parse fail — butuh regex fallback `\{.*\}`
- 🔻: no disclaimer → Tier-0.1 FAIL — deteksi: `grep Preliminary Advisory flows/*.json`
- ♻️ Refactor: extract `synthesize_risk()` fn<50 + `draft_clause()` fn<50

**Next:** 04-mcp-server.md
