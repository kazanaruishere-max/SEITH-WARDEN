# 07 — Deterministic Number Grounding (Code Node anti-hallucination)

**Goal:** LLM tidak dipercaya hitung — `Code` node `re` deterministik verifikasi `0.25 > 0.1`.

**Owner:** T1 | **Skill:** `tdd-guide` + `seith-warden-compliance` | **Zone:** `tools/ceiling_verify.py` `fn<50 stdlib`

**Alur di Canvas:**
```
ChatInput → [LLM extract raw:"0,25%"] → Code(tools/ceiling_verify.py extract_percent) → Comparator(verify_ceiling vs Graph ceiling) → RiskSynthesizer
           Code node hijau visible — judges lihat anti-hallucination
```

**Tools:**
```py
# tools/ceiling_verify.py — Code Component Langflow
def extract_percent(text): re.search(r"\d+(?:[.,]\d+)?\s*%", text)
def verify_ceiling(text, param="daily_rate_percent"): {found, ceiling: Graph, violation: found>ceiling, status}
```
- LLM hanya ekstrak `raw:"0,25%"`, Code yang `float(0.25)` + compare `> Graph[0.1]` → `VIOLATION` + `span evidence`.
- Ambiguitas `"kompetitif"` → `extract=None` → `PERLU_VERIFIKASI_MANUAL` (jangan tebak).

**Input → Output:**
```
"0,25%/hari" + Graph 0.1 → {found:0.25, ceiling:0.1, violation:true, status:VIOLATION}
"bunga kompetitif" → {found:None, status:PERLU_VERIFIKASI_MANUAL}
"Lock 120%" → {found:120, ceiling:100, violation:true}
```

**Verify:**
```
uv run ruff check tools/ceiling_verify.py → 0
uv run python tools/ceiling_verify.py → ok (5 assert: extract, daily VIOLATION, COMPLIANT, PERLU, lock)
Playground Pasal1 0,25% → HIGH dengan span evidence "0,25% > 0,10%"
```

**Science:** Regulatory compliance cannot hallucinate numbers — deterministic Code = Responsible AI 15% wow, bukan LLM math.

**Accountability:**
- ⚠️ Regex koma vs titik — normalize `replace(",",".")`
- 🔻 LLM hitung langsung = hallucination risk — Code node wajib presisi
- ♻️ Refactor: inline re logic shared dengan `pii_sanitizer.py`? No — separate fn<50 keep isolated

**Next:** 08-hitl-loop.md
