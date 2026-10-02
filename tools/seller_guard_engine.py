import calendar
import csv
import hashlib
import hmac
import io
import os
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, List, Optional, Tuple

IDR_ROUND = Decimal("1")
PCT_ROUND = Decimal("0.01")
RATE_CAP_PPH22 = Decimal("0.005")  # 0,5%
MAX_ALLOWED_ROWS = 5000


def calculate_sha256(raw_bytes: bytes) -> str:
    return hashlib.sha256(raw_bytes).hexdigest()


def parse_decimal(value: Any, default: str = "0") -> Decimal:
    if value is None:
        return Decimal(default)
    s = str(value).strip().replace("Rp", "").replace(".", "").replace(",", ".")
    try:
        return Decimal(s)
    except Exception:
        return Decimal(default)


class ReportNormalizer:
    HEADER_MAP = {
        "order_id": "order_id",
        "no_pesanan": "order_id",
        "id_pesanan": "order_id",
        "marketplace": "marketplace",
        "nama_marketplace": "marketplace",
        "platform": "marketplace",
        "order_date": "order_date",
        "tanggal_pesanan": "order_date",
        "tgl_order": "order_date",
        "payment_received_date": "payment_received_date",
        "tanggal_pembayaran": "payment_received_date",
        "gross_invoice_value": "gross_invoice_value",
        "nilai_tagihan_bruto": "gross_invoice_value",
        "gross": "gross_invoice_value",
        "omzet": "gross_invoice_value",
        "pph22_withheld": "pph22_withheld",
        "pph22_dipungut": "pph22_withheld",
        "withheld": "pph22_withheld",
        "pph22_refunded": "pph22_refunded",
        "pph22_dikembalikan": "pph22_refunded",
        "refunded": "pph22_refunded",
        "status": "status",
        "status_pesanan": "status"
    }

    @classmethod
    def normalize_row_dict(cls, row: Dict[str, str]) -> Dict[str, str]:
        normalized = {}
        for k, v in row.items():
            clean_k = k.strip().lower().replace(" ", "_")
            target_key = cls.HEADER_MAP.get(clean_k, clean_k)
            normalized[target_key] = v.strip() if v else ""
        return normalized

    @classmethod
    def parse_csv(cls, csv_text: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], str]:
        raw_bytes = csv_text.encode("utf-8")
        input_hash = calculate_sha256(raw_bytes)
        if csv_text.startswith("\ufeff"):
            csv_text = csv_text.lstrip("\ufeff")
        first_line = ""
        for ln in csv_text.splitlines():
            if ln.strip():
                first_line = ln
                break
        clean_first = first_line.lstrip("\ufeff").strip()
        lower_first = clean_first.lower()
        is_csv_like = "," in clean_first or ";" in clean_first
        if is_csv_like and not ("order_id" in lower_first and "gross_invoice_value" in lower_first):
            raise ValueError(
                "ERROR: Header CSV tidak valid - butuh 'order_id, gross_invoice_value' "
                f"(case-insensitive, pemisah , atau ;). Header ditemukan: '{clean_first}'"
            )
        if ";" in first_line and first_line.count(";") > first_line.count(","):
            csv_text = csv_text.replace(";", ",")
        reader = csv.DictReader(io.StringIO(csv_text))
        valid_txs: List[Dict[str, Any]] = []
        data_quality_findings: List[Dict[str, Any]] = []

        row_count = 0
        for row in reader:
            row_count += 1
            if row_count > MAX_ALLOWED_ROWS:
                data_quality_findings.append({
                    "finding_id": f"DQ-TRUNCATED-{row_count}",
                    "type": "DATA_QUALITY",
                    "reason": "[TRUNCATED_AT_5000_ROWS_SECURITY_BOUNDARY]",
                    "detail": "Baris CSV melebihi 5.000 baris. Sisanya diabaikan."
                })
                break

            norm = cls.normalize_row_dict(row)
            order_id = norm.get("order_id")
            if not order_id:
                data_quality_findings.append({
                    "finding_id": f"DQ-MISSING-ID-{row_count}",
                    "type": "DATA_QUALITY",
                    "reason": f"Baris {row_count}: Kolom order_id kosong",
                    "detail": str(norm)
                })
                continue

            gross_raw = str(norm.get("gross_invoice_value", "")).strip()
            clean_gross_str = gross_raw.replace("Rp", "").replace(".", "").replace(",", ".")
            try:
                gross = Decimal(clean_gross_str)
                withheld = parse_decimal(norm.get("pph22_withheld"))
                refunded = parse_decimal(norm.get("pph22_refunded"))
                status = norm.get("status", "COMPLETED").upper()
                pay_date = norm.get("payment_received_date", norm.get("order_date", ""))

                valid_txs.append({
                    "order_id": order_id,
                    "marketplace": norm.get("marketplace", "Marketplace A"),
                    "order_date": norm.get("order_date", pay_date),
                    "payment_received_date": pay_date,
                    "gross_invoice_value": gross,
                    "pph22_withheld": withheld,
                    "pph22_refunded": refunded,
                    "status": status,
                    "product_name": norm.get("product_name", "")
                })
            except Exception as e:
                data_quality_findings.append({
                    "finding_id": f"DQ-PARSE-ERROR-{row_count}",
                    "type": "DATA_QUALITY",
                    "reason": f"Baris {row_count} ({order_id}): Parsing gagal ({str(e)})",
                    "detail": str(norm)
                })

        return valid_txs, data_quality_findings, input_hash


class ThresholdGuard:
    def __init__(self, threshold_idr: Decimal = Decimal("500000000")):
        self.threshold_idr = threshold_idr

    def evaluate_threshold(
        self,
        txs: List[Dict[str, Any]],
        other_channel_ytd_gross: Decimal
    ) -> Dict[str, Any]:
        completed_txs = [t for t in txs if t.get("status") == "COMPLETED"]
        completed_txs.sort(key=lambda x: x.get("payment_received_date", ""))

        total_tx_gross = sum((t["gross_invoice_value"] for t in completed_txs), Decimal("0"))
        cumulative_gross = total_tx_gross + other_channel_ytd_gross

        ratio = cumulative_gross / self.threshold_idr * Decimal("100")
        pct = ratio.quantize(PCT_ROUND, ROUND_HALF_UP)
        status = "AMAN"
        if pct >= Decimal("100"):
            status = "TERLAMPAUI"
        elif pct >= Decimal("80"):
            status = "MENDEKATI"

        crossed_date = None
        notify_deadline = None
        running_gross = other_channel_ytd_gross

        for t in completed_txs:
            running_gross += t["gross_invoice_value"]
            if running_gross >= self.threshold_idr and not crossed_date:
                crossed_date = t.get("payment_received_date")
                if crossed_date:
                    try:
                        dt = datetime.strptime(crossed_date, "%Y-%m-%d")
                        last_day = calendar.monthrange(dt.year, dt.month)[1]
                        notify_deadline = f"{dt.year:04d}-{dt.month:02d}-{last_day:02d}"
                    except Exception:
                        notify_deadline = None

        remaining_idr = self.threshold_idr - cumulative_gross
        if remaining_idr < Decimal("0"):
            remaining_idr = Decimal("0")

        return {
            "threshold_idr": str(self.threshold_idr),
            "cumulative_gross_idr": str(cumulative_gross),
            "total_completed_gross_idr": str(total_tx_gross),
            "pct": str(pct),
            "status": status,
            "crossed_date": crossed_date,
            "notify_deadline": notify_deadline,
            "remaining_idr": str(remaining_idr)
        }


class WithholdingAuditor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.effective_date = config.get("effective_date")
        self.suspension_window = config.get("suspension_window")
        self.threshold_idr = parse_decimal(config.get("threshold_idr", "500000000"))

    def audit_transactions(
        self,
        txs: List[Dict[str, Any]],
        profile: Dict[str, Any],
        threshold_info: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        taxpayer_type = profile.get("taxpayer_type", "OP").upper()
        statement_status = profile.get("statement_status", "NONE").upper()
        statement_date = profile.get("statement_date")
        skb_valid = bool(profile.get("skb_valid", False))
        crossed_date = threshold_info.get("crossed_date")

        total_observed = Decimal("0")
        total_expected = Decimal("0")
        potential_claim = Decimal("0")

        crossed_month_dt = None
        if crossed_date:
            try:
                crossed_month_dt = datetime.strptime(crossed_date, "%Y-%m-%d")
            except Exception:
                crossed_month_dt = None

        notified_crossing = False
        crossed_order_ids = self._find_crossed_orders(txs, threshold_info)

        for tx in txs:
            order_id = tx["order_id"]
            gross = tx["gross_invoice_value"]
            withheld = tx["pph22_withheld"]
            refunded = tx["pph22_refunded"]
            status = tx["status"]
            pay_date = tx.get("payment_received_date", "")

            if status != "COMPLETED":
                findings.append({
                    "finding_id": f"F-MANUAL-{order_id}",
                    "type": "PERLU_VERIFIKASI_MANUAL",
                    "order_ids": [order_id],
                    "reason": "Transaksi retur memerlukan verifikasi bukti potong pembetulan",
                    "confidence": "SECONDARY",
                    "needs_manual": True
                })
                continue

            total_observed += withheld

            if (
                order_id in crossed_order_ids
                and not notified_crossing
                and taxpayer_type == "OP"
                and statement_status == "UNDER_500"
            ):
                findings.append({
                    "finding_id": f"F-CROSS-{order_id}",
                    "type": "THRESHOLD_CROSSED_NOTIFY_REQUIRED",
                    "order_ids": [order_id],
                    "observed_idr": str(withheld),
                    "expected_idr": "0",
                    "delta_idr": "0",
                    "cumulative_gross_idr": threshold_info.get("cumulative_gross_idr", "0"),
                    "notify_deadline": threshold_info.get("notify_deadline"),
                    "source_ref": "R-THRESHOLD-NEXT-MONTH",
                    "confidence": "SECONDARY",
                    "needs_manual": False
                })
                notified_crossing = True

            if self._is_in_suspension(pay_date):
                if withheld > refunded:
                    delta_suspension = withheld - refunded
                    findings.append({
                        "finding_id": f"F-SUSPEND-{order_id}",
                        "type": "REFUND_PENDING",
                        "order_ids": [order_id],
                        "observed_idr": str(withheld),
                        "expected_idr": "0",
                        "delta_idr": str(delta_suspension),
                        "source_ref": "R-SUSPENSION-REFUND",
                        "confidence": "UNVERIFIED",
                        "needs_manual": False
                    })
                    potential_claim += delta_suspension
                    continue
                expected = Decimal("0")
            elif self.effective_date and pay_date and pay_date < self.effective_date:
                expected = Decimal("0")
            elif skb_valid:
                expected = Decimal("0")
            elif taxpayer_type == "BADAN":
                expected = (gross * RATE_CAP_PPH22).quantize(IDR_ROUND, ROUND_HALF_UP)
            else:
                if statement_status != "UNDER_500":
                    exp_val = (gross * RATE_CAP_PPH22).quantize(IDR_ROUND, ROUND_HALF_UP)
                    findings.append({
                        "finding_id": f"F-STMT-{order_id}",
                        "type": "STATEMENT_MISSING",
                        "order_ids": [order_id],
                        "observed_idr": str(withheld),
                        "expected_idr": str(exp_val),
                        "delta_idr": "0",
                        "source_ref": "R-RATE-CAP",
                        "confidence": "SECONDARY",
                        "needs_manual": False
                    })
                    expected = exp_val
                else:
                    expected = self._evaluate_op_simple(
                        gross=gross,
                        pay_date=pay_date,
                        statement_status=statement_status,
                        statement_date=statement_date,
                        crossed_month_dt=crossed_month_dt,
                    )

            total_expected += expected
            delta = withheld - expected

            if abs(delta) <= Decimal("1"):
                continue
            elif delta > Decimal("1"):
                findings.append({
                    "finding_id": f"F-OVER-{order_id}",
                    "type": "OVER_WITHHELD",
                    "order_ids": [order_id],
                    "observed_idr": str(withheld),
                    "expected_idr": str(expected),
                    "delta_idr": str(delta),
                    "source_ref": "R-EXEMPT-OP-500M",
                    "confidence": "SECONDARY",
                    "needs_manual": False
                })
                potential_claim += delta
            else:  # delta < -1
                findings.append({
                    "finding_id": f"F-UNDER-{order_id}",
                    "type": "UNDER_WITHHELD",
                    "order_ids": [order_id],
                    "observed_idr": str(withheld),
                    "expected_idr": str(expected),
                    "delta_idr": str(delta),
                    "source_ref": "R-RATE-CAP",
                    "confidence": "SECONDARY",
                    "needs_manual": False
                })

        if threshold_info.get("status") == "MENDEKATI":
            findings.append({
                "finding_id": "F-THRESHOLD-NEAR",
                "type": "THRESHOLD_NEAR",
                "pct": threshold_info.get("pct", "0"),
                "cumulative_gross_idr": threshold_info.get("cumulative_gross_idr", "0"),
                "remaining_idr": threshold_info.get("remaining_idr", "0"),
                "source_ref": "R-EXEMPT-OP-500M",
                "confidence": "SECONDARY",
                "needs_manual": False
            })

        summary = {
            "total_orders": len(txs),
            "total_observed_idr": str(total_observed),
            "total_expected_idr": str(total_expected),
            "potential_claim_idr": str(potential_claim),
            "threshold": threshold_info
        }

        return findings, summary

    def _evaluate_op_simple(
        self,
        gross: Decimal,
        pay_date: str,
        statement_status: str,
        statement_date: Optional[str],
        crossed_month_dt: Optional[datetime],
    ) -> Decimal:
        if statement_status != "UNDER_500":
            return (gross * RATE_CAP_PPH22).quantize(IDR_ROUND, ROUND_HALF_UP)
        if not statement_date or statement_date > pay_date:
            return (gross * RATE_CAP_PPH22).quantize(IDR_ROUND, ROUND_HALF_UP)
        is_after_crossed_month = False
        if crossed_month_dt and pay_date:
            try:
                pay_dt = datetime.strptime(pay_date, "%Y-%m-%d")
                if (pay_dt.year > crossed_month_dt.year) or (
                    pay_dt.year == crossed_month_dt.year and pay_dt.month > crossed_month_dt.month
                ):
                    is_after_crossed_month = True
            except Exception:
                is_after_crossed_month = False
        if is_after_crossed_month:
            return (gross * RATE_CAP_PPH22).quantize(IDR_ROUND, ROUND_HALF_UP)
        return Decimal("0")

    def _find_crossed_orders(
        self, txs: List[Dict[str, Any]], threshold_info: Dict[str, Any]
    ) -> List[str]:
        crossed_date = threshold_info.get("crossed_date")
        if not crossed_date or threshold_info.get("status") != "TERLAMPAUI":
            return []
        sorted_txs = sorted(
            [t for t in txs if t.get("status") == "COMPLETED"],
            key=lambda x: (x.get("payment_received_date", ""), x.get("order_id", "")),
        )
        candidates = [
            t["order_id"] for t in sorted_txs if t.get("payment_received_date") == crossed_date
        ]
        return [sorted(candidates)[0]] if candidates else []

    def _is_in_suspension(self, pay_date: str) -> bool:
        if not self.suspension_window or not pay_date:
            return False
        start, end = self.suspension_window
        return start <= pay_date <= end


def _derive_seller_ref(nik: str) -> str:
    key = os.environ.get("SELLER_REF_KEY", "")
    if not key:
        raise ValueError(
            "SELLER_REF_KEY tidak disetel (fail-closed). "
            "Set Global Variable Langflow SELLER_REF_KEY."
        )
    return hmac.new(key.encode(), nik.encode(), hashlib.sha256).hexdigest()[:12]


def audit_seller_payout(
    csv_text: str,
    profile_dict: Dict[str, Any],
    config_dict: Dict[str, Any]
) -> Dict[str, Any]:
    txs, dq_findings, input_hash = ReportNormalizer.parse_csv(csv_text)
    threshold_idr = parse_decimal(config_dict.get("threshold_idr", "500000000"))
    guard = ThresholdGuard(threshold_idr=threshold_idr)

    other_gross = parse_decimal(profile_dict.get("other_channel_ytd_gross", "0"))
    threshold_info = guard.evaluate_threshold(txs, other_gross)

    auditor = WithholdingAuditor(config_dict)
    rule_findings, summary = auditor.audit_transactions(txs, profile_dict, threshold_info)

    all_findings = dq_findings + rule_findings
    summary["findings_count"] = len(all_findings)

    seller_ref = _derive_seller_ref(str(profile_dict.get("nik", "ANON")))

    return {
        "status": "ok",
        "seller_ref": seller_ref,
        "input_sha256": input_hash,
        "config_status": config_dict.get("status", "UNVERIFIED"),
        "rules_verified_at": config_dict.get("verified_at"),
        "summary": summary,
        "findings": all_findings,
        "human_review_required": True,
        "disclaimer": "Laporan Preliminary Advisory. Verifikasi via Coretax DJP."
    }
