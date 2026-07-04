from app.services.api_job_service import DEFAULT_RATE_LIMITS


def test_default_rate_limits_include_target_channels():
    expected_channels = {
        "smartstore",
        "gmarket",
        "auction",
        "elevenstreet",
        "toss_shopping",
        "coupang",
        "lotteon",
        "supplier",
    }

    assert expected_channels.issubset(DEFAULT_RATE_LIMITS.keys())


def test_default_rate_limits_are_positive():
    for limit in DEFAULT_RATE_LIMITS.values():
        assert limit["max_per_minute"] > 0
        assert limit["min_interval_seconds"] > 0
