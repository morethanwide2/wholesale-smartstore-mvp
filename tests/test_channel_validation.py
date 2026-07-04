from app.services.channel_validation import CHANNEL_REQUIRED_ATTRIBUTES, get_required_attributes


def test_channel_required_attributes_include_target_marketplaces():
    expected_channels = {
        "smartstore",
        "coupang",
        "gmarket",
        "auction",
        "elevenstreet",
        "toss_shopping",
        "lotteon",
    }

    assert expected_channels.issubset(CHANNEL_REQUIRED_ATTRIBUTES.keys())


def test_coupang_requires_notice_category():
    result = get_required_attributes("coupang")

    assert "notice_category" in result["required_attributes"]
    assert result["name_limit"] > 0
