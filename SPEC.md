# Facet Protocol Specification

**Version:** 0.2.0
**Status:** Working draft
**Last updated:** 2026-08-06

## 1. Introduction

Facet is the index for agent-ready businesses. This document specifies the protocol that lets autonomous agents discover, identify, transact with, and audit any participating merchant on the web.

The protocol composes four open standards into one rail:

- **KYAPay**: open IETF identity standard (ES256 JWT + JWKS)
- **MCP**: Anthropic capability and tool-discovery protocol
- **x402**: HTTP 402 payment-required revival, USDC-native
- **RFC 9421**: signed HTTP messages for web-bot-auth

Facet does not redefine any of these. It defines:

1. How they compose for agentic commerce
2. The endpoints a participating merchant exposes
3. The verifier semantics for agent credentials
4. The audit-trail format for every settled transaction

### 1.1 What changed in v0.2

v0.1 described discovery as a single `GET /v1/capabilities` manifest against MCP `2024-11-05`. That is superseded. MCP's `2026-07-28` revision made the protocol **stateless**: it removed the `initialize` handshake and session id, moved version negotiation into per-request `_meta`, and added a `server/discover` method. Section 4 is rewritten for that model and retains the older revision for back-compat.

v0.2 also adds Section 5, authorization. A merchant Terminal now accepts **either** a Facet KYA bearer token **or** an OAuth 2.1 access token, and advertises itself as an OAuth protected resource per RFC 9728 so a standards-compliant MCP client can complete the flow with no Facet-specific code.

## 2. Endpoints

A Facet-compliant merchant exposes:

```
POST /ucp/mcp                 → MCP endpoint (JSON-RPC 2.0). See Section 4.
GET  /v1/search?q=<query>     → Ranked, typed listings for the query
POST /v1/quote                → Quote for a chosen listing
POST /v1/reserve              → Reserve a quote
POST /v1/settle               → Settle a reservation (x402)
GET  /v1/audit/<txn-id>       → Signed audit record

GET  /.well-known/oauth-protected-resource   → RFC 9728 metadata. See Section 5.
```

`GET /v1/capabilities` remains available and returns the v0.1 manifest. New implementations SHOULD use `POST /ucp/mcp`; `/v1/capabilities` is retained for existing clients and is not extended.

Full request/response schemas: see [`schemas/`](./schemas).

## 3. Identity (KYA)

Agents identify themselves to merchants with a bearer credential on the `Authorization` header. Two credential types are accepted; see Section 5 for how a client chooses between them.

A Facet KYA is an ES256 JWT with `typ: kya+jwt`. The verifier MUST:

- Resolve issuer JWKS via the `kid` header
- Validate `iss`, `aud`, `iat`, `exp`, and `nbf` claims
- Reject an issuer not in the merchant's trusted-issuer set
- Cache JWKS responses per `kid` for no more than 24h

Merchants advertise their accepted issuers; a default issuer is published in the merchant's discovery bundle. Implementations SHOULD use edge-cached JWKS resolution where available for global low-latency verification.

KYA answers **who the agent is**. It does not describe how the agent pays; that is Section 6.

## 4. Discovery and tools (MCP)

### 4.1 Transport

The MCP endpoint is `POST /ucp/mcp`, speaking JSON-RPC 2.0 over HTTP. It is **stateless**: there is no session, no session id header, and no handshake required before calling a method.

### 4.2 Version negotiation

A client MAY declare the revision it speaks in either of two places:

- request `params._meta["io.modelcontextprotocol/protocolVersion"]`
- the `MCP-Protocol-Version` request header

A server MUST honor both, and MUST treat the declared value, not the channel it arrived on, as the revision. A request that declares no version MUST still be served.

If the declared revision is not supported, the server MUST reject the request with JSON-RPC error `-32022` and MUST include the supported set:

```json
{
  "code": -32022,
  "message": "Unsupported protocol version",
  "data": {
    "supported": ["2026-07-28", "2025-06-18"],
    "requested": "1999-01-01"
  }
}
```

`server/discover` MUST be exempt from version rejection, since it is how a client learns which revisions are available.

### 4.3 `server/discover`

Open, no credential. Returns the server's supported revisions and capabilities:

```json
{
  "resultType": "complete",
  "supportedVersions": ["2026-07-28", "2025-06-18"],
  "capabilities": { "tools": {} },
  "ttlMs": 3600000,
  "cacheScope": "public",
  "_meta": {
    "io.modelcontextprotocol/serverInfo": { "name": "...", "version": "..." }
  }
}
```

`serverInfo` lives under `_meta`, not at the top level.

### 4.4 `tools/list`

Open, no credential. Returns the tool set with `resultType: "complete"` and cache hints:

```json
{
  "resultType": "complete",
  "ttlMs": 300000,
  "cacheScope": "public",
  "tools": [ ... ]
}
```

Tool order MUST be deterministic: repeated calls return the same order, so a client may cache and diff the set. Order is stable and meaningful, not alphabetical.

Every tool carries a JSON Schema 2020-12 `inputSchema`. Clients MUST construct calls from that schema. Several tools nest their arguments under a single top-level object; a flattened call is rejected with `-32602`.

### 4.5 `tools/call`

Per-tool authorization, see Section 5. Successful results carry `resultType: "complete"` alongside `content` and, where the tool returns structured data, `structuredContent`. Results that represent a tool-level error carry `resultType` as well.

### 4.6 Errors

| Condition | Response |
|---|---|
| Unknown method | JSON-RPC `-32601` |
| Malformed or missing tool arguments | JSON-RPC `-32602` |
| Unsupported protocol revision | JSON-RPC `-32022` with `data.supported` |
| Missing or invalid credential on a gated tool | HTTP `401` with `WWW-Authenticate` (Section 5.3) |

Argument validation is evaluated before the authorization gate. A caller supplying malformed arguments to a gated tool receives `-32602` rather than `401`. This is intentional: tool schemas are already public via `tools/list`, so the ordering discloses nothing that discovery does not.

### 4.7 Back-compat with `2025-06-18`

Servers SHOULD continue to accept `initialize` and `ping` for clients on the older revision. `initialize` MUST negotiate: a client offering `2025-06-18` MUST receive `2025-06-18`, not the newest supported revision. Both methods are deprecated and MAY be removed once the older revision is retired.

## 5. Authorization

### 5.1 Two accepted credentials

A merchant Terminal accepts either:

1. a **Facet KYA** bearer token (Section 3), or
2. an **OAuth 2.1 access token** bound to the merchant's MCP resource URI.

Both travel as `Authorization: Bearer <token>`. A KYA is a complete credential on its own; the OAuth path exists so a client with no Facet-specific code can still authenticate.

Tools divide into open and gated. Catalog reads and payment-capability discovery are open. Cross-merchant directory search, quoting, payment requirements, and order reads are gated. The exact division is discoverable: a gated tool returns `401` when called without a credential.

### 5.2 Protected-resource metadata (RFC 9728)

A merchant MUST serve `GET /.well-known/oauth-protected-resource`:

```json
{
  "resource": "https://<merchant-host>/ucp/mcp",
  "authorization_servers": ["https://<issuer-host>"],
  "scopes_supported": ["mcp:tools"],
  "bearer_methods_supported": ["header"]
}
```

`resource` MUST be the canonical MCP endpoint URI with no trailing slash and no fragment. It is the value a client passes as the `resource` parameter when requesting a token, and the audience the merchant validates.

### 5.3 The `401` challenge

A gated tool called without an acceptable credential MUST return HTTP `401` with a `WWW-Authenticate` header naming the metadata document:

```
WWW-Authenticate: Bearer resource_metadata="https://<merchant-host>/.well-known/oauth-protected-resource", scope="mcp:tools"
```

That header is what starts the flow: it is how a client with no prior knowledge of Facet finds the authorization server. A request bearing a valid KYA is unaffected.

**Scope is advertised but not yet enforced.** `mcp:tools` is the defined scope value and is what `scopes_supported` names. In this revision, per-tool authorization is decided by the presence of a valid, correctly-audienced credential, not by the scope it carries. A client MUST NOT rely on requesting a narrower scope to constrain what its own token can do. Scope-based refusal (`403` with `error="insufficient_scope"`) is reserved for a future revision; implementations SHOULD NOT advertise it as an access control until they enforce it.

### 5.4 Obtaining a token

The authorization server publishes RFC 8414 metadata at `/.well-known/oauth-authorization-server`. The Facet reference issuer advertises:

- `grant_types_supported`: `["client_credentials"]`
- `token_endpoint_auth_methods_supported`: `["private_key_jwt"]`
- `registration_endpoint` for self-serve agent enrollment

There is no interactive authorization-code flow: agents are non-interactive clients. The `authorization_endpoint` is advertised for metadata completeness and returns `unsupported_response_type`.

A client authenticates to the token endpoint with a `private_key_jwt` client assertion (RFC 7523) and requests a token for a specific `resource` (RFC 8707). The resulting token is valid only at that merchant's MCP endpoint; presenting it to another merchant MUST fail. Audience binding, not scope, is what confines a token in this revision.

## 6. Payments (x402)

Settlement MUST follow x402. Currency MUST be USDC on Base L2 in v0.1. Multi-rail settlement is selected per the KYAPay `stp` claim.

## 7. Audit (Ed25519)

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

Verifier semantics for audit records: see [`AUDIT.md`](./AUDIT.md).

## 8. References

- KYAPay: open IETF Independent Submission for agent identity. Search `kyapay` at <https://datatracker.ietf.org>.
- MCP: <https://spec.modelcontextprotocol.io>
- x402: <https://github.com/coinbase/x402>
- RFC 9421 (HTTP Message Signatures): <https://www.rfc-editor.org/rfc/rfc9421>
- RFC 9728 (OAuth 2.0 Protected Resource Metadata): <https://www.rfc-editor.org/rfc/rfc9728>
- RFC 8414 (OAuth 2.0 Authorization Server Metadata): <https://www.rfc-editor.org/rfc/rfc8414>
- RFC 8707 (Resource Indicators for OAuth 2.0): <https://www.rfc-editor.org/rfc/rfc8707>
- RFC 7523 (JWT Client Authentication): <https://www.rfc-editor.org/rfc/rfc7523>
- web-bot-auth (Cloudflare): <https://blog.cloudflare.com/web-bot-auth>

## 9. Conformance

A v0.2-conformant implementation MUST implement Sections 2, 3, 4, 5, and 6. Section 7 is RECOMMENDED.

Within Section 4, an implementation MUST serve `server/discover`, MUST honor version declaration from both `_meta` and the header, MUST reject an unsupported revision with `-32022` carrying the supported set, and MUST return deterministic tool order. Support for `2025-06-18` back-compat is RECOMMENDED.

Within Section 5, an implementation MUST serve protected-resource metadata, MUST return the `WWW-Authenticate` challenge on a gated `401`, and MUST reject a token audienced to a different resource. Accepting OAuth access tokens in addition to KYA is REQUIRED for v0.2 conformance. Scope enforcement is NOT required in v0.2 and MUST NOT be presented as an access control by an implementation that does not enforce it.

---

*Working draft. Open issues or RFC discussions at <https://github.com/facet-llc/spec>.*
