# Use Lovart as the only image and video generation backend

Hermes owns contracts, approvals, task state, provenance, QA, and local delivery; Lovart alone executes image and video generation. Upstream MuAPI and direct-provider adapters remain reference-only because parallel paid backends duplicate credentials, state, billing, and retry behavior and weaken idempotency.
