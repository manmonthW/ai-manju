# Bind approval to immutable paid-job previews

Every paid Generation Job must be previewed and explicitly approved by matching a cryptographic preview hash before submission. Approval is consumed on execution; changed prompts, parameters, references, or outputs invalidate it, and submitted jobs must be collected before retry to prevent duplicate credit spend.
