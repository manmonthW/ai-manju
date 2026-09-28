from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from .contracts import ContractError, validate_job, validate_transition


class JobError(ValueError):
    pass


def _preview_payload(job: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(job)
    payload.pop("preview_hash", None)
    payload.pop("state", None)
    payload.pop("provider_task_id", None)
    payload.pop("events", None)
    payload.pop("approval", None)
    return payload


def canonical_hash(job: dict[str, Any]) -> str:
    encoded = json.dumps(_preview_payload(job), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


class JobStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _events(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _append(self, job: dict[str, Any], event: str) -> dict[str, Any]:
        record = {"event": event, "job": copy.deepcopy(job)}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return copy.deepcopy(job)

    def get(self, job_id: str) -> dict[str, Any]:
        for record in reversed(self._events()):
            if record["job"]["job_id"] == job_id:
                return record["job"]
        raise JobError(f"unknown job: {job_id}")

    def preview(self, input_job: dict[str, Any]) -> dict[str, Any]:
        job = copy.deepcopy(input_job)
        digest = canonical_hash(job)
        job["preview_hash"] = digest
        job["approval"] = {"status": "pending", "scope": job.get("approval", {}).get("scope", "single-job"), "approved_hash": digest}
        job["state"] = "reviewed"
        try:
            validate_job(job)
        except ContractError as exc:
            raise JobError(str(exc)) from exc
        return self._append(job, "previewed")

    def approve(self, job_id: str, approved_hash: str) -> dict[str, Any]:
        job = self.get(job_id)
        if job["state"] != "reviewed" or approved_hash != job["preview_hash"]:
            raise JobError("approval hash does not match the current reviewed preview")
        validate_transition("reviewed", "approved")
        job["approval"]["status"] = "approved"
        job["approval"]["approved_hash"] = approved_hash
        job["state"] = "approved"
        validate_job(job, require_approved=True)
        return self._append(job, "approved")

    def queue(self, job_id: str) -> dict[str, Any]:
        job = self.get(job_id)
        if job["state"] == "submitted":
            raise JobError("submitted jobs must collect before retry")
        if job["approval"]["status"] != "approved" or job["approval"]["approved_hash"] != job["preview_hash"]:
            raise JobError("exact approval is required before queueing")
        try:
            validate_transition(job["state"], "queued")
        except ContractError as exc:
            raise JobError(str(exc)) from exc
        job["approval"]["status"] = "consumed"
        job["state"] = "queued"
        return self._append(job, "queued")

    def submitted(self, job_id: str, provider_task_id: str) -> dict[str, Any]:
        job = self.get(job_id)
        try:
            validate_transition(job["state"], "submitted")
        except ContractError as exc:
            raise JobError(str(exc)) from exc
        if not provider_task_id.strip():
            raise JobError("provider_task_id is required")
        job["provider_task_id"] = provider_task_id
        job["state"] = "submitted"
        return self._append(job, "submitted")

    def collecting(self, job_id: str) -> dict[str, Any]:
        job = self.get(job_id)
        try:
            validate_transition(job["state"], "collecting")
        except ContractError as exc:
            raise JobError(str(exc)) from exc
        job["state"] = "collecting"
        return self._append(job, "collecting")

    def generated(self, job_id: str, result: dict[str, Any]) -> dict[str, Any]:
        job = self.get(job_id)
        try:
            validate_transition(job["state"], "generated")
        except ContractError as exc:
            raise JobError(str(exc)) from exc
        required = {"path", "sha256", "credits"}
        if not required.issubset(result):
            raise JobError("generated result requires path, sha256, and credits")
        job["result"] = copy.deepcopy(result)
        job["state"] = "generated"
        return self._append(job, "generated")

    def pass_qa(self, job_id: str, checks: list[str]) -> dict[str, Any]:
        job = self.get(job_id)
        try:
            validate_transition(job["state"], "qa_passed")
        except ContractError as exc:
            raise JobError(str(exc)) from exc
        if not checks or not all(isinstance(check, str) and check.strip() for check in checks):
            raise JobError("QA pass requires at least one concrete check")
        job["qa"] = {"verdict": "pass", "checks": list(checks)}
        job["state"] = "qa_passed"
        return self._append(job, "qa_passed")

    def accept(self, job_id: str) -> dict[str, Any]:
        job = self.get(job_id)
        try:
            validate_transition(job["state"], "accepted")
        except ContractError as exc:
            raise JobError(str(exc)) from exc
        job["state"] = "accepted"
        return self._append(job, "accepted")

    def reject(self, job_id: str, issues: list[str]) -> dict[str, Any]:
        job = self.get(job_id)
        try:
            validate_transition(job["state"], "rejected")
        except ContractError as exc:
            raise JobError(str(exc)) from exc
        if not issues or not all(isinstance(issue, str) and issue.strip() for issue in issues):
            raise JobError("rejection requires at least one concrete QA issue")
        job["qa"] = {"verdict": "block", "issues": list(issues)}
        job["state"] = "rejected"
        return self._append(job, "rejected")
