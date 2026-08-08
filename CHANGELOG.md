# Changelog

All notable changes to the Facet Protocol specification will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-08-06

### Added

- Section 4 rewritten for MCP's stateless revision (`2026-07-28`): `POST /ucp/mcp` as a JSON-RPC endpoint with no session and no handshake, `server/discover`, per-request version negotiation via `_meta` or the `MCP-Protocol-Version` header, `resultType`, cache hints (`ttlMs`, `cacheScope`), deterministic tool order, and `-32022` for an unsupported revision.
- Section 5, Authorization: a Terminal accepts either a Facet KYA bearer token or an OAuth 2.1 access token. Adds RFC 9728 protected-resource metadata, the `WWW-Authenticate` challenge that starts the flow, and token acquisition via `client_credentials` with a `private_key_jwt` assertion bound to the merchant's resource URI.
- References for RFC 9728, RFC 8414, RFC 8707, and RFC 7523.

### Changed

- `2025-06-18` is retained for back-compat. `initialize` and `ping` still work and are marked deprecated; `initialize` must negotiate rather than always answering with the newest supported revision.
- Conformance (Section 9) now names the specific Section 4 and Section 5 obligations rather than listing section numbers alone.
- Section 2 leads with `POST /ucp/mcp`. `GET /v1/capabilities` is retained for existing clients and is not extended.

### Fixed

- `schemas/v1.capabilities.json` documented the protocol as targeting MCP `2024-11-05`. That was three revisions stale and named a surface that is no longer where MCP is served. The field is now described as the legacy manifest's echo, pointing at Section 4 for the current surface.
- The footer pointed at a repository path that no longer hosts this spec.

## [Unreleased]

### Changed

- Tagline: "the search engine for agentic commerce" became "the index of agent-ready businesses". Sharper category framing.

### Added

- JSON Schema definitions for the six v0.1 endpoints, in `schemas/`.
- KYAPay JWT conformance test vectors, in `test-vectors/kyapay/`.
- Reference TypeScript SDK scaffold (`@facet/sdk-js` v0.0.1) with a real KYAPay verifier built on `jose`, in `sdks/typescript/`.

## [0.1.0] - 2026-05-03

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

- Multi-rail payment support (Visa VIC, Mastercard SCOF) per KYAPay `stp` claim
- SDK packages in Python and Go
- Example merchant integration end-to-end
