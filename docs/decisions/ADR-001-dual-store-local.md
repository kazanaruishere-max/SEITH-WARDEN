# ADR-001: Dual Vector Store — chroma-local (Free) vs Astra DB

**Status:** Accepted — 2026-09-26 | **Scope:** MVP Hackathon (Free Tier)

## Konteks | Context
Butuh dual-collection isolated (SOP vs PADK). Astra butuh token berbayar & online; juri nilai modularity, bukan vendor.

## Keputusan | Decision
Default `chroma-local` (gratis, offline, dual-collection). Astra opsional via `VECTOR_STORE=astra` + `ASTRA_DB_*`.

## Konsekuensi | Consequences
* Pro: 0 cost, demo offline, no vendor lock, lolos 10% Technical Execution.
* Kontra: Tidak persistent cloud-scale — *ponytail: ceiling hackathon; upgrade ke Astra saat SOM >20 klien Q2.*

## Verifikasi | Verification
`VECTOR_STORE` env switch + `tree` + 10 skenario pass di kedua backend.
