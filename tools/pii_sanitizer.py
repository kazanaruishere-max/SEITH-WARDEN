import re


def sanitize_sop_text(t: str) -> str:
    t = re.sub(r'\b\d{16}\b', '[REDACTED_NIK]', t)
    t = re.sub(r'\b(?:\d[ -]*?){13,19}\b', '[REDACTED_ACCOUNT_NO]', t)
    t = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', t)
    return t

if __name__ == "__main__":
    assert "[REDACTED_NIK]" in sanitize_sop_text("NIK 1234567890123456")
    assert "[REDACTED_EMAIL]" in sanitize_sop_text("a@b.co")
    assert "[REDACTED_ACCOUNT_NO]" in sanitize_sop_text("4111 1111 1111 1111")
    assert sanitize_sop_text("bunga 0,1%/hari") == "bunga 0,1%/hari"
    print("ok")
