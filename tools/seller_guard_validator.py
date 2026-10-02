import re
from typing import Any, Dict, List, Set


class NumericConsistencyValidator:
    """Memvalidasi bahwa seluruh angka/tanggal pada output LLM ada pada findings.json."""

    def __init__(self, findings: List[Dict[str, Any]]):
        self.valid_tokens = self._extract_valid_tokens(findings)

    def _extract_valid_tokens(self, findings: List[Dict[str, Any]]) -> Set[str]:
        tokens: Set[str] = set()
        for f in findings:
            for _, v in f.items():
                if isinstance(v, (int, str)):
                    # Simpan token angka, persentase, dan tanggal ISO
                    pattern = r"\b\d+(?:[\.,]\d+)?\b|\b\d{4}-\d{2}-\d{2}\b"
                    for match in re.findall(pattern, str(v)):
                        tokens.add(match.replace(",", "."))
        return tokens

    def validate_and_sanitize(
        self,
        finding_id: str,
        explanation: str,
        fallback_template: str
    ) -> str:
        # Ekstrak angka dari teks penjelasan LLM
        pattern = r"\b\d+(?:[\.,]\d+)?\b|\b\d{4}-\d{2}-\d{2}\b"
        found_in_text = re.findall(pattern, explanation)
        for token in found_in_text:
            cleaned = token.replace(",", ".")
            # Abaikan angka indeks kecil (1-3) jika konteks kalimat naratif
            try:
                val = float(cleaned)
                if cleaned not in self.valid_tokens and val > 5:
                    # Terdeteksi angka halusinasi! Aktifkan fallback deterministik
                    return f"{fallback_template} [EXPLANATION_FALLBACK: Deviasi Angka Terdeteksi]"
            except Exception:
                if cleaned not in self.valid_tokens:
                    return f"{fallback_template} [EXPLANATION_FALLBACK: Deviasi Tanggal Terdeteksi]"
        return explanation


def inject_evidence_table(body_template: str, order_details: List[Dict[str, Any]]) -> str:
    headers = (
        "| No. Pesanan | Tgl Pembayaran | Nilai Bruto | "
        "PPh 22 Dipungut | Seharusnya | Selisih |\n"
    )
    separator = "|:---|:---|:---|:---|:---|:---|\n"
    rows = []
    for o in order_details:
        order_id = o.get("order_id", "N/A")
        pay_date = o.get("payment_date", o.get("payment_received_date", "N/A"))
        gross = int(o.get("gross", o.get("gross_invoice_value", 0)))
        withheld = int(o.get("withheld", o.get("pph22_withheld", 0)))
        expected = int(o.get("expected", o.get("expected_idr", 0)))
        delta = int(o.get("delta", o.get("delta_idr", 0)))
        rows.append(
            f"| {order_id} | {pay_date} | Rp {gross:,} | "
            f"Rp {withheld:,} | Rp {expected:,} | Rp {delta:,} |\n"
        )
    table = headers + separator + "".join(rows)
    return body_template.replace("{{EVIDENCE_TABLE}}", table)
