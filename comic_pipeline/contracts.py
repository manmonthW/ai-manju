from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any

SCHEMA_VERSION = "1.0.0"
ID_PATTERNS = {
    "project_id": re.compile(r"^[A-Z][A-Z0-9-]{2,63}$"),
    "scene_id": re.compile(r"^EP\d{3}-SC\d{3}$"),
    "shot_id": re.compile(r"^EP\d{3}-SH\d{3}$"),
    "job_id": re.compile(r"^JOB-[A-Z0-9-]+$"),
}
SECRET_WORDS = ("api_key", "apikey", "token", "password", "secret", "cookie")
TRANSITIONS = {
    "draft": {"reviewed", "cancelled"},
    "reviewed": {"approved", "draft", "rejected"},
    "approved": {"queued", "draft", "cancelled"},
    "queued": {"submitted", "cancelled"},
    "submitted": {"collecting", "failed"},
    "collecting": {"generated", "failed"},
    "generated": {"qa_passed", "rejected"},
    "qa_passed": {"accepted", "rejected"},
    "accepted": {"superseded"},
    "rejected": {"draft", "superseded"},
    "failed": {"collecting", "draft", "cancelled"},
    "cancelled": set(),
    "superseded": set(),
}


class ContractError(ValueError):
    pass


def _require(data: dict[str, Any], fields: tuple[str, ...]) -> None:
    missing = [field for field in fields if field not in data]
    if missing:
        raise ContractError(f"missing required fields: {', '.join(missing)}")


def _schema(data: dict[str, Any]) -> None:
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ContractError(f"unsupported schema_version: {data.get('schema_version')!r}")


def _id(data: dict[str, Any], field: str) -> None:
    value = data.get(field)
    if not isinstance(value, str) or not ID_PATTERNS[field].fullmatch(value):
        raise ContractError(f"invalid {field}: {value!r}")


def _reject_secrets(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if any(word in normalized for word in SECRET_WORDS):
                raise ContractError(f"secret-like field is forbidden at {path}.{key}")
            _reject_secrets(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_secrets(item, f"{path}[{index}]")


def _relative_file(path: str) -> None:
    parsed = PurePosixPath(path)
    if parsed.is_absolute() or ".." in parsed.parts or path.endswith("/"):
        raise ContractError(f"output path must be a safe project-relative file: {path!r}")


def validate_project(data: dict[str, Any]) -> bool:
    _schema(data)
    _require(data, ("project_id", "title", "status", "format", "providers"))
    _id(data, "project_id")
    fmt = data["format"]
    _require(fmt, ("episode_duration_s", "aspect_ratio", "language"))
    if not isinstance(fmt["episode_duration_s"], (int, float)) or fmt["episode_duration_s"] <= 0:
        raise ContractError("episode_duration_s must be positive")
    providers = data["providers"]
    if providers.get("image") != "lovart" or providers.get("video") != "lovart":
        raise ContractError("image and video providers must be lovart")
    _reject_secrets(data)
    return True


def validate_shot(data: dict[str, Any]) -> bool:
    _schema(data)
    _require(data, ("shot_id", "scene_id", "story_purpose", "duration_s", "start_boundary", "primary_transition", "end_boundary", "camera", "references", "continuity_locks"))
    _id(data, "shot_id")
    _id(data, "scene_id")
    if not isinstance(data["duration_s"], (int, float)) or data["duration_s"] <= 0:
        raise ContractError("duration_s must be positive")
    for field in ("story_purpose", "start_boundary", "primary_transition", "end_boundary"):
        if not isinstance(data[field], str) or not data[field].strip():
            raise ContractError(f"{field} must be non-empty")
    _reject_secrets(data)
    return True


def validate_job(data: dict[str, Any], *, require_approved: bool = False) -> bool:
    _schema(data)
    _reject_secrets(data)
    _require(data, ("job_id", "modality", "provider", "source_ref", "prompt_ir_ref", "reference_bindings", "parameters", "outputs", "overwrite", "preview_hash", "approval", "state"))
    _id(data, "job_id")
    if data["provider"] != "lovart":
        raise ContractError("provider must be lovart")
    if data["modality"] not in {"image", "video"}:
        raise ContractError("modality must be image or video")
    outputs = data["outputs"]
    if not isinstance(outputs, list) or not 1 <= len(outputs) <= 16 or len(outputs) != len(set(outputs)):
        raise ContractError("outputs must contain 1-16 unique paths")
    for output in outputs:
        if not isinstance(output, str):
            raise ContractError("output path must be a string")
        _relative_file(output)
    approval = data["approval"]
    _require(approval, ("status", "scope", "approved_hash"))
    if approval["approved_hash"] != data["preview_hash"]:
        raise ContractError("approved_hash must match preview_hash")
    if require_approved and approval["status"] != "approved":
        raise ContractError("paid job must be explicitly approved")
    return True


def validate_transition(current: str, target: str) -> bool:
    if current not in TRANSITIONS or target not in TRANSITIONS:
        raise ContractError("unknown state")
    if target not in TRANSITIONS[current]:
        suffix = "; submitted jobs must collect before retry" if current == "submitted" else ""
        raise ContractError(f"invalid transition {current!r} -> {target!r}{suffix}")
    return True
