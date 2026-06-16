# SDKs have moved

The Facet SDKs and reference rail adapters now live in their own repository:

**https://github.com/facet-llc/sdk**

Published packages (Apache-2.0):

- `@facet-llc/protocol` — agents.txt parser and protocol types
- `@facet-llc/client` — agent-side client (search / quote / reserve / settle / audit)
- `@facet-llc/sdk-node` — Node SDK
- payment-rail adapters (x402, Stripe) and origination verifiers (AWS AgentCore, Coinbase CDP)

This repository remains the home of the protocol itself: the spec
([`../SPEC.md`](../SPEC.md)), the JSON schemas ([`../schemas/`](../schemas/)),
and the conformance vectors ([`../test-vectors/`](../test-vectors/)).
