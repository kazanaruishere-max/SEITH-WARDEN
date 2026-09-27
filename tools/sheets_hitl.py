

def generate_log(clause_id: str, risk: str, text: str) -> dict:
    sheets_ok = bool(text)
    webhook = "sent" if risk == "HIGH" and sheets_ok else "skipped"
    sheets = "ok" if sheets_ok else "failed"
    return {"sheets_status": sheets, "webhook_status": webhook, "clause_id": clause_id}


def hitl_readback(reviewer: str) -> str:
    return "re-route" if reviewer.strip().upper() == "REJECT" else "approved"


def cost_avoided(docs: int) -> int:
    return int(docs * 35_000_000 * 0.85)


def router_persona(query: str) -> str:
    q = query.lower()
    return "draft_remediation" if "draft" in q or "perbaikan" in q else "audit_severity"


if __name__ == "__main__":
    assert generate_log("1", "HIGH", "x")["webhook_status"] == "sent"
    assert generate_log("1", "LOW", "x")["webhook_status"] == "skipped"
    assert hitl_readback("REJECT") == "re-route"
    assert hitl_readback("APPROVE") == "approved"
    assert cost_avoided(12) == 357_000_000
    assert router_persona("audit Pasal 1 0,25%") == "audit_severity"
    assert router_persona("draft perbaikan Pasal 1") == "draft_remediation"
    print("ok")
