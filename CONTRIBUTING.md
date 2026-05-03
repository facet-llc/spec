# Contributing

Facet is the protocol layer above the open standards for agentic commerce. The spec lives here. The hosted product (Terminal, knowledge graph, schema generator, reputation registry, agent WAF) does not.

## What we want

- Spec issues: clarifications, edge cases, conformance questions
- RFC discussions: proposals for v0.2 and beyond, in [Discussions](https://github.com/facet-llc/protocol/discussions)
- Reference implementations: verifiers in other languages (Rust, Go, Java, etc.) that conform to `SPEC.md`
- Examples: merchant integrations that show end-to-end flows

## What we don't take

PRs against the hosted Terminal (`api.facet.llc`) or the closed product layers. Those live in a private repo.

## Spec changes

Spec changes use lightweight RFC discipline:

1. Open a Discussion in the RFC category
2. Wait at least 7 days for feedback
3. If consensus emerges, open a PR against `SPEC.md` referencing the Discussion

Breaking changes bump the major version. Backward-compatible additions bump minor.

## Questions

[Issues](https://github.com/facet-llc/protocol/issues) for spec questions. [Discussions](https://github.com/facet-llc/protocol/discussions) for everything else.
