# Architecture

Facet is the protocol layer for agentic commerce. This doc explains how the pieces fit together and where the trust boundaries are. For wire format see [`SPEC.md`](./SPEC.md). For the SDK see [`sdks/typescript/`](./sdks/typescript/).

## The four open standards Facet rides

```
                    +-----------------------+
                    |  facet.llc /v1/*      |   merchant endpoints
                    |  (Facet-compliant)    |
                    +-----------+-----------+
                                |
            +-------------------+-------------------+
            |                                       |
            v                                       v
   +--------------+  +-----------+  +----------+  +-----------+
   | KYAPay (id)  |  | MCP (cap) |  | x402 ($) |  | RFC 9421  |
   |  ES256 JWT   |  | Anthropic |  | Coinbase |  | bot-auth  |
   |  + JWKS      |  | discovery |  | USDC L2  |  | Cloudflare|
   +------+-------+  +-----+-----+  +----+-----+  +-----+-----+
          |                |             |              |
          v                v             v              v
   identity check     capability       payment       signed
                      manifest         settlement    request
```

Facet does not re-implement any of these. We compose them into a single rail and add the layers above the spec that production deployments need.

## Protocol flow

The agent's job is to identify itself, find what it wants, lock the price, pay, and prove it happened.

```
+---------+                                       +-----------+
|  Agent  |                                       | Merchant  |
+----+----+                                       +-----+-----+
     |                                                  |
     |  GET /v1/capabilities                            |
     |  (no auth)                                       |
     |------------------------------------------------->|
     |              MCP manifest + x402 pricing         |
     |<-------------------------------------------------|
     |                                                  |
     |  GET /v1/search?q=...                            |
     |  Authorization: Bearer <KYAPay JWT>              |
     |------------------------------------------------->|
     |    1. extract iss, kid from JWT header           |
     |    2. resolve issuer JWKS                        |
     |    3. verify ES256 signature                     |
     |    4. validate aud, exp, nbf                     |
     |              ranked, typed listings              |
     |<-------------------------------------------------|
     |                                                  |
     |  POST /v1/quote { listing_id }                   |
     |------------------------------------------------->|
     |              quote_id, amount, expires_at        |
     |<-------------------------------------------------|
     |                                                  |
     |  POST /v1/reserve { quote_id }                   |
     |------------------------------------------------->|
     |    402 Payment Required + x402 instructions      |
     |<-------------------------------------------------|
     |                                                  |
     |  (off-protocol: USDC transfer on Base)           |
     |                                                  |
     |  POST /v1/settle { reservation_id, x402_payment }|
     |------------------------------------------------->|
     |              txn_id, audit_endpoint              |
     |<-------------------------------------------------|
     |                                                  |
     |  GET /v1/audit/<txn_id>                          |
     |------------------------------------------------->|
     |              Ed25519-signed audit record         |
     |<-------------------------------------------------|
```

Six round-trips, fully auditable. The agent's KYAPay JWT carries identity through all of them; the merchant's Ed25519 audit record carries proof of settlement back.

## Trust boundaries

| Boundary | Trusted by | Verification |
|---|---|---|
| Agent → Merchant | KYAPay JWT | Merchant verifies via issuer's JWKS (ES256 + JWKS) |
| Issuer → Merchant (via JWKS) | Issuer's HTTPS endpoint | Cached per `kid`, allowlisted by `expectedIssuers` |
| Agent payment → Merchant | Public Base L2 transaction | Merchant checks `tx_hash` matches `to`/`amount` from /v1/reserve |
| Merchant audit → Agent | Ed25519 signature on audit record | Agent verifies via merchant's signing key (in DID document or JWKS) |

Two trust gates matter most:

1. **The agent's KYAPay token is only as trustworthy as the issuer.** Merchants MUST allowlist issuers; the SDK refuses to verify against arbitrary `iss` claims for this reason.
2. **The merchant's audit signature is only as trustworthy as the merchant's signing key.** Future v0.2 work: agent-side verifier for audit records, with reputation registry for issuer/merchant scoring.

## What's open vs what's closed

```
+------------------------------------------------+
|  Five layers above the spec   (CLOSED, hosted) |
|  - Vertical depth (knowledge graph)            |
|  - Schema generation (Shopify/Woo/NetSuite)    |
|  - Signed response provenance (Ed25519)        |
|  - Reputation registry (DID-keyed)             |
|  - Agent WAF (verifier-tier policy at edge)    |
+------------------------------------------------+
|  Facet protocol spec + SDKs   (OPEN, this repo)|
|  - SPEC.md                                     |
|  - schemas/v1.*.json                           |
|  - sdks/typescript/ (verifier + Terminal)      |
|  - test-vectors/kyapay/                        |
+------------------------------------------------+
|  Open standards we ride       (OPEN, others)   |
|  - KYAPay (IETF Independent Submission)        |
|  - MCP (Anthropic)                             |
|  - x402 (Coinbase)                             |
|  - RFC 9421 (IETF, Cloudflare)                 |
+------------------------------------------------+
```

The split is deliberate. The protocol grows because anyone can implement it. The hosted product is how we make money.

## SDK shape

`@facet/sdk-js` v0.0.x exposes two surfaces:

**Verifier** (merchant-side or agent-side):

```ts
import { verifyKYAToken } from '@facet/sdk-js';

const result = await verifyKYAToken(jwt, {
  audience: 'https://my-merchant.com',
  expectedIssuers: ['https://issuer.example.com'],
});
```

**Terminal client** (agent-side):

```ts
import { FacetTerminal } from '@facet/sdk-js';

const facet = new FacetTerminal({ getKYAToken: () => token });
const search = await facet.searchListings({ q: 'dallas plumbing' });
const quote = await facet.requestQuote({ listing_id: search.results[0].id });
const reservation = await facet.reserve({ quote_id: quote.quote_id });
// ... pay via x402, then:
const receipt = await facet.settle({ reservation_id, x402_payment });
const audit = await facet.getAuditRecord(receipt.txn_id);
```

End-to-end example in [`sdks/typescript/examples/hello-agent/`](./sdks/typescript/examples/hello-agent/).

## Roadmap

| Version | What lands |
|---|---|
| v0.0.x | Verifier, Terminal client, conformance vectors, schemas, this doc |
| v0.1.0 | `verifyAuditRecord` (Ed25519), AUDIT.md, multi-rail payments per `stp` claim |
| v0.2.0 | Python and Go SDK siblings, autogenerated TypeScript types from schemas, merchant-side example apps |
| v1.0.0 | IETF draft submission for the Facet protocol layer above the open standards |
