# 06 — Ceiling Graph (PADK Knowledge Graph, bukan RAG cosine)

**Goal:** Presisi batas regulasi 100% — `RuleAuditor` query Graph `padk_graph.json` bukan vector cosine noise.

**Owner:** T1 | **Skill:** `seith-warden-compliance` | **Zone:** `data/kb/padk_graph.json`

**Graph:**
```json
{"pasal12":{"ayat1":{"ceiling":0.1,"unit":"%/hari","scope":"konsumtif","citation":"PADK 2026 Pasal 12 Ayat 1"},"ayat3":{"ceiling":100,"unit":"% pokok","scope":"bunga+denda+biaya ≤ pokok","citation":"PADK 2026 Pasal 12 Ayat 3"}}}
```
- Sinkron dengan `data/kb/padk_2026_curated.md` — cek drift tiap `scripts/verify.ps1`.
- Sumber SSOT ceiling — LLM dilarang invent angka batas.

**Langflow:** `Custom Component GraphLookup` — input `param=daily_rate_percent|lock_cap_percent` → output `ceiling + citation`. Visual node hijau di canvas, beda dari Retriever.

**Input → Output:**
```
daily_rate_percent + Graph(0.1) → {ceiling:0.1, citation:"Pasal 12 Ayat 1", violation: found>0.1}
lock_cap_percent + Graph(100) → {ceiling:100, violation: 120>100}
```

**Verify:**
```
uv run python -m json.tool data/kb/padk_graph.json → valid
python: Graph["pasal12"]["ayat1"]["ceiling"]==0.1
Bob vs Playground: citation exact bukan similarity score
```

**Accountability:**
- ⚠️ Drift graph vs curated.md — deteksi: `grep 0,1% data/kb/*`
- 🔻 Cosine RAG untuk ceiling = FAIL judging — Graph wajib presisi
- ♻️ Refactor: extract graph to `ADR-002-ceiling-graph`

**Next:** 07-deterministic-verify.md
