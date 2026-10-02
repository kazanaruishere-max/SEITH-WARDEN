# 05 — Secrets Management & Transport Security

**Goal:** Menjamin tidak ada secret/API key plaintext yang ter-commit ke dalam repositori publik, memastikan seluruh API key diinjeksikan via environment variables / Global Variables Langflow, serta mengamankan kanal komunikasi HTTP client-server.

**Owner:** T2 | **Skill:** `security-reviewer` + `seith-warden-pm` | **Zone:** `.env.example`, `.gitignore`, `flows/seith_warden_flow.json`, `docs/security.md`

## 1. Konfigurasi Kredensial

* **Google Generative AI:** Node `LanguageModelComponent-global` dikonfigurasi dengan slot `api_key: ""` (kosong secara default). Kredensial diisi oleh pengguna via UI Langflow Desktop atau Global Variable `GOOGLE_API_KEY`.
* **Langflow MCP Server:** Dilindungi bearer token `x-api-key: ${LANGFLOW_API_KEY}`. Tanpa key, endpoint MCP menolak request dengan status 401/403.
* **Google Sheets Web App & Webhook:** URL diinjeksikan via input UI node atau variabel lingkungan `SHEETS_WEBHOOK_URL` dan `ALERT_WEBHOOK_URL`. Token `SEITH_WARDEN_2026` disimpan di environment, bukan di hardcoded commit rahasia.

## 2. Pemeriksaan Kebocoran (Leak Check)
* `git status` dan script audit `scripts/verify.ps1` memverifikasi bahwa file `.env` tidak pernah terlacak (*untracked / gitignored*).
* File `flows/seith_warden_flow.json` diaudit bersih dari string kunci privat (`sk-...`).

## 3. Verifikasi Nyata
* `pwsh -NoProfile -File scripts/verify.ps1` -> `[OK] bob streamablehttp`, `[OK] opencode vs bob identik (no drift)`, `All checks passed!`.
* Verifikasi file JSON: seluruh file konfigurasi valid sintaks dan bebas secret terbuka.

## 4. Accountability
* ✅ Terverifikasi: Repositori bebas dari hardcoded secret; verifikasi automated gate lulus 100%.
* ⚠️ Belum terverifikasi: Rotasi API key sebelum demo hari-H tetap menjadi tanggung jawab pengguna.
* 🔻 Risiko: Pengguna yang tidak sengaja melakukan `git add -f .env` dapat mengekspos kredensial ke remote.
* ♻️ Refactor: Unifikasi placeholder `${LANGFLOW_API_KEY}` pada `.bob/mcp.json` dan `.opencode/opencode.json`.
