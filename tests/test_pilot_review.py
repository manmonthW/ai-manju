from comic_pipeline.pilot_review import review_pilot


def test_review_flags_unproven_popularity_claim_and_allows_original_hook_driven_pilot():
    report = review_pilot(
        title="我在朝堂直播抄家",
        declared_claim="最火的穿越爽剧",
        duration_s=42,
        character_count=2,
        location_count=1,
        shot_count=10,
        has_cold_open=True,
        has_reversal=True,
        has_cliffhanger=True,
    )
    assert report["creative_fit"] == "pass"
    assert report["market_claim"] == "unverified"
    assert "不能声称" in report["notes"][0]


def test_review_blocks_overlong_or_unbounded_pilot():
    report = review_pilot(
        title="test",
        declared_claim="pilot",
        duration_s=60,
        character_count=7,
        location_count=5,
        shot_count=25,
        has_cold_open=False,
        has_reversal=False,
        has_cliffhanger=False,
    )
    assert report["creative_fit"] == "block"
    assert report["issues"]
