from app.services.product_cleaner import clean_product_name


def test_clean_product_name_removes_free_shipping_token() -> None:
    result = clean_product_name("[무료배송] 데일리 티셔츠")
    assert result.cleaned_name == "데일리 티셔츠"


def test_clean_product_name_removes_wholesale_token_and_spaces() -> None:
    result = clean_product_name("도매특가   텀블러")
    assert result.cleaned_name == "텀블러"


def test_clean_product_name_truncates_long_name() -> None:
    result = clean_product_name("가" * 120, max_length=100)
    assert len(result.cleaned_name) == 100


def test_clean_product_name_marks_forbidden_word_review() -> None:
    result = clean_product_name("가품 키워드 검수 필요 가방")
    assert result.needs_review is True
