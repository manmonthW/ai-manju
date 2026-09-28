import json
from pathlib import Path

import pytest

from comic_pipeline.jobs import JobError, JobStore, canonical_hash


def make_job():
    return {
        "schema_version": "1.0.0",
        "job_id": "JOB-EP001-SH001-V01",
        "modality": "video",
        "provider": "lovart",
        "source_ref": "EP001-SH001",
        "prompt_ir_ref": "prompts/EP001-SH001.json",
        "reference_bindings": [],
        "parameters": {"duration_s": 4, "aspect_ratio": "9:16", "audio": False},
        "outputs": ["generations/lovart/videos/EP001-SH001-v01.mp4"],
        "overwrite": False,
        "preview_hash": "sha256:" + "0" * 64,
        "approval": {"status": "pending", "scope": "single-job", "approved_hash": "sha256:" + "0" * 64},
        "state": "draft",
    }


def test_preview_hash_is_deterministic_and_excludes_mutable_approval_state():
    job = make_job()
    first = canonical_hash(job)
    job["approval"]["status"] = "approved"
    job["state"] = "approved"
    assert canonical_hash(job) == first


def test_store_previews_then_approves_exact_hash(tmp_path: Path):
    store = JobStore(tmp_path / "jobs.jsonl")
    previewed = store.preview(make_job())
    assert previewed["state"] == "reviewed"
    assert previewed["preview_hash"].startswith("sha256:")
    approved = store.approve(previewed["job_id"], previewed["preview_hash"])
    assert approved["state"] == "approved"
    assert approved["approval"]["approved_hash"] == previewed["preview_hash"]


def test_changed_job_invalidates_existing_approval(tmp_path: Path):
    store = JobStore(tmp_path / "jobs.jsonl")
    previewed = store.preview(make_job())
    store.approve(previewed["job_id"], previewed["preview_hash"])
    changed = dict(make_job())
    changed["parameters"] = {"duration_s": 6, "aspect_ratio": "9:16", "audio": False}
    revised = store.preview(changed)
    assert revised["approval"]["status"] == "pending"
    assert revised["preview_hash"] != previewed["preview_hash"]


def test_store_refuses_queue_without_exact_approval(tmp_path: Path):
    store = JobStore(tmp_path / "jobs.jsonl")
    previewed = store.preview(make_job())
    with pytest.raises(JobError, match="approval"):
        store.queue(previewed["job_id"])


def test_submitted_job_records_provider_id_and_collects_before_failure_retry(tmp_path: Path):
    store = JobStore(tmp_path / "jobs.jsonl")
    previewed = store.preview(make_job())
    store.approve(previewed["job_id"], previewed["preview_hash"])
    store.queue(previewed["job_id"])
    submitted = store.submitted(previewed["job_id"], "lovart-task-123")
    assert submitted["provider_task_id"] == "lovart-task-123"
    with pytest.raises(JobError, match="collect"):
        store.queue(previewed["job_id"])
    collecting = store.collecting(previewed["job_id"])
    assert collecting["state"] == "collecting"


def test_collected_asset_can_be_marked_generated_then_rejected_by_qa(tmp_path: Path):
    store = JobStore(tmp_path / "jobs.jsonl")
    previewed = store.preview(make_job())
    store.approve(previewed["job_id"], previewed["preview_hash"])
    store.queue(previewed["job_id"])
    store.submitted(previewed["job_id"], "lovart-task-123")
    store.collecting(previewed["job_id"])
    generated = store.generated(previewed["job_id"], {"path": "generations/out.mp4", "sha256": "a" * 64, "credits": 8})
    assert generated["state"] == "generated"
    rejected = store.reject(previewed["job_id"], ["identity marker is on the wrong side"])
    assert rejected["state"] == "rejected"
    assert rejected["qa"]["issues"]


def test_generated_asset_can_pass_qa_then_be_accepted(tmp_path: Path):
    store = JobStore(tmp_path / "jobs.jsonl")
    previewed = store.preview(make_job())
    store.approve(previewed["job_id"], previewed["preview_hash"])
    store.queue(previewed["job_id"])
    store.submitted(previewed["job_id"], "lovart-task-123")
    store.collecting(previewed["job_id"])
    store.generated(previewed["job_id"], {"path": "generations/out.mp4", "sha256": "a" * 64, "credits": 8})

    qa_passed = store.pass_qa(previewed["job_id"], ["identity remains stable", "single ledger remains intact"])
    assert qa_passed["state"] == "qa_passed"
    assert qa_passed["qa"]["verdict"] == "pass"
    assert qa_passed["qa"]["checks"] == ["identity remains stable", "single ledger remains intact"]

    accepted = store.accept(previewed["job_id"])
    assert accepted["state"] == "accepted"
