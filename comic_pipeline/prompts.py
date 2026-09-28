from __future__ import annotations

from typing import Any


class CapabilityError(ValueError):
    pass


CAPABILITIES = {
    # Runtime values are deliberately conservative and must be refreshed from the
    # logged-in Lovart UI before paid submission.
    "seedance": {
        "modes": {"t2v", "i2v", "start_end_frame"},
        "duration_s": (3, 15),
        "resolutions": {"720p", "1080p"},
    },
    "kling": {
        "modes": {"t2v", "i2v", "start_end_frame", "motion_transfer", "camera_trajectory"},
        "duration_s": (3, 15),
        "resolutions": {"720p", "1080p"},
    },
}


def validate_capability(ir: dict[str, Any], model: str) -> bool:
    capability = CAPABILITIES.get(model)
    if capability is None:
        raise CapabilityError(f"unknown model capability profile: {model}")
    mode = ir.get("mode")
    if mode not in capability["modes"]:
        raise CapabilityError(f"{model} does not support {mode}")
    output = ir.get("output", {})
    duration = output.get("duration_s")
    minimum, maximum = capability["duration_s"]
    if not isinstance(duration, (int, float)) or not minimum <= duration <= maximum:
        raise CapabilityError(f"duration {duration!r} outside {model} range {minimum}-{maximum}s")
    resolution = output.get("resolution")
    if resolution not in capability["resolutions"]:
        raise CapabilityError(f"unsupported resolution {resolution!r} for {model}")
    return True


def render_prompt(ir: dict[str, Any], model: str) -> str:
    validate_capability(ir, model)
    output = ir["output"]
    actions = sorted(ir["actions"], key=lambda item: item["order"])
    sequence = " Then ".join(f"{item['motion']}; end with {item['endpoint']}" for item in actions)
    camera = ir.get("camera", {})
    constraints = ir.get("constraints", {})
    unchanged = ", ".join(constraints.get("unchanged_elements", [])) or "identity and environment"
    negatives = ", ".join(constraints.get("negative_prompt", []))
    if ir["mode"] in {"i2v", "start_end_frame"}:
        lead = "Animate the supplied reference image; describe motion only."
    else:
        scene = ir.get("scene", {})
        subjects = ", ".join(item.get("description", item["id"]) for item in ir.get("subjects", []))
        lead = f"Scene: {scene.get('environment', '')}. Subject: {subjects}."
    parts = [
        lead,
        f"Action: {sequence}.",
        f"Camera: {camera.get('shot_size', '')}, {camera.get('movement', 'locked')}." ,
        f"Keep unchanged: {unchanged}.",
        f"Duration: {output['duration_s']} seconds. Aspect ratio: {output['aspect_ratio']}.",
    ]
    if negatives:
        parts.append(f"Do not add: {negatives}.")
    return " ".join(parts)
