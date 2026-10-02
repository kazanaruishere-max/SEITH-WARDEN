import csv
import io
import json
import os
import sys
import unittest
from decimal import Decimal
from pathlib import Path

os.environ.setdefault("SELLER_REF_KEY", "test-key-for-unit")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.seller_guard_engine import (  # noqa: E402
    ReportNormalizer,
    audit_seller_payout,
    calculate_sha256,
    parse_decimal,
)
from tools.seller_guard_validator import (  # noqa: E402
    NumericConsistencyValidator,
    inject_evidence_table,
)
from tools.sheets_seller_dispatcher import (  # noqa: E402
    dispatch_seller_audit,
)


class TestSellerGuardEngine(unittest.TestCase):
    def test_sha256_determinism(self):
        data = b"order_id,gross\nORD-001,100000"
        h1 = calculate_sha256(data)
        h2 = calculate_sha256(data)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)

    def test_decimal_parsing_and_no_float(self):
        d1 = parse_decimal("Rp 1.500.000,50")
        self.assertIsInstance(d1, Decimal)
        self.assertEqual(d1, Decimal("1500000.50"))

        d2 = parse_decimal(None)
        self.assertEqual(d2, Decimal("0"))

    def test_normalizer_truncation_marker(self):
        header = (
            "order_id,marketplace,order_date,payment_received_date,"
            "gross_invoice_value,pph22_withheld,pph22_refunded,status\n"
        )
        rows = [
            f"ORD-{i},Marketplace A,2026-11-01,2026-11-02,10000,0,0,COMPLETED\n"
            for i in range(5005)
        ]
        csv_text = header + "".join(rows)

        txs, dq, _ = ReportNormalizer.parse_csv(csv_text)
        self.assertEqual(len(txs), 5000)
        self.assertTrue(
            any(d.get("reason") == "[TRUNCATED_AT_5000_ROWS_SECURITY_BOUNDARY]" for d in dq)
        )

    def test_oracle_cases_t01_to_t07(self):
        expected_path = ROOT / "tests" / "expected_seller_guard.json"
        config_fixture_path = ROOT / "tests" / "fixtures" / "config_test.json"

        with open(expected_path, "r", encoding="utf-8") as f:
            expected_data = json.load(f)["cases"]
        with open(config_fixture_path, "r", encoding="utf-8") as f:
            configs = json.load(f)

        for case_id, case in expected_data.items():
            scenario_key = case["scenario"]
            cfg = configs[scenario_key]
            prof = case["profile"]
            tx = case["transaction"]

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=list(tx.keys()))
            writer.writeheader()
            writer.writerow(tx)
            csv_text = output.getvalue()

            result = audit_seller_payout(csv_text, prof, cfg)
            expected_findings = case["expected_findings"]

            if not expected_findings:
                rule_findings = [f for f in result["findings"] if f["type"] != "DATA_QUALITY"]
                self.assertEqual(len(rule_findings), 0, f"Case {case_id} expected COMPLIANT")
            else:
                for exp in expected_findings:
                    match = next((f for f in result["findings"] if f["type"] == exp["type"]), None)
                    self.assertIsNotNone(match, f"Case {case_id}: missing expected {exp['type']}")
                    if "delta_idr" in exp:
                        self.assertEqual(match["delta_idr"], exp["delta_idr"])
                    if "observed_idr" in exp:
                        self.assertEqual(match["observed_idr"], exp["observed_idr"])
                    if "expected_idr" in exp:
                        self.assertEqual(match["expected_idr"], exp["expected_idr"])
                    if "notify_deadline" in exp:
                        self.assertEqual(match["notify_deadline"], exp["notify_deadline"])
                    if "pct" in exp:
                        self.assertEqual(Decimal(match["pct"]), Decimal(exp["pct"]))

    def test_full_dummy_dataset(self):
        csv_path = ROOT / "data" / "sop_dummy" / "sales_export_dummy.csv"
        prof_path = ROOT / "data" / "sop_dummy" / "seller_profile_dummy.json"
        cfg_path = ROOT / "tests" / "fixtures" / "config_demo.json"
        exp_path = ROOT / "tests" / "expected_seller_guard.json"

        csv_text = csv_path.read_text(encoding="utf-8")
        profile = json.loads(prof_path.read_text(encoding="utf-8"))
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        expected = json.loads(exp_path.read_text(encoding="utf-8"))["dataset_66_rows"]

        result = audit_seller_payout(csv_text, profile, cfg)

        self.assertEqual(result["input_sha256"], expected["metadata"]["input_sha256"])
        exp_summary = expected["summary"]
        res_sum = result["summary"]
        self.assertEqual(res_sum["total_orders"], exp_summary["total_orders"])
        self.assertEqual(res_sum["total_observed_idr"], exp_summary["total_observed_idr"])
        self.assertEqual(res_sum["total_expected_idr"], exp_summary["total_expected_idr"])
        self.assertEqual(res_sum["potential_claim_idr"], exp_summary["potential_claim_idr"])

        res_th = res_sum["threshold"]
        exp_th = exp_summary["threshold"]
        self.assertEqual(res_th["status"], exp_th["status"])
        self.assertEqual(res_th["crossed_date"], exp_th["crossed_date"])
        self.assertEqual(res_th["notify_deadline"], exp_th["notify_deadline"])

        counts = {}
        for f in result["findings"]:
            t = f["type"]
            counts[t] = counts.get(t, 0) + 1

        self.assertEqual(counts, expected["expected_findings_summary"])

    def test_numeric_consistency_validator(self):
        findings = [{
            "finding_id": "F001",
            "observed_idr": "50000",
            "expected_idr": "0",
            "delta_idr": "50000"
        }]
        validator = NumericConsistencyValidator(findings)

        # Valid text with exact numbers
        valid_text = "Terdapat pemotongan Rp 50000 yang seharusnya 0 sehingga selisih 50000."
        res = validator.validate_and_sanitize("F001", valid_text, "Template fallback")
        self.assertEqual(res, valid_text)

        # Hallucinated text with fake penalty Rp 1.500.000
        hallucinated_text = "Anda terkena denda tambahan 1500000 rupiah."
        res_hal = validator.validate_and_sanitize("F001", hallucinated_text, "Template fallback")
        self.assertIn("EXPLANATION_FALLBACK", res_hal)

    def test_inject_evidence_table(self):
        template = "Mohon proses pengembalian:\\n{{EVIDENCE_TABLE}}\\nTerima kasih."
        orders = [{
            "order_id": "ORD-001",
            "payment_date": "2026-11-05",
            "gross": 10000000,
            "withheld": 50000,
            "expected": 0,
            "delta": 50000
        }]
        result = inject_evidence_table(template, orders)
        self.assertIn("ORD-001", result)
        self.assertIn("Rp 50,000", result)
        self.assertNotIn("{{EVIDENCE_TABLE}}", result)

    def test_dispatch_seller_audit_skipped(self):
        finding = {
            "type": "OVER_WITHHELD",
            "order_ids": ["ORD-001"],
            "observed_idr": "50000",
            "expected_idr": "0",
            "delta_idr": "50000"
        }
        res = dispatch_seller_audit(finding, "test_hash_123")
        self.assertEqual(res["status"], "SKIPPED")
        self.assertIn("SELLER_GUARD_SHEETS_URL", res["detail"])


if __name__ == "__main__":
    unittest.main()
