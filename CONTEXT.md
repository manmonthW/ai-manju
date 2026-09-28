# AI Comic Drama Domain

This context defines the canonical language and ownership boundaries for the local AI comic-drama production pipeline.

## Language

**Project**:
The production container for one drama series or bounded pilot, with one format profile, rights context, provider policy, and delivery target.

**Episode**:
A timed narrative unit within a Project. Creative prose lives in its screenplay Markdown; its stable metadata and validation results are structured records.

**Scene**:
A dramatic unit with a stable `EP###-SC###` identity, location/time state, participants, objective, opposition, turn, and exit state.

**Shot**:
A stable `EP###-SH###` editorial unit with one story purpose, a start boundary, one primary transition, and an end boundary. Reordering preserves identity; splitting or merging creates successor IDs.
_Avoid_: Prompt, generated clip

**Asset**:
A versioned identity, location, prop, look, or state record consumed by Shots. An Asset record is not proof that media exists.

**Reference**:
A readable media file with provenance and hash. Each binding declares what it may control and must not control.
_Avoid_: Prompt entry, planned upload

**Planned Reference**:
A declared external attachment slot that does not yet prove a readable local asset exists.

**Prompt IR**:
A provider-neutral, structured statement of scene, subjects, ordered actions, camera, sound, references, constraints, and output needs. Model renderers derive provider-specific prompts from it.

**Generation Job**:
A bounded, single-modality request with immutable preview content, declared outputs, approval hash, state, and provider task identity. A Job is not a generated asset.

**Approval**:
Explicit authorization tied to the exact preview hash of one bounded paid Job or batch. Any material input change invalidates it.

**Submission**:
Evidence that Lovart accepted a Job. After Submission, recovery must attempt collection before any retry to avoid duplicate spend.

**Generated Asset**:
A retrieved file that passes structural media verification. It has not necessarily passed creative QA.

**Accepted Asset**:
A Generated Asset that passed the required technical, continuity, editorial, and project-specific review gates.

**Continuity Lock**:
An immutable or shot-bounded constraint on identity, wardrobe, prop state, location geometry, screen direction, or action handoff.

**Inferred Attribute**:
A model-created detail unsupported by canonical sources. It remains draft until explicitly approved and must not silently become canonical.

## Ownership

- Screenplay owns dramatic intent and dialogue.
- Asset records own canonical identity and mutable state.
- Storyboard owns Shot identity, coverage, and boundaries.
- Director advice may propose visual strategy but cannot rewrite Shot identity or continuity.
- Prompt renderers own provider syntax, not story meaning.
- Lovart owns generation execution, not project state or acceptance.
- QA owns acceptance verdicts; technical success never implies creative approval.
