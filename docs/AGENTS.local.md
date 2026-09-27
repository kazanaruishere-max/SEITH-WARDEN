# KEPUTUSAN LOKAL PROYEK: SEITH-WARDEN
**Proyek:** SEITH-WARDEN (Supervisory Engine for Institutional Trust & Hazard-mitigation — Workflow Automation & Regulatory Detection Engine Network)  
**Kompetisi:** Hackathon Nasional Hacktiv8 x IBM 2026 (Financial)  
**Tanggal:** September 2026 — Deadline Submission 4 Oktober 2026  
**Tim:** Solo — Free Tier Stack

## 1. Penamaan & Branding
- **Nama Resmi:** SEITH-WARDEN (menggantikan SEITH-XEIR). SEITH = Supervisory Engine... | WARDEN = Workflow Automation...
- **Kebijakan Bahasa:** Full Bahasa Indonesia untuk semua docs kecuali `README.md` yang bilingual ID|EN untuk juri IBM global + OJK lokal.

## 2. Arsitektur & Stack Lock
- **Orchestrator:** Langflow + MCP Server `streamablehttp` `127.0.0.1:7860` (Action+Input) — PDF Hal 21.
- **LLM:** Google Gemini 1.5 Flash free tier (`temperature 0.0 / 0.0 / 0.1` — lihat `AGENTS.md §2`).
- **Vector Store:** `chroma-local` default gratis dual-collection isolated. `astra` opsional H2.
- **Embedding:** Google `text-embedding-004` free tier.
- **External Tools:** Google Sheets API free + `webhook.site` / Slack free webhook (conditional HIGH only).
- **Python:** WAJIB `uv` (`uv run ...`), jangan `python` langsung.
- **Bob:** Real connected — Bob `Gear→MCP lf-seith_warden` via `mcp-proxy --transport streamablehttp --headers x-api-key` → Langflow Desktop `:7860` `a760286c-.../streamable` (reuse key `sk-...So` H-1 revoke, no generate baru). Dev proxy via `.opencode/opencode.json` protokol identik. Detail: `docs/assets/bob-integration.md` (real).

## 3. Tool-Calling & Eskalasi
- **Sheets:** Audit trail permanen (Timestamp | Dokumen | Klausul | Jenis | Nilai | Batas | Risiko | Rekomendasi | Reviewer).
- **Webhook:** Hanya `risk_level=="HIGH"` (conditional node). Skipped jika LOW/MEDIUM.
- **Fallback Tunggal:** `PERLU_VERIFIKASI_MANUAL` — sinkron di `AGENTS.md`, `docs/arsitektur.md`, `docs/security.md`.

## 4. Secret Policy (H-1 Rule)
- Kredensial via env var (`GOOGLE_API_KEY`, `LANGFLOW_API_KEY`, `SHEETS_*`). `.opencode/opencode.json` pakai `${env}` placeholder.
- **Dev-only:** Key plaintext lokal `.opencode/opencode.json:15` diizinkan sementara untuk fleksibilitas solo. **WAJIB revoke/ganti env-only sebelum submit public link 2026-10-03.**
- File `flows/*.json` dan `.env` masuk `.gitignore`.

## 5. Decision Log

| Tanggal | Keputusan | Alasan | Dampak |
|:---|:---|:---|:---|
| 2026-09-26 | Dual vector `chroma-local` gratis | Free tier, demo offline, hindari vendor lock | ADR-001 |
| 2026-09-26 | Full ID kecuali README bilingual | Kecepatan solo + pasar OJK lokal, README untuk IBM global | Konsistensi docs |
| 2026-09-26 | H-1 revoke rule | Fleksibilitas dev solo vs keamanan submit public | Blok Accountability wajib catat |
| 2026-09-26 | Lock temp 0.0/0.0/0.1 + fallback tunggal | Deterministik audit, anti-halusinasi Responsible AI | `AGENTS.md §1` |
| 2026-09-26 | Rumus AGENTS 10§ MARKET-IDX untuk WARDEN | Anti AI generik/slop, flow jelas, no bug logic, refactor wajib | AGENTS.md rewrite |
| 2026-09-27 | Perkuat docs/arsitektur.md §2-§6 + skeleton flows/ | Pipeline detail + MCP 3 schema + Sheets 9 kolom siap implementasi | Docs 100% ready |
| 2026-09-27 | Bob formalitas via opencode + docs/assets | PDF 88 hal: Bob wajib sebagai MCP client, runtime harian opencode tanpa install berat | `docs/assets/bob-integration.md` |
| 2026-09-27 | Perkuat prd §1.3 canvas Hal73 + §4.4 kompetitor + §4.5 roadmap | Maks 30% Innovation + 20% Problem Clarity per PDF | PRD 100% |
| 2026-09-27 | Perkuat security §2,5,6 Hal 81-85 + README badge | Maks 15% Responsible AI (data/output/action + bias) | Security 100% |
| 2026-09-27 | Handoff governance Phase00 done + Phase01 sliced 5 + template | AGENTS §8b — 00 `01/02` slices, Phase01 `01-05` kontrak, template DoD 8 gate | Handoff 100% ready → implementasi |
| 2026-09-27 | Bob real connected Gear→MCP + Global Variables LANGFLOW_API_KEY reuse | Juri wajib Bob, Desktop tanpa Generate API Key — fallback no-header test, approve reuse sk-...So H-1 revoke | `docs/assets/bob-integration.md` real + `.handoff/04-mcp-server.md` |
| 2026-09-27 | Novel uplift: ceiling Graph + deterministic Code + HITL loop + dual persona | Anti generic LLM→LLM→LLM — Innovation 30% + RAI 15% — Graph 0.1/100 presisi + Code re deterministic + Sheets REJECT re-route + cost_avoided | `data/kb/padk_graph.json` + `tools/ceiling_verify.py` + `.handoff/06-08` + `flows v0.2.0` |

## 6. Handoff & Verification Gate
- **Awal sesi:** `Read docs/AGENTS.local.md` + `.handoff/phase-NN-topic/00-overview.md` (phase aktif).
- **Akhir sesi/topik:** `skill://handoff` → `.handoff/phase-NN-topic/*.md` + Accountability `✅/⚠️/🔻/♻️`.
- **Gate:** `uv run ruff check .` + `tree /F` + `10 skenario JSON valid` + `flows/seith_warden_flow.json valid` — klaim selesai hanya jika lulus dengan output asli.
- **Tracer:** Phase00 `00-overview.md`+`01/02` done + Phase01 `00-overview.md`+`01-08` sliced uplift (Graph+Code+HITL+dual persona) → `.handoff/README.md` SSOT — flow `v0.2.0` 14 nodes.

## 7. Roadmap Ringkas
- **MVP Hackathon (now):** Dual ingestion → GraphLookup(0.1/100) + Code deterministic + 3-agent chain → Strict JSON + Sheets HITL REJECT→re-route + cost_avoided + Bob dual persona. *Science: Innovation 30% + RAI 15% uplift.* YAGNI OCR/BI/ISO Q2-Q4.
- **Q2-Q4:** OCR, multi-tenant, BI/PDP expansion, OJK auto-sync. Free infra MVP = margin SaaS tinggi untuk jualan.

## 8. Referensi Cepat
- Spec agen: `AGENTS.md` — Arsitektur: `docs/arsitektur.md` + `docs/assets/bob-integration.md` — Security: `docs/security.md` — Setup: `docs/setup.md` — Lexicon: `docs/CONTEXT.md` — Hackathon: `docs/hacktiv8_hackathon_national.md` + PDF `docs/assets/Hacktiv8 Hackathon National - Google Slide.pdf` — KB: `data/kb/padk_2026_curated.md` — Skenario: `tests/test_scenarios.json`.
