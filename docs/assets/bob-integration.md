# Integrasi IBM Bob → Langflow SEITH-WARDEN (Real Connected)

> **Status: REAL CONNECTED** — Bob sebagai MCP Client terhubung ke Langflow Desktop SEITH-WARDEN via `streamablehttp`. Protokol identik dengan `opencode` proxy di `.opencode/opencode.json`.

## Arsitektur (PDF Hal 21-26,30-31)

```
User natural → IBM Bob (MCP Client, pilih tool) → MCP streamablehttp x-api-key → Langflow Desktop :7860 (PII→dual-vector→RefMapper0.0→RuleAuditor0.0→RiskSynthesizer0.1→Sheets/Webhook) → JSON strict → Bob → User
```

- **Server:** Langflow Desktop `http://localhost:7860/api/v1/mcp/project/a760286c-db9f-406b-bb95-4d2121592e5e/streamable`
- **Client:** IBM Bob (Gear → MCP) + `opencode` (dev proxy) — keduanya discovery 3 tools `Action+Input` yang sama
- **Bob peran:** Wajah/selector/renderer — bukan logika audit (logika di Langflow)

## Prerequisite

- Langflow Desktop jalan: `uv run langflow run --host 127.0.0.1 --port 7860` → `Invoke-WebRequest http://localhost:7860/api/v1/flows -Headers @{"x-api-key"="$env:LANGFLOW_API_KEY"}` → 200 (jangan kill :7860 — Tier-0)
- Project ID `a760286c-db9f-406b-bb95-4d2121592e5e` — cek URL bar Langflow `/project/<id>` jika beda update semua config
- `uvx` tersedia: `uv --version` + `uvx --help`

## Konfigurasi Langflow Desktop — Global Variables (Desktop tidak ada Generate API Key)

1. Langflow → `Settings → Global Variables → Add New`
2. `Type: Credential → Name: LANGFLOW_API_KEY → Value: <isi dari .opencode/opencode.json:15, dev-only sk-...So, H-1 revoke 2026-10-03>` → Save. Variabel ini auto-apply ke field `API Key`.
3. Alternative jika Desktop no-auth: kosongkan — test Bob tanpa header dulu (lihat fallback).

## Konfigurasi Bob — Gear → MCP (Real)

1. Bob → ikon **Gear → MCP → edit `lf-seith_warden`** (atau `+ Add MCP Server`)
2. Tempel config **dengan auth** (pakai key existing, H-1 revoke):
```json
{
  "mcpServers": {
    "lf-seith_warden": {
      "command": "cmd",
      "args": ["/c", "uvx", "--with", "mcp~=1.28", "mcp-proxy", "--transport", "streamablehttp", "--headers", "x-api-key", "${LANGFLOW_API_KEY}", "http://localhost:7860/api/v1/mcp/project/a760286c-db9f-406b-bb95-4d2121592e5e/streamable"]
    }
  }
}
```
Ganti `${LANGFLOW_API_KEY}` dengan value `sk-...So` dari `.opencode/opencode.json:15` jika Bob tidak expand env.
3. **Fallback tanpa header** jika 0 tools (Desktop sering no-auth):
```json
{"mcpServers":{"lf-seith_warden":{"command":"cmd","args":["/c","uvx","--with","mcp~=1.28","mcp-proxy","--transport","streamablehttp","http://localhost:7860/api/v1/mcp/project/a760286c-db9f-406b-bb95-4d2121592e5e/streamable"]}}}
```
4. Restart Bob → verify discovery **3 tools `Action+Input`**:
   - `audit_sop_regulatory_reference(sop_text: string)`
   - `evaluate_rate_cap_substance(daily_rate_percent: number, lock_cap_percent?: number)`
   - `generate_compliance_remediation_log(clause_id, risk_level, remediation_text)`

## Konfigurasi Opencode (Dev Proxy — Identik Protokol)

File `.opencode/opencode.json` sudah identik — dev harian via `opencode` tanpa buka Bob berat:

```json
{"mcp":{"seith-warden-langflow":{"type":"local","command":["uvx","--with","mcp~=1.28","mcp-proxy","--transport","streamablehttp","--headers","x-api-key","${LANGFLOW_API_KEY}","http://localhost:7860/api/v1/mcp/project/a760286c-db9f-406b-bb95-4d2121592e5e/streamable"],"enabled":true}}}
```

## Tool Naming (PDF Hal 27-29) — Action+Input

| Tool | Action | Input |
|:---|:---|:---|
| `audit_sop_regulatory_reference` | audit | sop_text |
| `evaluate_rate_cap_substance` | evaluate | daily_rate_percent + sop_text |
| `generate_compliance_remediation_log` | generate | clause_id + risk_level + remediation_text |

## Verifikasi Lapis (PDF Hal 32-34)

1. **Flow:** Langflow Playground input dummy `Pasal 1 bunga 0,25%/hari` → Chat Output JSON `risk_level:HIGH` + `citation: PADK 2026 Pasal 12 Ayat 1`
2. **MCP:** `Invoke-WebRequest http://localhost:7860/api/v1/flows` → 200
3. **Bob:** daftar tools harus 3 → uji explicit `"audit klausul Pasal 1 bunga 0,25%/hari"` → expect `HIGH + RATE_CAP_BREACH` sebelum natural language variasi

## Troubleshooting

- 0 tools di Bob → cek `uvx` di PATH (`where uvx`), cek `x-api-key` header, coba fallback tanpa header, ganti `--with mcp<2.0.0` jika Hal 59 minta
- Project ID mismatch → update URL `.../project/<id_baru>/streamable` di Bob + opencode.json
- Chat kosong → cek `flows/seith_warden_flow.json` `${env}` only (no hardcode `sk-` di JSON selain opencode dev-only)

## Bukti Submission

- [ ] Screenshot Bob `Gear → MCP` menampilkan 3 tools `Action+Input`
- [ ] Screenshot Langflow Playground `HIGH` vs Bob chat `HIGH` yang sama
- [ ] `flows/seith_warden_flow.json` (3 prompt terkunci + dual retriever + Sheets/Webhook) + `python -m json.tool` valid

Sumber: PDF `docs/assets/Hacktiv8 Hackathon National - Google Slide.pdf` Hal 4,21-34,56-60,86.
