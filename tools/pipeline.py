import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ceiling_verify import verify_ceiling
from pii_sanitizer import sanitize_sop_text


def audit_clause(text: str, param: str = "daily_rate_percent") -> dict:
    clean = sanitize_sop_text(text)
    r = verify_ceiling(clean, param)
    if r["status"] == "PERLU_VERIFIKASI_MANUAL":
        return {"risk": "PERLU_VERIFIKASI_MANUAL", **r}
    if r.get("violation"):
        return {"risk": "HIGH", **r}
    if "SEOJK" in text and not r.get("violation"):
        return {"risk": "MEDIUM", **r}
    if r["status"] == "COMPLIANT":
        return {"risk": "COMPLIANT", **r}
    return {"risk": "LOW", **r}


def run_scenarios() -> list:
    cases = [
        ("Bunga 0,25%/hari 19/SEOJK.05/2023", "HIGH"),
        ("Bunga 0,30% + denda cap 150%", "HIGH"),
        ("Lock Cap 120% pokok", "HIGH"),
        ("Rujuk 06/SEOJK.07/2022 tanpa angka", "PERLU_VERIFIKASI_MANUAL"),
        ("bunga kompetitif", "PERLU_VERIFIKASI_MANUAL"),
        ("19/SEOJK.05/2023 bunga 0,08%/hari", "MEDIUM"),
        ("typo PADK minor", "PERLU_VERIFIKASI_MANUAL"),
        ("istilah minor", "PERLU_VERIFIKASI_MANUAL"),
        ("PADK 12/PADK.05/2026 bunga 0,08% cap 90%", "COMPLIANT"),
        ("bunga 0,10%/hari cap 100%", "COMPLIANT"),
    ]
    out = []
    for txt, exp in cases:
        is_lock = txt.startswith("Lock Cap")
        param = "lock_cap_percent" if is_lock else "daily_rate_percent"
        res = audit_clause(txt, param)
        low_ok = res["risk"] in ("LOW", "PERLU_VERIFIKASI_MANUAL")
        ok = res["risk"] == exp or (exp == "LOW" and low_ok)
        out.append((txt[:24], res["risk"], exp, ok))
    return out


if __name__ == "__main__":
    for t, got, exp, ok in run_scenarios():
        assert ok, f"{t} got {got} exp {exp}"
        print(f"{t} -> {got} ({'ok' if ok else 'FAIL'})")
    print("pipeline ok")
