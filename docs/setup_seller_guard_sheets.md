# Setup Google Sheets Audit Trail — Seller Payout & PPh 22 Guard

Dokumentasi ini menjelaskan langkah setup Google Apps Script Web App untuk menerima data audit trail kepatuhan PPh 22 Seller Marketplace (9 kolom + hash integritas SHA-256).

---

## 1. Skema Kolom Spreadsheet

Buat Google Spreadsheet baru bernama `SEITH-WARDEN: Seller PPh 22 Audit Log`.

Kolom-kolom yang otomatis dihasilkan pada baris pertama:
1. `Timestamp` (Waktu audit dilakukan)
2. `SellerRef` (Pseudonim: `sha256(NIK)[:12]`)
3. `Marketplace` (Marketplace A, B, atau C)
4. `Finding_Type` (OVER_WITHHELD, STATEMENT_MISSING, THRESHOLD_NEAR, dsb)
5. `Order_Count` (Jumlah pesanan terdampak)
6. `Observed_IDR` (PPh 22 riil dipungut)
7. `Expected_IDR` (PPh 22 seharusnya menurut aturan)
8. `Delta_IDR` (Potensi klaim pengembalian dana)
9. `Status` (FLAGGED / COMPLIANT)
10. `Input_SHA256` (Bukti kriptografis keaslian CSV)
11. `Reviewer` ("Preliminary Advisory (HITL Required)")

---

## 2. Kode Google Apps Script

Buka spreadsheet, klik **Extensions > Apps Script**, ganti seluruh kode dengan:

```javascript
function doPost(e) {
  try {
    var expectedToken = "SEITH_SELLER_2026";
    var incomingToken = e.parameter.token;

    if (!incomingToken || incomingToken !== expectedToken) {
      return ContentService.createTextOutput(JSON.stringify({
        status: "error",
        message: "Unauthorized: Invalid or missing authentication token"
      })).setMimeType(ContentService.MimeType.JSON);
    }

    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);

    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        "Timestamp", "SellerRef", "Marketplace", "Finding_Type", 
        "Order_Count", "Observed_IDR", "Expected_IDR", "Delta_IDR", 
        "Status", "Input_SHA256", "Reviewer"
      ]);
    }

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

## 3. Deployment & Konfigurasi Lingkungan

1. Klik tombol **Deploy > New deployment**.
2. Pilih jenis **Web app**.
3. Atur:
   - **Execute as:** `Me`
   - **Who has access:** `Anyone` (PENTING: Jangan pilih "Anyone with Google account").
4. Klik **Deploy** dan salin Web App URL.
5. Masukkan ke file `.env` root:
   ```env
   SELLER_GUARD_SHEETS_URL=https://script.google.com/macros/s/AKfy.../exec
   SELLER_GUARD_TOKEN=SEITH_SELLER_2026
   ```
