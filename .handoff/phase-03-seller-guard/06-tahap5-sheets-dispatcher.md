# Phase 03 — Task 06: Tahap 5 — Integrasi Google Sheets Dispatcher & Keamanan Transport

**Goal:** Mengimplementasikan pengiriman audit trail ke Google Sheets baru (terpisah penuh dari sheet audit SOP lama) menggunakan skema 9 kolom, autentikasi token lingkungan (`SELLER_GUARD_SHEETS_URL` dan `SELLER_GUARD_TOKEN`), pencatatan identitas ter-pseudonimkan (`sha256(NIK)[:12]`), dan pelaporan status faktual (`LIVE`, `FAILED`, `SKIPPED`).

---

## 1. Skema Kolom Audit Trail (9 Kolom + Hash Integritas)

Setiap temuan yang diekstrak oleh engine dikirimkan ke baris Google Sheets dengan struktur:

| No | Nama Kolom | Tipe Data | Deskripsi & Contoh Nilai | Standar Keamanan Finansial |
|:---|:---|:---|:---|:---|
| 1 | `Timestamp` | String (ISO) | `2026-10-01 14:30:00` | Waktu pemeriksaan audit dilakukan. |
| 2 | `SellerRef` | String (Masked) | `a1b2c3d4e5f6` | **Pseudonim:** `sha256(NIK)[:12]`. Dilarang menampilkan NIK/NPWP mentah! |
| 3 | `Marketplace` | String | `Marketplace A` | Platform tempat transaksi terjadi. |
| 4 | `Finding_Type` | Enum String | `OVER_WITHHELD` | Salah satu dari enum resmi temuan kepatuhan. |
| 5 | `Order_Count` | Integer | `3` | Jumlah pesanan yang terdampak temuan ini. |
| 6 | `Observed_IDR` | Decimal String | `150000` | Total nominal PPh 22 yang riil dipungut. |
| 7 | `Expected_IDR` | Decimal String | `0` | Total nominal PPh 22 yang seharusnya menurut aturan. |
| 8 | `Delta_IDR` | Decimal String | `150000` | Selisih nominal (potensi klaim pengembalian dana). |
| 9 | `Status` | String | `LIVE` / `SKIPPED` | Status audit: `PENDING_REVIEW` / `FLAGGED`. |
| * | `Input_SHA256` | String (Hex) | `7f83b1657ff1...` | Bukti kriptografis keaslian file CSV saat diaudit. |
| * | `Reviewer` | String | `Preliminary Advisory` | Penanda *Human-in-the-loop* wajib. |

---

## 2. Kode Google Apps Script (`SellerGuard_doPost.js`)

Pengguna membuat Spreadsheet baru khusus Seller Guard, membuka **Extensions > Apps Script**, dan menyalin kode berikut:

```javascript
/**
 * SEITH-WARDEN: Seller Payout & PPh 22 Guard Audit Trail Webhook
 * Keamanan: Validasi token parameter & pencatatan baris transaksi audit
 */
function doPost(e) {
  try {
    var expectedToken = "SEITH_SELLER_2026"; // Diselaraskan dengan SELLER_GUARD_TOKEN di .env
    var incomingToken = e.parameter.token;

    if (!incomingToken || incomingToken !== expectedToken) {
      return ContentService.createTextOutput(JSON.stringify({
        status: "error",
        message: "Unauthorized: Invalid or missing authentication token"
      })).setMimeType(ContentService.MimeType.JSON);
    }

    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);

    // Inisialisasi Header jika spreadsheet baru/kosong
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        "Timestamp", "SellerRef", "Marketplace", "Finding_Type", 
        "Order_Count", "Observed_IDR", "Expected_IDR", "Delta_IDR", 
        "Status", "Input_SHA256", "Reviewer"
      ]);
    }

    // Append baris temuan audit
    var newRow = [
      data.timestamp || new Date().toISOString(),
      data.seller_ref || "ANONYMOUS",
      data.marketplace || "ALL",
      data.finding_type || "UNKNOWN",
      data.order_count || 1,
      data.observed_idr || "0",
      data.expected_idr || "0",
      data.delta_idr || "0",
      data.status || "PENDING_REVIEW",
      data.input_sha256 || "N/A",
      "Preliminary Advisory (HITL Required)"
    ];

    sheet.appendRow(newRow);

    return ContentService.createTextOutput(JSON.stringify({
      status: "ok",
      row: sheet.getLastRow(),
      finding_id: data.finding_id || null
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}
```

---

## 3. Komponen Dispatcher Python (`tools/sheets_seller_dispatcher.py`)

Komponen pengirim membaca environment lokal dengan toleransi kegagalan aman (*graceful degradation*):

```python
import os
import requests
import json
from typing import Dict, Any

def dispatch_seller_audit(finding: Dict[str, Any], input_sha256: str) -> Dict[str, Any]:
    webhook_url = os.environ.get("SELLER_GUARD_SHEETS_URL", "").strip()
    token = os.environ.get("SELLER_GUARD_TOKEN", "SEITH_SELLER_2026").strip()

    # Kontrak Jujur: Jika URL tidak dikonfigurasi, laporkan SKIPPED
    if not webhook_url:
        return {"status": "SKIPPED", "detail": "SELLER_GUARD_SHEETS_URL tidak disetel. Audit trail lokal tetap aman."}

    # Sematkan token query parameter
    delimiter = "&" if "?" in webhook_url else "?"
    target_url = f"{webhook_url}{delimiter}token={token}"

    payload = {
        "timestamp": finding.get("timestamp"),
        "seller_ref": finding.get("seller_ref"),
        "marketplace": finding.get("marketplace"),
        "finding_type": finding.get("type"),
        "order_count": len(finding.get("order_ids", [])),
        "observed_idr": str(finding.get("observed_idr", "0")),
        "expected_idr": str(finding.get("expected_idr", "0")),
        "delta_idr": str(finding.get("delta_idr", "0")),
        "status": "FLAGGED" if Decimal(str(finding.get("delta_idr", "0"))) > 0 else "COMPLIANT",
        "input_sha256": input_sha256
    }

    try:
        # Wajib allow_redirects=True untuk menangani redirect HTTP 302 Google Apps Script
        resp = requests.post(target_url, json=payload, timeout=10, allow_redirects=True)
        if resp.status_code == 200:
            return {"status": "LIVE", "response": resp.json()}
        elif resp.status_code in (401, 403):
            return {"status": "FAILED", "detail": f"Autentikasi token ditolak (HTTP {resp.status_code})"}
        else:
            return {"status": "FAILED", "detail": f"HTTP Error {resp.status_code}: {resp.text[:100]}"}
    except Exception as exc:
        return {"status": "FAILED", "detail": f"Koneksi gagal: {str(exc)}"}
```

---

## 4. Panduan Operasional Pengguna (Redeploy "New version")
1. Buat Google Sheet baru dengan nama: `SEITH-WARDEN: Seller PPh 22 Audit Log`.
2. Tempel kode di Apps Script editor.
3. Klik tombol biru **Deploy > Manage deployments > Edit > New version**.
4. Set permission: **Execute as: Me**, **Who has access: Anyone**.
5. Salin Web App URL dan letakkan di file `.env` root:
   ```env
   SELLER_GUARD_SHEETS_URL=https://script.google.com/macros/s/AKfy.../exec
   SELLER_GUARD_TOKEN=SEITH_SELLER_2026
   ```

---

## 5. Gate Verifikasi Tahap 5
1. Uji kondisi `SELLER_GUARD_SHEETS_URL=""` $\rightarrow$ Fungsi mengembalikan `{"status": "SKIPPED"}` (tanpa crash, no fake LIVE).
2. Uji kondisi URL disetel $\rightarrow$ Baris baru nyata muncul di Google Sheet dengan kolom `SellerRef` ter-masking dan `Delta_IDR` terhitung benar.
