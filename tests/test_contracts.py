import json
from pathlib import Path

import pytest

from comic_pipeline.contracts import ContractError, validate_job, validate_project, validate_shot, validate_transition

FIXTURES = Path(__file__).parent / "fixtures"


def load(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_project_contract_accepts_minimal_valid_project():
    validate_project(load("project.valid.json"))


def test_project_contract_rejects_unknown_schema_version():
    data = load("project.valid.json")
    data["schema_version"] = "9.9.9"
    with pytest.raises(ContractError, match="schema_version"):
        validate_project(data)


def test_shot_contract_requires_stable_ids_and_single_transition():
    validate_shot(load("shot.valid.json"))
    data = load("shot.valid.json")
    data["shot_id"] = "1"
    with pytest.raises(ContractError, match="shot_id"):
        validate_shot(data)


def test_paid_job_requires_preview_hash_and_explicit_approval():
    validate_job(load("job.approved.json"))
    data = load("job.approved.json")
    data["approval"]["status"] = "pending"
    with pytest.raises(ContractError, match="approved"):
        validate_job(data, require_approved=True)


def test_job_rejects_secret_like_fields_and_absolute_outputs():
    data = load("job.approved.json")
    data["api_key"] = "forbidden"
    with pytest.raises(ContractError, match="secret-like"):
        validate_job(data)
    data = load("job.approved.json")
    data["outputs"] = ["/tmp/out.mp4"]
    with pytest.raises(ContractError, match="relative"):
        validate_job(data)


def test_submitted_job_must_collect_before_retry():
    assert validate_transition("submitted", "collecting")
    with pytest.raises(ContractError, match="collect"):
        validate_transition("submitted", "queued")
