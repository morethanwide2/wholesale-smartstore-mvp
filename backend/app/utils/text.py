import re


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def remove_noise_tokens(text: str) -> str:
    cleaned = text.replace("[무료배송]", "").replace("도매특가", "")
    cleaned = re.sub(r"[^\w\s가-힣\-/]", " ", cleaned)
    return normalize_spaces(cleaned)
