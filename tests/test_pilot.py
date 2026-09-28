import json
from pathlib import Path

from comic_pipeline.contracts import validate_project, validate_shot

PILOT = Path(__file__).parents[1] / "pilots" / "through-time-revenge"


def test_pilot_project_and_all_shots_are_contract_valid():
    validate_project(json.loads((PILOT / "project.json").read_text(encoding="utf-8")))
    shots = json.loads((PILOT / "storyboard" / "shots.json").read_text(encoding="utf-8"))
    assert len(shots) == 10
    for shot in shots:
        validate_shot(shot)


def test_pilot_duration_is_between_30_and_45_seconds():
    shots = json.loads((PILOT / "storyboard" / "shots.json").read_text(encoding="utf-8"))
    assert 30 <= sum(shot["duration_s"] for shot in shots) <= 45


def test_pilot_ids_are_unique_and_every_shot_has_one_transition():
    shots = json.loads((PILOT / "storyboard" / "shots.json").read_text(encoding="utf-8"))
    ids = [shot["shot_id"] for shot in shots]
    assert len(ids) == len(set(ids))
    assert all(isinstance(shot["primary_transition"], str) and shot["primary_transition"].strip() for shot in shots)


def test_pilot_uses_lovart_only_for_image_and_video():
    project = json.loads((PILOT / "project.json").read_text(encoding="utf-8"))
    assert project["providers"] == {"image": "lovart", "video": "lovart"}
