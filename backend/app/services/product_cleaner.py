from dataclasses import dataclass

from app.utils.text import remove_noise_tokens


FORBIDDEN_WORDS = ["의료기기", "수입금지", "짝퉁", "가품"]


@dataclass(frozen=True)
class CleanResult:
    cleaned_name: str
    needs_review: bool
    review_reason: str | None = None


def clean_product_name(name: str, max_length: int = 100) -> CleanResult:
    cleaned = remove_noise_tokens(name)
    needs_review = False
    review_reason = None

    for word in FORBIDDEN_WORDS:
        if word in cleaned:
            needs_review = True
            review_reason = f"금지어 포함: {word}"
            break

    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip()

    return CleanResult(cleaned_name=cleaned, needs_review=needs_review, review_reason=review_reason)
