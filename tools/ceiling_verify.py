import json
import re
from pathlib import Path


def _load_graph() -> dict:
    p = (Path(__file__).resolve().parent.parent / "data" / "kb" / "padk_graph.json").resolve()
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"pasal12": {"ayat1": {"ceiling": 0.1}, "ayat3": {"ceiling": 100}}}


_G = _load_graph()


def extract_percent(text: str) -> float | None:
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*%", text)
    return float(m.group(1).replace(",", ".")) if m else None


def verify_ceiling(text: str, param: str = "daily_rate_percent") -> dict:
    v = extract_percent(text)
    if v is None:
        return {"found": None, "status": "PERLU_VERIFIKASI_MANUAL"}
    key = "ayat3" if "lock" in param else "ayat1"
    default = 0.1 if "daily" in param else 100
    ceil = _G.get("pasal12", {}).get(key, {}).get("ceiling", default)
    status = "VIOLATION" if v > ceil else "COMPLIANT"
    return {"found": v, "ceiling": ceil, "violation": v > ceil, "status": status}


if __name__ == "__main__":
    assert extract_percent("Bunga 0,25%/hari") == 0.25
    a = verify_ceiling("0,25%/hari", "daily_rate_percent")
    assert a["violation"] is True
    assert verify_ceiling("0,08%/hari")["violation"] is False
    assert verify_ceiling("bunga kompetitif")["status"] == "PERLU_VERIFIKASI_MANUAL"
    b = verify_ceiling("Lock Cap 120% pokok", "lock_cap_percent")
    assert b["violation"] is True
    print("ok")
