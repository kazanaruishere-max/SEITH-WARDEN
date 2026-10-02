import json
import os
import urllib.error
import urllib.request
from decimal import Decimal
from typing import Any, Dict


def dispatch_seller_audit(finding: Dict[str, Any], input_sha256: str) -> Dict[str, Any]:
    webhook_url = os.environ.get("SELLER_GUARD_SHEETS_URL", "").strip()
    token = os.environ.get("SELLER_GUARD_TOKEN", "SEITH_SELLER_2026").strip()

    # Kontrak Jujur: Jika URL tidak dikonfigurasi, laporkan SKIPPED
    if not webhook_url:
        return {
            "status": "SKIPPED",
            "detail": "SELLER_GUARD_SHEETS_URL tidak disetel. Audit trail lokal tetap aman."
        }

    # Sematkan token query parameter
    delimiter = "&" if "?" in webhook_url else "?"
    target_url = f"{webhook_url}{delimiter}token={token}"

    delta_val = Decimal(str(finding.get("delta_idr", "0")))
    status_label = "FLAGGED" if delta_val > Decimal("0") else "COMPLIANT"

    payload = {
        "timestamp": finding.get("timestamp"),
        "seller_ref": finding.get("seller_ref", "ANONYMOUS"),
        "marketplace": finding.get("marketplace", "Marketplace A"),
        "finding_type": finding.get("type", "UNKNOWN"),
        "order_count": len(finding.get("order_ids", [])),
        "observed_idr": str(finding.get("observed_idr", "0")),
        "expected_idr": str(finding.get("expected_idr", "0")),
        "delta_idr": str(finding.get("delta_idr", "0")),
        "status": status_label,
        "input_sha256": input_sha256
    }

    try:
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            target_url,
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_body = resp.read().decode("utf-8")
            if resp.status in (200, 201):
                try:
                    res_json = json.loads(resp_body)
                    return {"status": "LIVE", "response": res_json}
                except Exception:
                    return {"status": "LIVE", "response": resp_body}
            return {
                "status": "FAILED",
                "detail": f"HTTP status {resp.status}: {resp_body[:100]}"
            }
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return {
                "status": "FAILED",
                "detail": f"Autentikasi token ditolak (HTTP {e.code})"
            }
        return {"status": "FAILED", "detail": f"HTTP Error {e.code}: {e.reason}"}
    except Exception as exc:
        return {"status": "FAILED", "detail": f"Koneksi gagal: {str(exc)}"}
