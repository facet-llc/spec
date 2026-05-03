# Facet Protocol

**The search engine for agentic commerce.** Open KYAPay verifier + the protocol layers above the spec.

```bash
curl -s https://facet.llc
# → 402 Payment Required. Identify via KYAPay; pay per-query at the Terminal.
```

Facet implements the open KYAPay identity standard (ES256 JWT + JWKS, web-bot-auth aligned, RFC 9421) and ships the protocol layers above the spec — vertical depth, schema generation, signed response provenance, reputation registry, and agent WAF.

## Layer cake

| Layer | Open standard | Facet's role |
|---|---|---|
| Identity | KYAPay (open IETF spec) | Leading verifier deployment in production |
| Discovery | MCP (Anthropic) | `/v1/capabilities` endpoints are MCP-native |
| Payments | x402 (Coinbase) | USDC settlement on Base L2 |
| Bot signing | RFC 9421 web-bot-auth | KYAPay JWTs are web-bot-auth aligned |

## Quickstart

```bash
# Get a ranked, typed listing for your agent to quote, reserve, and settle
curl -X GET "https://facet.llc/v1/search?q=dallas+plumbing" \
  -H "Authorization: Bearer <KYAPay JWT>"
```

See [`SPEC.md`](./SPEC.md) for the protocol spec and [`examples/`](./examples) for end-to-end integrations.

## What's in this repo

- [`SPEC.md`](./SPEC.md) — Facet protocol v0.1 spec, RFC-style
- [`examples/`](./examples) — minimal merchant integration (coming v0.2)
- Reference verifier + SDKs (coming v0.2)

## What's NOT in this repo

The hosted Terminal, vertical knowledge graph, schema generation engine, reputation registry, and agent WAF stay closed. Open the protocol; close the product.

## Status

`v0.1` — protocol spec public. Reference implementation lands `v0.2`.

## License

Apache 2.0. See [`LICENSE`](./LICENSE).

---

**Built by [Facet](https://facet.llc).** Issues / RFCs welcome — open an [issue](https://github.com/facet-llc/protocol/issues) or start a [discussion](https://github.com/facet-llc/protocol/discussions).
