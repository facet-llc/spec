# Facet Protocol Specification

**Version:** 0.1.0 (skeleton, fills in v0.2)
**Status:** Working draft
**Last updated:** 2026-05-03

## 1. Introduction

Facet is the index of agent-ready businesses. This document specifies the protocol that lets autonomous agents discover, identify, transact with, and audit any participating merchant on the web.

The protocol composes four open standards into one rail:

- **KYAPay**: open IETF identity standard (ES256 JWT + JWKS)
- **MCP**: Anthropic capability and tool-discovery protocol
- **x402**: HTTP 402 payment-required revival, USDC-native
- **RFC 9421**: signed HTTP messages for web-bot-auth

Facet does not redefine any of these. It defines:

1. How they compose for agentic commerce
2. The endpoints a participating merchant exposes
3. The verifier semantics for KYAPay tokens
4. The audit-trail format for every settled transaction

## 2. Endpoints

A Facet-compliant merchant exposes:

```
GET  /v1/capabilities         → MCP capability + pricing manifest
GET  /v1/search?q=<query>     → Ranked, typed listings for the query
POST /v1/quote                → Quote for a chosen listing
POST /v1/reserve              → Reserve a quote
POST /v1/settle               → Settle a reservation (x402)
GET  /v1/audit/<txn-id>       → Signed audit record
```

Full request/response schemas: see [`schemas/`](./schemas) (coming v0.2).

## 3. Identity (KYAPay)

Agents authenticate to merchants via KYAPay JWTs. The verifier MUST:

- Accept `kya+jwt`, `pay+jwt`, and `kya-pay+jwt` token types per the KYAPay spec
- Resolve issuer JWKS via the `kid` header
- Validate `iss`, `aud`, `iat`, `exp`, and `nbf` claims
- Cache JWKS responses per `kid` for ≤24h

Implementations SHOULD use Cloudflare-cached JWKS resolution where available for global low-latency verification.

## 4. Discovery (MCP)

The `/v1/capabilities` endpoint MUST return a valid MCP manifest. Manifest entries SHOULD include `pricing` extensions for x402 settlement.

## 5. Payments (x402)

Settlement MUST follow x402. Currency MUST be USDC on Base L2 in v0.1. v0.2 will add multi-rail support per the KYAPay `stp` claim.

## 6. Audit (Ed25519)

Every settled transaction returns a signed audit record. This is Facet-specific and is not part of the KYAPay or x402 spec.

```json
{
  "txn_id": "...",
  "iat": 1714752000,
  "merchant": "did:facet:...",
  "agent": "did:facet:...",
  "sig": "<Ed25519 over the canonical body>",
  "kid": "<merchant signing key id>"
}
```

Verifier semantics for audit records: see [`AUDIT.md`](./AUDIT.md) (coming v0.2).

## 7. References

- KYAPay: open IETF Independent Submission for agent identity. Search `kyapay` at <https://datatracker.ietf.org>.
- MCP: <https://spec.modelcontextprotocol.io>
- x402: <https://github.com/coinbase/x402>
- RFC 9421 (HTTP Message Signatures): <https://www.rfc-editor.org/rfc/rfc9421>
- web-bot-auth (Cloudflare): <https://blog.cloudflare.com/web-bot-auth>

## 8. Conformance

A v0.1-conformant implementation MUST implement Sections 2, 3, 4, 5. Section 6 is RECOMMENDED in v0.1 and REQUIRED in v0.2.

---

*Working draft. Open issues or RFC discussions at <https://github.com/facet-llc/protocol>.*
