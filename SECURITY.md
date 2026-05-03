# Security Policy

## Reporting a vulnerability

Email security@facet.llc.

Please include:

- A description of the issue
- Steps to reproduce
- Affected version (commit SHA or release tag)
- Your name and how you'd like to be credited (or anonymous)

We respond within 72 hours. Coordinated disclosure window is 90 days from acknowledgement.

## Scope

In scope:

- The protocol spec in `SPEC.md`
- Any reference verifier or SDK shipped from this repo (`sdks/*`), all versions
- The conformance test vectors and generator (`test-vectors/`)
- The JSON schemas (`schemas/`)

Out of scope (private repos, separate disclosure path):

- The hosted Terminal at `api.facet.llc`
- Any closed product layers (knowledge graph, schema generator, reputation registry, agent WAF)

For hosted-Terminal vulnerabilities, also email security@facet.llc but mark the subject `[hosted]`.
