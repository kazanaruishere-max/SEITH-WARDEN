# Panduan Setup — SEITH-WARDEN (Free Tier + Formalitas Bob)

Stack gratis 100%. Python wajib via `uv`. Bob = formalitas MCP client (PDF Hal 4,21,30) — runtime harian `opencode`.

## 1. Prasyarat
- `uv` terinstall (`uv --version`) — jangan pakai `python` langsung.
- `GOOGLE_API_KEY` free tier dari https://aistudio.google.com untuk Gemini 1.5 Flash + `text-embedding-004` (PDF Hal 44).
- `LANGFLOW_API_KEY` lokal untuk MCP `x-api-key`.
- Opsional `COMPOSIO_API_KEY` dari https://dashboard.composio.dev (PDF Hal 41-43) — hanya jika pakai Google Docs/Calendar via Composio; free tier cukup Sheets API langsung.
- Opencode terinstall (`.opencode/opencode.json` sudah ada). Bob tidak wajib install harian — lihat formalitas di `docs/assets/bob-integration.md`.

## 2. Instalasi

```bash
cp .env.example .env  # isi GOOGLE_API_KEY & LANGFLOW_API_KEY (dan COMPOSIO jika perlu)
uv sync
```

Isi `.env`:

```
GOOGLE_API_KEY=...
LANGFLOW_API_KEY=...
VECTOR_STORE=chroma-local
SHEETS_ID=...
SHEETS_WEBHOOK_URL=...
```

## 3. Konfigurasi Kredensial Langflow (PDF Hal 44-47)

1. Buka `https://aistudio.google.com/u/0/api-keys` → Create API Key → salin → isi `GOOGLE_API_KEY`.
2. (Opsional) `https://dashboard.composio.dev` → Platform mode → Create API Key → centang Write All → salin `COMPOSIO_API_KEY`.
3. Langflow → Rocket icon → Settings → Model Providers → masukkan Gemini API Key → Save.
4. Langflow → Global Variables → Add New → Key `COMPOSIO_API_KEY` Value (jika pakai).

## 4. Jalankan Langflow + MCP

```bash
uv run langflow run --host 127.0.0.1 --port 7860
# Endpoint MCP: http://localhost:7860/api/v1/mcp/project/a760286c-db9f-406b-bb95-4d2121592e5e/streamable
# Header: x-api-key: $LANGFLOW_API_KEY
```

Verifikasi: `Invoke-WebRequest http://localhost:7860/api/v1/flows -Headers @{"x-api-key"="$env:LANGFLOW_API_KEY"}` harus 200 sebelum demo.

## 5. Bob sebagai MCP Client — Formalitas

- Runtime harian pakai `opencode` (protokol `streamablehttp` + `mcp-proxy` identik dengan Bob — PDF Hal 31).
- Untuk juri: ikuti `docs/assets/bob-integration.md` Hal 56-60: `Langflow MCP Server → JSON → Generate API Key` → Bob `Gear → MCP → + → tempel JSON` + args `--with mcp<2.0.0` → discovery 3 tools `Action+Input`.
- Tidak perlu install Bob harian (~300MB). Bukti protocol sama: `.opencode/opencode.json`.

## 6. Vector Store

- Default `chroma-local` gratis offline — dual collection `collection_sop_internal` + `collection_ojk_padk2026` (isolated).
- Opsional `astra` — isi `ASTRA_DB_*` di `.env`, set `VECTOR_STORE=astra`.

## 7. Test 10 Skenario

```bash
uv run ruff check .
uv run python tools/pii_sanitizer.py  # harus ok (re NIK→rekening→email)
uv run python -m json.tool tests/test_scenarios.json
uv run python -m json.tool flows/seith_warden_flow.json
```

## 8. Verifikasi Lengkap (PDF Hal 32-34)

1. Flow dulu: Playground `sop_bunga_dummy.md Pasal 1 (0,25%/hari)` → Chat Output `risk_level: HIGH`.
2. Project/MCP: MCP aktif, endpoint benar, flow ditemukan.
3. Bob terakhir: Bob discover 3 tools, uji `"audit klausul Pasal 1"`.

## 9. Submit (4 Okt 2026)

- Revoke H-1 (2026-10-03): ganti `.opencode/opencode.json` plaintext `sk-hhTm1...` → `${env}`.
- Pastikan repo/file public `Anyone with the link` di `bit.ly/submit-hackathon` + absensi `bit.ly/absensi-hackathon` tiap camp.
