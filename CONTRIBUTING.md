# Contributing to Facet Protocol

Facet is the protocol layer above the open standards for agentic commerce. The spec lives here; the hosted product does not.

## Welcome

We welcome:

- **Spec issues** — clarifications, edge cases, conformance questions
- **RFC discussions** — proposals for v0.2+ via [Discussions](https://github.com/facet-llc/protocol/discussions)
- **Reference implementations** — alternative-language verifiers (Rust, Go, Java, etc.) that conform to `SPEC.md`
- **Examples** — merchant integrations that show end-to-end flows

We do **not** take PRs against:

- The hosted Terminal (`api.facet.llc`) — closed source
- The vertical knowledge graph, schema generator, reputation registry, agent WAF — closed source

## Spec changes

Spec changes use lightweight RFC discipline:

1. Open a Discussion in [RFCs](https://github.com/facet-llc/protocol/discussions/categories/rfcs)
2. Allow ≥7 days for community feedback
3. If consensus emerges, open a PR against `SPEC.md` referencing the Discussion

Breaking changes bump the major version. Backward-compatible additions bump minor.

## Code of conduct

Be precise. Be technical. Disagree on substance, not people.

## Questions

[Issues](https://github.com/facet-llc/protocol/issues) for spec questions. [Discussions](https://github.com/facet-llc/protocol/discussions) for everything else.
