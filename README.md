# Facet Protocol

The index of agent-ready businesses.

## Why

Every team building agents that transact ends up writing the same plumbing. An identity verifier. An x402 settlement loop. An audit trail. Five teams, five implementations, none compatible.

The pattern is a protocol, not a feature. So I wrote one, ran a verifier in production at facet.llc, and put both here. If you're building anything in this space, this saves you a few months.

## Try the live one

```bash
curl -s https://facet.llc
# 402 Payment Required. Identify via KYAPay, pay per-query at the Terminal.
```

The site is the demo. Scrape it and you get the protocol response. Send a valid KYAPay JWT and you get ranked, typed listings to quote, reserve, and settle.

```bash
curl -X GET "https://facet.llc/v1/search?q=dallas+plumbing" \
  -H "Authorization: Bearer <KYAPay JWT>"
```

## What Facet is

Facet implements the open KYAPay identity standard (ES256 JWT + JWKS, web-bot-auth aligned per RFC 9421). On top of that we ship five protocol layers the spec doesn't cover: vertical depth, schema generation, signed response provenance, reputation registry, and an agent WAF.

The four open standards we ride:

| Layer | Standard | What we do with it |
|---|---|---|
| Identity | KYAPay (IETF) | Run the leading verifier in production |
| Discovery | MCP (Anthropic) | `/v1/capabilities` is MCP-native |
| Payments | x402 (Coinbase) | USDC settlement on Base L2 |
| Bot signing | RFC 9421 (Cloudflare) | KYAPay JWTs are aligned |

## What's in here

`SPEC.md` is the v0.1 protocol spec, RFC-style. Read it if you're building a verifier or a Facet-compliant merchant.

`examples/` will get end-to-end integrations in v0.2 (TypeScript merchant, Python merchant, Go merchant, agent client).

## What's not in here

The hosted Terminal at `api.facet.llc` is closed. Same for the vertical knowledge graph, schema generator, reputation registry, and agent WAF. Those are how we make money. The spec is open so anyone can verify and integrate.

## Status

v0.1: protocol spec public. v0.2: reference verifier and SDKs in TypeScript, Python, and Go.

## License

Apache 2.0. See [`LICENSE`](./LICENSE).

---

Built by [Facet](https://facet.llc). Spec questions go in [issues](https://github.com/facet-llc/protocol/issues). RFC discussion lives in [discussions](https://github.com/facet-llc/protocol/discussions).
