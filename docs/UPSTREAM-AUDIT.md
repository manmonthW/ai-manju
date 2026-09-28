# Upstream audit and adoption record

Pinned checkouts under `references/repos/` are analysis-only and are not installed runtime dependencies.

| Repository | Pinned SHA | License | Decision |
|---|---|---|---|
| zenstory-ai/drama-skills | `4d2ac3b95ecae79fb4e4672e4ade07c57f79d1ca` | MIT | Selectively reimplement stable IDs, shot boundaries, reference semantics, approval hashing, collection-before-retry, and separated QA. Do not install the 11-skill suite or provider adapters. |
| eternityspring/shuohao-skills | `ef4ac0c313c7eeb1f918db5f0f0eb319745900bc` | Apache-2.0 | Adopt deterministic statistics, lint categories, offline report ideas, and adversarial tests. Do not introduce `script.json` as a second screenplay authority or global creative thresholds. |
| cajias/agentic-video-skills | `204cefd08bbb87fd4681f1f2b0dccbc444a978c1` | MIT for cinematic-director | Use as a read-only director-advice reference. It cannot own Shot IDs, continuity, or provider execution. |
| shinchven/nano-banana-skills | `d93dc85aeaadf122d241d2b0691a9eac03f9a4f7` | MIT | Retain the three-panel reference-sheet idea, expanded into versioned manifests, individual views, provenance, inferred-field review, and validation. |
| SamurAIGPT/Generative-Media-Skills | `5519622e885abc60217a65c8e090bcb1d9830746` | MIT | Reference-only for staged workflows and approval gates. Reject MuAPI runtime, credentials, uploads, direct billing, and flawed shell adapters. |
| maciejdzierzek/kling-ai-prompt-generator | `248b9a275fedd511a1f0d9c32dc42a233ffb6357` | MIT | Reimplement provider-neutral Prompt IR plus capability-driven renderers. Split motion transfer from camera trajectory; never hard-code volatile capability claims as permanent truth. |

## Source and license policy

Abstract methods are reimplemented locally. Any future direct code or substantial template copy must retain its source repository's license and attribution, including Apache NOTICE obligations where applicable. Model-service terms, source rights, likeness consent, voice consent, fonts, music, and generated-output rights remain separate from repository licenses.

## Security conclusions

- No external runtime or dependency was installed.
- No API key, token, cookie, password, or connection string is accepted in project contracts.
- Images and videos route only through the logged-in Lovart browser path.
- Paid jobs require immutable preview approval.
- Submitted jobs collect before retry.
- Generated media is structurally verified before creative QA and acceptance.
