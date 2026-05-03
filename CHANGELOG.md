# Changelog

All notable changes to the Facet Protocol specification will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-05-03

### Added

- Initial public release of the Facet Protocol specification
- Section 1: Introduction and standards composition
- Section 2: Endpoint surface (`/v1/capabilities`, `/v1/search`, `/v1/quote`, `/v1/reserve`, `/v1/settle`, `/v1/audit/<txn-id>`)
- Section 3: Identity verification semantics (KYAPay)
- Section 4: Discovery via MCP
- Section 5: Payments via x402 (USDC on Base L2)
- Section 6: Signed audit records (Ed25519, above-the-spec extension)
- Apache 2.0 license
- Contribution guide and RFC process

### Coming in v0.2

- Reference verifier (TypeScript)
- SDK packages (`@facet/sdk-js`, `@facet/sdk-python`, `@facet/sdk-go`)
- JSON Schema for every endpoint
- Test vectors for KYAPay JWT conformance
- Multi-rail payment support (Visa VIC, Mastercard SCOF) per KYAPay `stp` claim
- Example merchant integration end-to-end
