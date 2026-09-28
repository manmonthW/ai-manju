from comic_pipeline.prompts import CapabilityError, render_prompt, validate_capability


def prompt_ir(mode="i2v"):
    return {
        "schema_version": "1.0.0",
        "mode": mode,
        "scene": {"environment": "ancient imperial court", "lighting": "warm dawn"},
        "subjects": [{"id": "CH001", "description": "young strategist in plain dark robe"}],
        "actions": [{"order": 1, "subject_id": "CH001", "motion": "raises the sealed grain ledger", "endpoint": "holds it still at chest height"}],
        "camera": {"shot_size": "medium", "movement": "slow push-in"},
        "audio": {"enabled": False},
        "style": {"visual_style": "premium Chinese animated drama"},
        "constraints": {"unchanged_elements": ["face", "robe", "ledger seal"], "negative_prompt": ["text", "extra fingers"]},
        "references": [{"role": "start_frame", "path": "keyframes/EP001-SH001-start.png"}],
        "output": {"duration_s": 4, "aspect_ratio": "9:16", "resolution": "720p"},
    }


def test_seedance_i2v_renderer_describes_motion_and_preservation():
    rendered = render_prompt(prompt_ir(), "seedance")
    assert "raises the sealed grain ledger" in rendered
    assert "unchanged" in rendered.lower()
    assert "4 seconds" in rendered


def test_renderer_rejects_unsupported_motion_transfer():
    ir = prompt_ir("motion_transfer")
    try:
        validate_capability(ir, "seedance")
    except CapabilityError as exc:
        assert "motion_transfer" in str(exc)
    else:
        raise AssertionError("unsupported capability accepted")


def test_capability_rejects_duration_outside_live_registry():
    ir = prompt_ir()
    ir["output"]["duration_s"] = 99
    try:
        validate_capability(ir, "seedance")
    except CapabilityError as exc:
        assert "duration" in str(exc)
    else:
        raise AssertionError("invalid duration accepted")
