# Facet: The Post-Scraping Substrate for the Agent Web

**A white paper on agent-native infrastructure for B2B commerce**

Version 0.3 · 2026-05-05 · Facet, Inc.

---

## 1. Abstract

Agent-mediated traffic has crossed the majority threshold on many commercial websites, and the protocol layer for agent-to-business interaction is being standardized in real time by a coalition of well-capitalized players. Anthropic (Model Context Protocol), Skyfire (KYAPay, IETF Independent Submission), Coinbase (x402 HTTP payments + AgentKit), and Cloudflare (RFC 9421 signed-bot-auth). This paper introduces Facet, **a horizontal product-layer installed above those rails**. a standalone tool every website can deploy to protect itself from unidentified scrapers and monetize verified good-agent traffic. Facet addresses the problems the horizontal protocol stack leaves unsolved: catalog-to-agent schema generation, site-side agent traffic analytics, agent reputation scoring, and Ed25519 response-provenance. Facet is the agent-native protection and monetization substrate installed on top of the emerging horizontal protocol stack. The reference deployment uses an F&B supplier-network as the go-to-market wedge -- but Facet the product is horizontal and available to any website. The paper presents Facet's design principles, the thin `agents.txt` discovery-file format Facet publishes alongside the KYAPay-primary identity layer, HTTP-level protocol sketches for Facet's quote/reserve flow terminating at KYAPay's `charge` API, the Ed25519 response-signing architecture (absent from KYAPay's spec), and a comparative analysis against scraping, API gateways, and closed enterprise APIs. Ecosystem participants. agent operators, site integrators, and standards-body reviewers of the KYAPay IETF draft. are invited to contribute.

---

## 2. Introduction: The Post-Scraping Web

The web's interaction model was designed for humans reading documents, evolved for humans interacting with applications, and is now being driven at scale by autonomous software agents. Cloudflare Radar reports AI-bot traffic crossing 50% of non-search bot volume in early 2025 and rising. Every commercial website serving that traffic is doing so through a substrate designed for a different client.

The result is a system that fails on five axes simultaneously.

**Adversarial.** Scrapers and sites are in a perpetual arms race. CAPTCHAs, headless-Chrome fingerprinting, proxy networks, residential IP pools. Both sides burn engineering resources on a problem that should not exist. The cost of the arms race is absorbed by the site (bandwidth, bot-defense licensing) and by the scraper (proxy cost, CAPTCHA-solving services). Neither side wins in aggregate.

**Unmetered.** An AI agent retrieving a product price, a specification sheet, or a compliance document from a supplier pays nothing, and the supplier receives nothing. The supplier absorbs the bandwidth and compute; the economic value flows entirely to the agent's operator and, indirectly, to the end user. For suppliers, this is an externality with no compensating mechanism.

**Unidentified.** The supplier has no way to distinguish a paying customer's agent from a competitor's scraper, from a legitimate research tool, from a malicious harvester. Every request looks like a user-agent string. which is to say, none of them look like anything the server can trust.

**Unverifiable.** An agent that chains multiple sources cannot cryptographically prove that a given price, quote, or document came from a specific origin at a specific time. Downstream consumers of the agent's output must trust the agent's memory or the agent's model; neither is a source of truth.

**Unauditable.** There is no record of which agent requested what, when, on whose behalf, under what terms. Regulatory regimes emerging through 2024–2026 (the EU AI Act, US state-level rulings on scraping and copyright) demand exactly this record.

Each of these failures has been addressed individually by adjacent tooling. bot management for adversarial, paywalls for unmetered, API keys for unidentified, digital signatures for unverifiable, logging for unauditable. None has been bundled into a coherent substrate. Facet is the first attempt.

---

## 3. Forcing Functions

Six empirical shifts make the 2026 window critical. Each claim below is attributable to a specific source; URL verification is required before external publication and is flagged where the source is directional rather than precise.

**Agent-traffic volume.** Cloudflare Radar's bot analytics reported AI-bot traffic crossing 50% of non-search bot volume in Q1 2025 and continuing to rise through the year. (Cloudflare Radar, Q1 2025 AI bot traffic analysis; URL verification pending.) The underlying drivers are (a) production deployment of Operator-class autonomous agents by Anthropic, OpenAI, and Google; (b) rapid adoption of agentic workflows in enterprise software; (c) consumer AI assistant adoption at scale.

**Publisher paywalls.** The New York Times' litigation against OpenAI and Microsoft (filed December 2023, ongoing as of 2026), Reddit's paid API transition (2023), and Stack Overflow's crawler restrictions (2023–2024) collectively signal a systemic publisher response: agent traffic will not be served uncompensated. (Industry reporting through 2025; specific citations require URL verification.)

**Cloudflare AI Audit and pay-per-crawl.** Cloudflare announced AI Audit in 2024 and expanded with pay-per-crawl options through 2025 (Cloudflare blog, 2024–2025). The feature is positioned as bot-defense billing, not commerce infrastructure. but the deployment signals the market direction and legitimizes per-request agent monetization as a category.

**MCP adoption.** Anthropic's Model Context Protocol was published in November 2024 and has seen rapid developer adoption through 2025. Claude Desktop native integration, third-party MCP servers across developer tooling, enterprise MCP integrations (Anthropic MCP documentation and ecosystem directory, 2024–2025). MCP is the protocol shape for agent-tool interaction; the hosted-terminal business layered above it is unclaimed.

**x402 protocol.** Coinbase published the x402 HTTP payment extension in 2024, enabling native HTTP 402 Payment Required responses settled in USDC on Base L2 (Coinbase x402 documentation and reference implementations, 2024). Programmatic micropayment over HTTP is now trivial.

**EU AI Act transparency provisions.** The EU AI Act entered force August 2024 with staged application through 2026–2027 (EUR-Lex, Regulation (EU) 2024/1689). Transparency and provenance requirements for agent-mediated interactions favor identity and audit substrates over scraping.

The convergence of these six shifts within an approximately 30-month window is the category-formation signal. The primitive that bundles them. identity, commerce, audit, protocol. is unclaimed. The 12-to-18-month window for establishing the substrate is driven by Cloudflare's and Anthropic's product velocity: Cloudflare will likely ship an integrated commerce + identity layer by late 2027 at the earliest; Anthropic will not but may contribute protocol changes that complicate independent positioning if they occur without Facet's participation.

---

## 4. The Category: Agent-Native Infrastructure

The web's infrastructure has moved through two prior eras and is now entering a third.

**Era 1. the static web (1993–2005).** Documents for humans. HTML retrieved by browsers, crawled by early search engines. Infrastructure primitives: HTTP, HTML, `robots.txt` (1994), early search indexing. The substrate assumed a human reader.

**Era 2. the app web (2005–2025).** Applications for humans. Single-page applications, REST APIs, mobile clients, OAuth. Infrastructure primitives: JSON/REST, GraphQL, service meshes, API gateways, Bot Management. The substrate assumed a human user driving an application; APIs were a developer-integration surface, not an agent surface.

**Era 3. the agent web (2026–).** Autonomous software driving tasks at scale. Agents as primary non-human clients, outnumbering humans on many commercial sites. The substrate requires: machine-verifiable identity, machine-addressable schemas, native monetization per query, atomic transaction primitives, cryptographic provenance, structured audit. None of this is a retrofit of Era 2 infrastructure. The substrate must be rebuilt.

Retrofitting an API gateway for agents produces a system with API-key identity (not DID), per-month developer billing (not per-query micropayment), JSON-schema contracts (not MCP + schema.org hybrid), and no provenance layer. It works for the first wave of agent adoption and breaks at scale. Facet is Era 3 infrastructure, designed to interoperate with Era 2 where necessary (suppliers still run their ERPs and catalogs on Era 2 stacks) but exposing an Era 3 surface.

---

## 5. Design Principles

Six principles govern the architecture. They are invariants, not suggestions.

**1. Every agent is a first-class principal.** Agent identity is a Decentralized Identifier (DID), resolvable via `.well-known/did.json` or the DID resolution network. Every agent request includes a JWT signed by the agent operator's key. This is categorically different from an API key: a DID is cryptographically bound to an identity document published by the operator, enabling revocation, rotation, and trust-chain resolution without a central registry.

**2. Every supplier is a sandbox-isolated tenant.** Tenant isolation is enforced at the OS and database layer, not the application layer. Each supplier's data lives in logically isolated Postgres schemas (or equivalent) and Edge Functions execute in per-request sandboxes. Cross-tenant data leakage is prevented by the platform, not by careful application code.

**3. Every response is signed.** Cryptographic provenance is default-on, not an enterprise upsell. Every Facet Terminal response carries an `X-Facet-Signature` header with an Ed25519 signature over the request and response hashes and timestamp. Downstream agents chaining responses can verify authenticity without trusting the intermediate model.

**4. Protocols are open; services are hosted.** The `agents.txt` specification and the Facet Terminal protocol are published under Apache 2.0 on the Facet GitHub. Reference implementations are open source. The hosted runtime, managed identity, analytics, and commerce layers are proprietary SaaS. This is the same split as Let's Encrypt (open protocol) versus commercial CAs (proprietary service).

**5. Standalone product, focused company.** Facet is a separate company with its own cap table, brand, and product surface. Every component -- terminal, knowledge graph, admin dashboard, audit log, data room -- runs under `facet.llc` with its own auth, RLS, and operational store. No shared dependencies on adjacent products; nothing for an investor to disentangle at acquisition.

**6. Agent-first, not agent-retrofit.** Every service in the stack is designed under the assumption that the primary client is autonomous, untrusted, and potentially malicious. The threat model starts with "this request is hostile" and structural isolation proves otherwise on a per-request basis.

---

## 6. The Nine-Component Stack

Facet decomposes into nine components. Each exposes a distinct surface, and most are independently deployable. Ship order within the reference implementation is adapter → terminal → identity → commerce → analytics, with the remaining four components shipping in parallel once the MVP is stable.

### 6.1 Schema Auto-Generator

A Deno background worker ingests a supplier's catalog from one or more sources (Shopify REST API, WooCommerce REST API, NetSuite SuiteTalk, CSV uploads, PIM APIs such as Akeneo, or a headless crawl of the supplier's catalog pages) and emits a normalized `facet.yaml` manifest. The manifest drives the Terminal Runtime's schema exposure and is re-generated on a configurable cadence or in response to supplier webhook signals.

The schema-inference pipeline uses Claude Sonnet for ambiguous fields (for example, mapping a supplier's internal "Category 1 / Category 2" taxonomy to schema.org Product Category) and rule-based transformation for deterministic fields (SKU, price, availability). Every inferred field is flagged for supplier review before going live; no automatic inference ships to production without explicit supplier approval.

```
Supplier catalog
    |
    v
+-----------------+
| Source adapter  |  (Shopify, NetSuite, Woo, CSV, PIM, headless crawl)
+-----------------+
    |
    v
+-----------------+
| Normalizer      |  (rule-based + LLM for ambiguous fields)
+-----------------+
    |
    v
+-----------------+
| facet.yaml      |  (MCP + OpenAPI + schema.org hybrid manifest)
+-----------------+
    |
    v
 Terminal Runtime
```

### 6.2 Agent Terminal Runtime

A Deno Edge Function that serves signed agent requests. The request flow is: verify agent DID and JWT, check rate limit, meter the request, dispatch to the handler (read, quote, reserve, settle), sign the response, append to the audit log.

### 6.3 agents.txt and Identity Gateway

The `agents.txt` file is a declarative permissions and pricing manifest published at `/.well-known/agents.txt`. Full specification in §7. The Identity Gateway is a Deno Edge Function that resolves DIDs, caches resolution results for 5 minutes, and polls the DID operator's revocation list every 60 seconds. Full identity model in §9.

### 6.4 Atomic Commerce Primitives

Four idempotent signed calls: `search`, `quote`, `reserve`, `settle`. Full HTTP protocol in §8.

### 6.5 Agent Analytics

An append-only events table in Postgres captures every Terminal request. Per-supplier materialized views refresh hourly for the admin dashboard. Aggregate queries for cross-supplier insights run against the analytics schema, not the operational schema.

### 6.6 Content Licensing Marketplace

A publisher sets a per-query price in `agents.txt`. Payment handling uses x402 HTTP 402 responses. The Facet platform takes 15–20% of publisher revenue as a marketplace fee.

### 6.7 Agent WAF

Upstream of the Terminal. Classifies incoming requests: verified (Facet identity), known-scraper (blocked), unknown (challenged). Standalone product for suppliers not yet on the Terminal; bundled with Pro tier.

### 6.8 Agent Reputation Registry

A DID-keyed reputation registry storing signals on payment history, abuse reports, and agreement compliance. API-queryable. Suppliers set a minimum trust threshold in `agents.txt`; agent operators can query their own reputation and remediate if it falls.

### 6.9 Signed-Response Provenance

Every Terminal response carries an `X-Facet-Signature` header. Full signature structure and verification pseudocode in §9.

---

## 6.5 Business-Archetype Primitives. The Eight Surfaces (added v1.1)

The nine technical components in §6 form the **infrastructure layer**. Sitting above them is the **product layer**: eight business-archetype primitives that wrap the four atomic transaction verbs (§8) with archetype-specific semantics. Customers buy primitives; primitives buy verbs; verbs ride the rails.

A site declares which primitives it has activated via `Capabilities:` in `agents.txt v1.1` (see `specs/agents.txt-v1.1.md` §5). One site typically activates 2–4 (an F&B co-manufacturer activates **Catalog + Quote/RFQ + Paywalled Content + Credentialed**; a hotel activates **Booking + Date-Bound Inventory + Paywalled Content**). The primitives compose freely.

### 6.5.1 Catalog (fixed-price, in-stock)

The original Facet primitive: an agent browses → quotes → reserves → pays → ships. All four atomic verbs active. Reservation TTL 5 min default. Idempotent by reservation token. Reference adapters: Shopify, WooCommerce, BigCommerce, Square, CSV, F&B Ingredient Distributor specialist generator. Coverage: D2C brands, B2B catalog wholesalers, ingredient distributors (Facet's GTM wedge), drop-shippers, app stores, course catalogs, digital marketplaces, B2B SaaS plan signup. Take-rate: 1–3% on settled transactions. **Production-ready today.**

### 6.5.2 Paywalled Content (per-query / per-token / per-second access)

`search → quote → settle` (no reserve. access is instant on payment). Then `consume_license` increments usage counter against the purchased scope. Per-scope offers (e.g. `/tech/* = $0.05`, `/research/* = $0.20`). Coverage: news (NYT, WSJ), Substack newsletters, academic journals (Elsevier, Springer), data vendors (Bloomberg-style B2B feeds), premium video/audio, API access plans, document repositories, legal databases. Take-rate: 15–20% (industry standard for content licensing. competing head-to-head with Tollbit). **Scaffolded; W4 extension to add `quote_license` + per-scope offers.**

### 6.5.3 Subscription / Cadence (agent-side recurring orders)

Initial `search → quote → settle` to set up the profile, then cron-triggered `settle` calls on the schedule. Pause / skip / cancel manage cadence without re-consenting. Cadences: weekly, biweekly, monthly, quarterly, annual. **Important distinction:** the existing `site_subscription_tiers` table is for Facet charging suppliers (Free/Pro/Enterprise tiers); the Subscription primitive is for agents establishing recurring orders with suppliers. two different things. Coverage: meal kits, box-of-the-month, beverage co-packers, pet food autoship, office-supply autoship, maintenance contracts, software seat top-ups. Take-rate: 2% on recurring orders + Pro tier. **Greenfield (W2 build).**

### 6.5.4 Booking / Scheduling ⭐ (the highest-ROI primitive)

`search` (find available slots) → `reserve` (hold slot, default TTL 5 min) → `settle` (confirm + pay deposit). Modify and cancel are extensions. Largest single-primitive TAM expansion in the entire plan: **~7M US establishments**. Coverage: trades (plumbers, HVAC, electricians, locksmiths), personal services (salons, spas, tattoo studios), healthcare (dentists, vets, telehealth, with HIPAA gating via Credentialed overlay), professional (lawyers, accountants, consultants, photographers), fitness/wellness (yoga, gyms, personal trainers), childcare/education (daycare, tutors, camps), food/drink (restaurant reservations, brewery tours, catering), lodging/travel (hotels, vacation rentals, tour operators), real-estate (property tours), pet services (grooming, boarding, walking). Reference adapters (W1 launch): Square Appointments, Acuity, Calendly. Take-rate: 1–3% per confirmed booking. **Greenfield (W1 build. top priority).**

### 6.5.5 Date-Bound Inventory

Generalizes Booking with multi-day capacity and inventory math. `search(date_range, qty, criteria)` → `reserve` (hold inventory across the date range) → `settle`. Coverage: hotels (Cloudbeds/Mews adapters), vacation rentals, rental cars, equipment rental (skis, kayaks, party supply, construction), self-storage, seasonal perishables (CSAs, holiday produce), co-working spaces, sports venue bookings. Take-rate: 2–5%. **Greenfield (W2 build, depends on Booking infrastructure).**

### 6.5.6 Auction / Dynamic Price

`search` (list active auctions) → `place_bid(amount, max_bid?)` (server runs proxy bidding) → outbid notifications via webhooks → `settle` on win. Anti-sniping extensions configurable. Coverage: marketplaces (eBay-tier, Whatnot, Mercari), vertical collectibles (StockX, GOAT, Reverb, Discogs, TCGplayer, PWCC), fine art / luxury (Sotheby's, Christie's, Heritage, Bonhams), wine (WineBid, Acker), industrial (Ritchie Bros, Copart, GovDeals), domain auctions, B2B commodities (with Credentialed overlay), charity auctions. Out of scope: sports betting, online gambling, live ad-exchange RTB, regulated derivatives trading. Take-rate: 0.5–2%. **Greenfield (W4 build).**

### 6.5.7 Quote / RFQ / Negotiation

`submit_rfq(spec, attachments)` → seller `rfq_quote(price, terms, valid_until)` → buyer `accept_quote` or `counter_quote(terms)` → on accept, `settle`. Async by nature; SLA-bound by `RFQ-Response-SLA-Hours`. Coverage: custom manufacturing (CNC shops, PCB fabs, 3D printing, sheet metal, injection molding), industrial supply (quote-driven tier of McMaster-Carr/Grainger), specialty chemicals, food/beverage co-manufacturers, freight/logistics (LTL/FCL brokers), B2B services (custom catering, conference AV, large-scale printing, corporate gifts), commercial real estate, insurance brokers, custom apparel, trade shows, custom software dev shops, printing/publishing, construction trades (custom estimates), automotive/marine/aviation custom services. Take-rate: $0.50–$2.00/quote + 1–2% on accepted. **Greenfield (W3 build). upmarket extension of the F&B supplier wedge.**

### 6.5.8 Credentialed / Regulated (gating overlay, not a transactional primitive)

**Not a separate transactional primitive**. a gating layer that wraps any of primitives 1–7. Per-site `regulated_gates` (`age:21`, `jurisdiction:US-CA`, `license:dea`, `kyc:full`, `prescription:rx`). All transactional MCP tools across primitives 1–7 check gates BEFORE executing; reject with `403 GATE_FAILED { reason, required_proof_kind, accepted_issuers }` if proof is missing. Facet **never holds** the regulated proof. only the attestation that an authorized issuer has verified it. In-scope verticals: cannabis dispensaries (state-by-state), alcohol delivery, tobacco/vape, firearms accessories (NOT firearms transfer. FFL gauntlet), nutraceuticals, age-gated content, prescription pet meds, B2B precursor chemicals (DEA list). Out-of-scope: brokerages/banks, gambling/sports betting, healthcare PHI as covered entity, government form submission, firearms transfer. Take-rate: 2–5% premium on regulated transactions. **Greenfield (W3 build).**

### 6.5.9 View + Handoff (UBI-only / non-transactional)

A business with a UBI listing but **no transactional verbs activated**. agent reads info, returns it to a human (or summarizes for downstream task), no money or commitment changes hands. `get_listing(ubi_id)` returns full UBI baseline (NAP+, hours, license, photos, reputation). `request_handoff(method)` returns click-to-call URL, directions, copy-to-share, mailto, or SMS template. Coverage: cafes, bars, walk-in retail, mom-and-pop shops, food trucks, farm stands, religious institutions, civic/public goods (libraries, parks, ATMs, EV charging, transit), cultural/historical (museums info-only baseline), info-only sites (personal blogs, OSS projects, docs sites, government info). ~25% of all businesses with web/maps presence fit here. Take-rate: $0–$5/mo claim subscription only. **Greenfield (W0 build alongside UBI baseline).**

### 6.5.10 Universal Business Index (foundation, not a primitive)

The substrate every primitive runs against. Append-mostly directory of every business with any web/maps/social presence (~65–80M globally), seeded from OpenStreetMap (ODbL backbone), state license registries (TX/CA/FL/NY DOL plumbing/electrical/contractor), USDA/FDA establishment registries (FSMA 117 food facilities), Crunchbase (SaaS), GuideStar (nonprofits), Google Places (enrichment-only for claimed listings). Owner-claim flow: unclaimed → claimed_unverified (postcard/phone OTP) → verified_owner (DNS/GMB OAuth) → kyc_verified (Stripe Connect KYC). Each tier unlocks more primitive activation. Anti-gaming: agent reputation scores tied to KYA identity + on-chain payment proof, fundamentally harder to fake than human Yelp reviews. See `docs/founding/UBI_MODEL.md` for the full schema, ingestion pipeline, claim flow, and reputation system.

### 6.5.11 Knowledge Graph Layer (UBI substrate, added v1.2)

The relational shape of UBI answers "find me businesses near 75002 with NAICS 238220." It does not answer "find me a Brenntag substitute in DFW that supplies the same SKUs **and** carries the same FSMA-204 compliance posture," or "trace the 2-hop supply chain from this co-manufacturer to its packaging vendors and audit any with disputed agent reputation." Those are graph queries. typed-edge traversal and embedding-similarity nearest-neighbor. not row-filter SQL.

The knowledge graph layer adds both as a thin substrate over `universal_business_index` (no duplication of business data, no new authoritative directory). Three new Postgres tables -- `kg_nodes`, `kg_edges`, `kg_reports` -- form the graph substrate, with `org_id` and `access_level` dropped (Facet is single-tenant at the DB level today) and a `kg_nodes.ubi_id` foreign key that lets business nodes link 1:1 to UBI rows. Pgvector embeddings (`text-embedding-3-small`, 1536-dim, IVFFlat lists=200) support `facet_kg_match_nodes` for semantic search; a recursive BFS RPC `facet_kg_traverse` supports N-hop walks across typed relations (`supplies`, `licensed_by`, `located_in`, `complies_with`, `same_naics`, `same_zip`, `same_corridor`, `competes_with`, `derived_from`, `semantically_similar_to`, `references`, `cites`, `owns`).

Five ingestion paths populate the graph, each with its own `source` tag for dedup and rollback: (1) **UBI backfill**. one node per `universal_business_index` row, `node_type='business'`; (2) **derived structural edges**. `same_naics` / `same_zip` / `licensed_by` / `located_in` computed entirely from existing UBI columns; (3) **concept extraction from founding docs** via `gpt-4o-mini` against `UBI_MODEL.md`, `PRIMITIVES.md`, this whitepaper, and the architecture doc; (4) **regulatory concepts**. FSMA-204 / NAICS-7 / OSM-tag-vocab / state-licensing-board concept layer; (5) **semantic embeddings**. daily refresh, ~$1 per 1M nodes one-shot.

Three Terminal Edge Function endpoints expose the graph to agents (auth via the same `requireSiteRole` site-role pattern that protects every other Terminal route. never Origin/Referer): `POST /v1/graph/match` for semantic search ("find me businesses similar to X"), `GET /v1/graph/related` for hop-bounded neighborhood retrieval ("show me 2-hop substitutes filtered by `same_naics` + `licensed_by`"), and `GET /v1/graph/path` for bidirectional reachability ("is supplier X reachable from buyer Y in ≤4 hops"). Rate-limits 30/min and 60/min per token.

What the graph unlocks for agents: substitute discovery that crosses NAICS boundaries (embedding ANN), supply-chain trace with provenance per hop, FSMA-204 compliance audit by reachability to a regulation concept node, geo-cluster expansion beyond bounding-box queries, cold-start reputation inheritance from semantically-similar verified peers, and founding-doc semantic Q&A. None of this is exposed via direct Postgres reads. every graph query is mediated by a Terminal endpoint with the same RLS posture and rate-limit discipline as every other Facet primitive.

Schema details, RPC signatures, ingestion adapters, and phasing in `UBI_MODEL.md` §6.5; file-by-file execution plan in `tasks/facet-graphify-integration-plan-2026-05-01.md`. v1 ships in seven phases (schema → backfill → embed → derive → concepts → query RPCs → Terminal endpoints); v1.1 adds an admin browser and a daily scheduled rebuild.

### 6.5.12 Coverage at end of plan

| Bucket (% of ~70M global) | Primary primitive | Coverage state |
|---|---|---|
| Transactional w/ structured commerce (~3%) | Catalog | ✅ Today |
| Bookable services (~12%) | Booking | ✅ after W1 |
| Quote-driven B2B (~5%) | RFQ | ✅ after W3 |
| Walk-in / call-only (~25%) | View+Handoff | ✅ after W0 |
| Info-only / docs / OSS (~30%) | UBI directory | ✅ after W0 |
| Civic / public goods (~10%) | UBI directory | ✅ after W0 |
| No website (social/maps-only ~15%) | UBI w/ social ingestion | ✅ after W5 |
| Subscriptions / cadence (~1%) | Subscription | 🟡 → ✅ after W2 |
| Paywalled content (~2%) | Paywall | 🟡 → ✅ after W4 |
| Date-bound inventory (~3%) | Date-Bound | ✅ after W2 |
| Auction (~1%) | Auction | ✅ after W4 |
| Regulated overlay (~4%) | Credentialed | ✅ after W3 |

**Total coverage at end of plan: ~95%** of all businesses with web/maps/social presence have a Facet primitive that fits their shape. The remaining ~5% are explicitly out-of-scope (finance, gambling, healthcare PHI, gov submission, firearms transfer) per per-primitive DON'T-BUILD lists in `PRIMITIVES.md` §4.

---

## 7. agents.txt v0.2. Thin Discovery Manifest

> **v1.1 update (2026-04-30):** the manifest spec has bumped to v1.1 with new top-level field `Capabilities:` declaring which of the 8 archetype primitives the supplier has activated, plus optional sections `[business_index]`, `[booking]`, `[auction]`, `[rfq]`, `[regulated]` for primitive-specific config. Backward-compat clause: v1.1 parsers MUST parse v1.0 + v0.2 docs unchanged. See `specs/agents.txt-v1.1.md` for the full spec; this section retains the v0.2 reference for archive purposes.

The `agents.txt` file Facet publishes is a **thin discovery manifest**, not a competing permissions standard. It declares where to find the supplier's Terminal, which KYAPay issuers the supplier trusts, and F&B-specific pricing hints. Actual permissions enforcement happens at the Terminal against the KYAPay token; `agents.txt` is a pointer. This is a deliberate retirement of Facet's earlier v0.1 "declarative permissions standard" ambition, given that KYAPay + RFC 9421 already occupy the permissions-and-auth space with real institutional weight.

**Format.** Plain text, UTF-8, line-based. `Key: Value` pairs. Lines beginning with `#` are comments. Sections delimited by `[section-name]` headers (optional; defaults apply if omitted). Unknown `[section]` headers are ignored by v0.2 parsers to enable forward compatibility.

**Required fields (top-level).**

| Field | Type | Semantics |
|-------|------|-----------|
| `Facet-Version` | string | Specification version. Current is `0.2`. |
| `Terminal` | URL | Absolute URL to the Facet Terminal endpoint for this domain. |
| `KYA-Issuers` | URL list | Comma-separated URLs of KYAPay-compliant issuers the supplier trusts. The Terminal validates incoming tokens against these issuers' JWKS. |

**Optional fields (top-level).**

| Field | Type | Semantics |
|-------|------|-----------|
| `Pricing-Hint` | string list | Advisory per-request and per-transactional rates; binding rates are set at the Terminal and surfaced in `quote` responses. Example: `0.001 USDC/query, 0.01 USDC/transactional`. |
| `Rate-Limit` | string | Default rate limit; negotiable per operator. Format: `<count>/<interval>`. Example: `1000/hour`. |
| `Alt-Identity` | enum | If present, declares an alternate identity path the Terminal supports (e.g. `DID`). Off by default. |
| `Reputation-Minimum` | integer | 0–100 threshold against Facet's Agent Reputation Registry. Agents below the threshold are refused. |
| `Contact` | string | Human contact for supplier operator. |

**Example 1 -- Retail florist with same-day in-zone delivery (Hill Country Flowers, Austin TX).**

```
# /.well-known/agents.txt
Facet-Version: 0.2
Terminal: https://facet.hillcountryflowers.com/v1
KYA-Issuers: https://issuer.skyfire.xyz, https://kya.hillcountryflowers.com
Pricing-Hint: 0.001 USDC/query, 0.01 USDC/transactional
Rate-Limit: 5000/hour
Reputation-Minimum: 70
Contact: agents@hillcountryflowers.com
```

**Example 2 -- Neighborhood restaurant with reservations and preorder (Tony's Trattoria, North Beach SF).**

```
# /.well-known/agents.txt
Facet-Version: 0.2
Terminal: https://facet.tonystrattoria.com/v1
KYA-Issuers: https://issuer.skyfire.xyz
Pricing-Hint: 0.005 USDC/query, 0.05 USDC/transactional
Rate-Limit: 500/hour
Reputation-Minimum: 85
Contact: reservations@tonystrattoria.com

[booking]
Slot-TTL-Seconds: 600
Cancellation-Window-Hours: 4
Party-Size-Max: 12
```

**Example 3 -- Independent auto-repair shop with service slots and DID alternate path (Stevens Auto Service, Brooklyn NY).**

```
# /.well-known/agents.txt
Facet-Version: 0.2
Terminal: https://facet.stevensauto.com/v1
KYA-Issuers: https://issuer.skyfire.xyz
Alt-Identity: DID
Pricing-Hint: 0.002 USDC/query, 0.02 USDC/transactional
Rate-Limit: 2000/hour
Reputation-Minimum: 75
Contact: shop@stevensauto.com

[booking]
Slot-TTL-Seconds: 300
Loaner-Available: true
Diagnostic-Required: false
```

---

## 8. Transaction Flow. Four Atomic Verbs

> **v1.1 framing note:** these four verbs are the **atomic transaction layer** that powers all 8 business-archetype primitives in §6.5. Catalog uses all four. Paywalled Content uses search + quote + settle (no reserve). Booking uses search (slot-find) + reserve (slot-hold) + settle (confirm). Auction uses search + place_bid (extension of reserve) + settle on win. RFQ uses submit_rfq (extension of search) + counter + accept (extension of quote) + settle. Subscription uses settle×N on cron after initial setup. The verbs are primitive-agnostic; the primitives compose them with archetype-specific semantics. See §8.5 for the per-primitive verb-extension table.

The commerce surface exposes four idempotent, signed primitives: `search`, `quote`, `reserve`, `settle`. Each is an MCP tool call (JSON-RPC over HTTPS) and can also be expressed as a REST endpoint. Examples below use the REST form for readability; the JSON-RPC form is symmetric.

### 8.1 search

```
POST /v1/search HTTP/1.1
Host: facet.hillcountryflowers.com
Authorization: Bearer <agent-jwt>
Content-Type: application/json

{
  "query": "tulip arrangement under $125, sympathy occasion",
  "filters": {"delivery_zone": "austin-78704", "delivery_by": "2026-05-08T17:00:00Z"}
}
```

Response includes product IDs and ephemeral quote tokens.

### 8.2 quote

```
POST /v1/quote HTTP/1.1
Host: facet.hillcountryflowers.com
Authorization: Bearer <agent-jwt>
Content-Type: application/json

{"product_id": "SKU-TULIP-MED", "delivery_zone": "austin-78704", "delivery_by": "2026-05-08T17:00:00Z"}
```

Response: price, availability window, reservation token (TTL 60 seconds), `X-Facet-Signature` header.

### 8.3 reserve

```
POST /v1/reserve HTTP/1.1
Host: facet.hillcountryflowers.com
Authorization: Bearer <agent-jwt>
Content-Type: application/json

{"quote_token": "qt_abc123..."}
```

Response: reservation ID, settlement intent with x402 payment details, TTL 300 seconds.

### 8.4 settle

Includes an x402 payment proof in the `X-Payment` header.

```
POST /v1/settle HTTP/1.1
Host: facet.hillcountryflowers.com
Authorization: Bearer <agent-jwt>
X-Payment: <x402-payment-proof>
Content-Type: application/json

{"reservation_id": "rsv_xyz789..."}
```

Response: signed receipt, order ID, fulfillment details.

### 8.5 x402 payment proof handling

The `reserve` response includes an HTTP 402 Payment Required directive with the destination address, amount, and chain (Base L2, USDC). The agent's wallet (Coinbase AgentKit or equivalent) constructs the payment, obtains proof from the Base RPC, and submits it in the `X-Payment` header of the `settle` call. The Terminal verifies the proof against the expected amount and destination before finalizing.

**Protocol detail note.** The exact x402 proof format continues to be specified by Coinbase. The format above reflects 2025 reference implementations; production Facet will track the specification as it stabilizes rather than freezing an invented encoding. Implementers should consult the latest x402 reference at the time of integration.

Each primitive is idempotent by reservation token or payment proof. Duplicate calls with the same token return the same result without side effects. This is critical for agent retry behavior under network partition.

---

## 8.5 Archetype-Specific Verb Constraints (added v1.1)

Each of the 8 business-archetype primitives from §6.5 composes the four atomic verbs differently. This section documents the per-archetype constraint table. what's required, optional, extended, or forbidden. so an agent SDK can validate per-primitive call shapes statically.

| Primitive | search | quote | reserve | settle | Archetype-specific tools | Notes |
|---|---|---|---|---|---|---|
| **Catalog** | ✅ required | ✅ required | ✅ required (TTL: 5 min default) | ✅ required (x402 payment proof) | `get_product`, `get_order`, `refund_request`, `order_history` | Original primitive. All four verbs idempotent by reservation token. |
| **Paywalled Content** | ✅ required (catalog of scopes) | ✅ required (price discovery per scope) | ❌ omitted (instant access) | ✅ required (settle == grant license) | `quote_license`, `purchase_license`, `consume_license` | No reserve because access is instant on payment. `consume_license` increments usage counter against the purchased scope. |
| **Subscription / Cadence** | ✅ optional (reuse catalog search) | ✅ required (initial pricing) | ✅ optional (initial slot if applicable) | ✅ required ×N (cron-triggered after profile creation) | `create_subscription`, `pause_subscription`, `skip_next_run`, `cancel_subscription`, `modify_subscription_lines` | Initial flow = standard 4 verbs. Subsequent runs auto-trigger settle on cron without re-confirmation. |
| **Booking / Scheduling** | ✅ required (`find_slots(resource, date_range, party_size)`) | ✅ optional (price quote per slot) | ✅ required (`hold_slot(slot_id, hold_seconds)`. TTL bound by `Hold-Duration-Seconds` manifest field) | ✅ required (`confirm_booking(hold_token, payment_proof)`. applies deposit) | `find_slots`, `hold_slot`, `confirm_booking`, `modify_booking`, `cancel_booking` | Search = slot search. Reserve = slot hold. Settle = confirm booking. |
| **Date-Bound Inventory** | ✅ required (`find_inventory(date_range, qty, criteria)`) | ✅ required | ✅ required (multi-day hold) | ✅ required | `find_inventory`, `reserve_inventory`, `confirm_inventory_booking` | Generalizes Booking with date-range capacity. Inventory math (room types, party-size constraints, length-of-stay rules) handled by per-strategy adapter. |
| **Auction** | ✅ required (`list_auctions(filters)`) | ✅ optional (`get_auction(id)` returns current bid) | ✅ implicit (bid ≡ reservation contingent on win) | ✅ required (settle on win) | `list_auctions`, `get_auction`, `place_bid(amount, max_bid?)`, `get_bid_status` | Reserve replaced by `place_bid` with server-side proxy logic (max-bid). Anti-sniping extensions extend `ends_at` on late bids per `Anti-Sniping-Extension-Sec` manifest field. Webhooks: `auction.bid_outbid`, `auction.ending_soon`, `auction.won`, `auction.lost`. |
| **Quote / RFQ** | ✅ optional (catalog browse before RFQ) | ❌ replaced by `submit_rfq + counter_quote` | ✅ optional (deposit hold on accepted quote) | ✅ required | `submit_rfq(spec, attachments)`, `get_rfq_status`, `accept_quote`, `counter_quote(terms)`, `cancel_rfq` | Async by nature; quote is human-issued by supplier admin (or supplier's own automation). SLA bound by `RFQ-Response-SLA-Hours` manifest field. |
| **Credentialed (overlay)** | ✅ pre-checked (gate enforcement) | ✅ pre-checked | ✅ pre-checked | ✅ pre-checked | none new. overlays primitives 1–7 | All transactional verbs across primitives 1–7 check `regulated_gates` BEFORE executing. Reject with `403 GATE_FAILED { reason, required_proof_kind, accepted_issuers }` if `kya_proof_attestations` missing/expired/wrong-issuer. |
| **View + Handoff** | ❌ omitted (browse via UBI directory API) | ❌ omitted | ❌ omitted (no transactions) | ❌ omitted | `get_listing(ubi_id)`, `request_handoff(method)` | UBI-only listings expose only directory + handoff. No money or commitment changes hands. |

**Implementation pattern.** Each MCP tool registers in `services/terminal/src/handler.ts` ROUTES map under the primitive's namespace (e.g. `/v1/booking/find-slots`, `/v1/auction/place-bid`). The Terminal validates the calling site's `Capabilities:` declaration before dispatching: a call to `/v1/booking/find-slots` against a site that hasn't declared `booking` ∈ `Capabilities` returns `400 INVALID_REQUEST { code: "primitive_not_active" }`. This prevents typos + ensures the manifest is always the source of truth for what's available.

**Webhook events extension (v1.1):**
- `booking.confirmed`, `booking.cancelled`, `booking.modified`
- `auction.bid_outbid`, `auction.ending_soon`, `auction.won`, `auction.lost`
- `rfq.received` (supplier-side), `rfq.quoted`, `rfq.accepted`
- `subscription.run.settled`, `subscription.run.failed`
- `gate.failed` (Credentialed overlay)

All idempotent via the same reservation-token / payment-proof rules from §8. duplicate webhook deliveries return the same event ID, agents dedupe at their handler.

**Composition example (F&B co-manufacturer with all 4 archetypes active):**
```
Capabilities: catalog, quote-rfq, paywalled-content, credentialed
Regulated-Gates: license:dea, kyc:basic
RFQ-Response-SLA-Hours: 48
```

Agent calls supported in this configuration:
- `search` / `get_product` / `quote` / `reserve` / `settle` (Catalog, gated by DEA license)
- `quote_license` / `purchase_license` / `consume_license` (Paywalled Content for spec sheets)
- `submit_rfq` / `accept_quote` / `counter_quote` (RFQ for custom batch orders)
- `subscribe_webhook` for any of the above + RFQ-specific events
- All transactional calls require `kya_proof_attestation` for `license:dea` + `kyc:basic` before executing

Per-primitive deep-dive: see `docs/founding/PRIMITIVES.md`.

---

## 9. Identity, Signatures, Provenance

### 9.1 KYAPay-primary agent identity

Facet adopts **KYAPay** (Skyfire's IETF Independent Submission, co-authored by Mike Jones of RFC 7515/7519 authorship) as the primary agent identity rail. An agent operator mints one of three token types. `kya+jwt` (identity only), `pay+jwt` (payment only), or `kya-pay+jwt` (combined). against a KYAPay-compliant issuer. The token is an ES256 JWT carrying claims for agent identity (`aid`), agent platform (`apd`), audience binding (`aud`), expiry, nonce, and a settlement-type claim (`stp`) that selects between `coin` (USDC) or `card` (Visa VIC, Mastercard SCOF) when the token is payment-capable.

Facet's Identity Gateway verifies each incoming token by: issuer pinning against the supplier's `agents.txt` `KYA-Issuers` allow-list, JWKS public-key fetch from the issuer's `/.well-known/jwks.json`, ES256 signature verification, audience binding check, temporal (`exp`/`nbf`) check, and replay-nonce check. JWKS is cached for five minutes; revocation is polled per issuer policy. The `aid` and `apd` claims feed Facet's Agent Reputation Registry for per-operator scoring and rate-limit resolution.

### 9.2 DID-based agent identity (optional alternate path)

For crypto-native agent operators that cannot use a KYC-issued KYA token, Facet supports a fallback mechanism based on W3C Decentralized Identifiers. The agent operator publishes a DID document at `.well-known/did.json` on their domain; the DID document contains one or more public keys and metadata. Facet resolves DIDs by HTTP GET on the operator's `.well-known/did.json`, caches the resolution for 5 minutes, and checks a revocation list at 60-second intervals.

Each agent session on this path carries a JWT signed by the operator's key. The JWT claims include the DID subject (the specific agent instance), the principal (the customer on whose behalf the agent is acting, if applicable), expiry, and nonce. Facet verifies the JWT signature against the cached DID document on every request. This path is feature-flagged per supplier via the `Alt-Identity: DID` directive in `agents.txt`, disabled by default, and recommended only when a specific agent-operator relationship justifies the alternative.

### 9.2 Ed25519 response signatures

Every Facet Terminal response includes an `X-Facet-Signature` header:

```
X-Facet-Signature: ed25519 <base64url-signature>; key=<kid>; ts=<timestamp>
```

The signature input is the concatenation of three hashes and a timestamp:

```
signature_input = sha256(canonical_request) || sha256(response_body) || timestamp
```

where `canonical_request` is the method, URL, sorted headers, and body in a canonical form; `response_body` is the raw response bytes; and `timestamp` is an RFC 3339 string.

### 9.3 JWKS and key rotation

Public keys are published at `/.well-known/facet-keys.json` as a JWKS (JSON Web Key Set):

```json
{
  "keys": [
    {
      "kty": "OKP",
      "crv": "Ed25519",
      "kid": "facet-hillcountry-2026-q2",
      "x": "<base64url-public-key>",
      "created": "2026-04-01T00:00:00Z",
      "expires": "2027-04-01T00:00:00Z"
    }
  ]
}
```

Keys rotate quarterly. Old keys remain in the JWKS for 365 days after expiry to support late verification of cached responses.

### 9.4 Verification (language-agnostic pseudocode)

```
function verify_facet_response(request, response, signature_header):
    sig, kid, ts = parse(signature_header)
    if abs(now() - ts) > MAX_CLOCK_SKEW:
        return INVALID_TIMESTAMP
    pubkey = fetch_jwks_key(request.host, kid)
    if pubkey is None:
        return UNKNOWN_KID
    if pubkey.expired_more_than(365_days_ago):
        return EXPIRED_KEY

    req_hash = sha256(canonical(request))
    resp_hash = sha256(response.body)
    input = concat(req_hash, resp_hash, ts)

    if ed25519_verify(pubkey, input, sig):
        return VALID
    return INVALID_SIGNATURE
```

### 9.5 Chained-agent provenance

An agent that receives a Facet response and forwards derived data to a downstream agent can attach the original signature as provenance. The downstream agent can verify the signature against the original origin's JWKS and confirm that the data was not fabricated or stale beyond the signature's timestamp window. This is the mechanism by which a multi-hop agent chain produces verifiable output without requiring each intermediate agent to be trusted.

---

## 10. Reference Architecture

Facet runs as a set of Netlify-fronted subdomains under `facet.llc`, with the data plane on a dedicated Supabase project. Each supplier's Terminal is exposed at a per-supplier subdomain (e.g. `facet.hillcountryflowers.com`, the retail-florist reference deployment) CNAMEd to a shared multi-tenant Edge Function; suppliers do not host any infrastructure. Edge Functions run on Deno under Supabase Functions.

```
                          Agent Request
                               |
                               v
                +-----------------------------+
                |  facet.hillcountryflowers   |
                |  .com (Terminal, CNAMEd     |
                |  to shared edge)            |
                |  Deno Edge Function         |
                |  - KYAPay JWT verify (ES256)|
                |  - Rate limiter             |
                |  - Meter                    |
                |  - Dispatcher               |
                +-----------------------------+
                               |
                +--------------+--------------+
                v              v              v
        +-------------+ +-------------+ +-------------+
        |  Catalog    | |  Commerce   | |  Analytics  |
        |  Primitives | |  Primitives | |  Ingestion  |
        +-------------+ +-------------+ +-------------+
                               |
                               v
                +------------------------------+
                |  Supabase Postgres (Facet)   |
                |  suppliers, agents, sessions |
                |  events, orders, signatures  |
                +------------------------------+
                               |
                               v
                +------------------------------+
                |  Facet Knowledge Graph (UBI) |
                |  9.4M+ business records,     |
                |  pgvector + typed edges      |
                +------------------------------+

  Operator surfaces, hostname-routed at the edge:
    facet.llc                 -- marketing
    facet.<supplier>.com      -- terminal (per-supplier CNAME, see above)
    app.facet.llc             -- operator admin (Next.js)
    audit.facet.llc           -- public audit log Edge Function
    dataroom.facet.llc        -- investor data room
```

The Facet Knowledge Graph (the Universal Business Index, UBI) is the cross-product integration point. Every terminal event -- query, quote, reservation, settlement -- emits a structured record into UBI. The operator dashboard at `app.facet.llc` reads UBI for supplier graph views, compliance intelligence, and procurement analytics. The dashboard does not touch the terminal's operational store directly; it reads UBI, which preserves tenant isolation by construction.

---

## 11. Comparison to Alternatives

Facet does not treat KYAPay, MCP, x402, or RFC 9421 as alternatives. those are the rails Facet adopts. This section compares Facet against the genuine alternatives a supplier or agent operator might consider *instead of Facet-plus-those-rails*.

### 11.1 Raw MCP alone

MCP is a protocol; Facet is a hosted vertical product layered above MCP. Raw MCP alone is free but requires each supplier to operate their own MCP server, integrate KYAPay verification independently, implement metering, wire up the commerce primitives from scratch, and instrument analytics on their own. Raw MCP suits suppliers with strong in-house engineering who want full control. Facet wins for the long tail. every F&B supplier who will not hand-roll the KYAPay integration, the schema generator, or the publisher-side analytics.

### 11.2 OpenAPI gateways (Kong, Apigee, RapidAPI)

API gateways solve human-developer integration: OAuth, API keys, per-month billing, REST-centric schemas. Agents are not developers. A retrofitted API gateway ends up with an identity model (API keys) that cannot enforce revocation cleanly, a billing model (monthly subscription) that does not fit per-query agent economics, and a schema model (OpenAPI alone) that misses MCP-native capabilities. Gateways win for traditional API-first businesses; they do not win for agent-native F&B.

### 11.3 Headless-browser scraping

The scraping stack (residential proxies, CAPTCHA solvers, Chromium automation) has a working business model today. It fails on the five axes in §2. Scraping wins as long as suppliers do not stand up terminals; the moment they do, the scraping cost stack collapses against a simple HTTP call authenticated by a KYAPay token. Facet's adoption loop is the forcing function that makes scraping economically irrational for Facet-enabled F&B suppliers.

### 11.4 Horizontal agent-commerce platforms (Skyfire direct, Tollbit, Stripe Agent Pay)

These are the protocol rails or adjacent horizontal plays, not vertical alternatives. Skyfire-direct is Facet's identity and settlement rail, not its competitor. Tollbit covers publisher micropayments and is complementary on the publishing side (Facet does not pursue publishing). Stripe Agent Pay is a card-rail option that KYAPay already abstracts over. A supplier choosing any of these directly gets a horizontal primitive with no F&B schema generator, no publisher-side agent analytics, no F&B-calibrated reputation, and no Ed25519 response-signing layer. Facet provides those on top.

### 11.5 Closed enterprise APIs

Large ingredient distributors and co-manufacturers already expose APIs. EDI, custom REST, occasional GraphQL. These are closed: no standard identity model, no cross-vendor discovery, no agent-friendly schema. They win for the enterprise buyer who already has the relationship and the integration contract. They lose for the long-tail agent trying to discover suppliers it has no prior contract with. Facet provides the discovery plus negotiate plus transact surface that closed APIs do not. on top of KYAPay-verified identity that the closed enterprise-API stack does not speak.

---

## 12. Economic Model

### 12.1 Two-sided marketplace

Suppliers pay on the product side; agent operators route transactions through the commerce side; Facet collects subscription from suppliers plus take-rate on transactions. The suppliers are the paying side; agent operators are the demand side that makes the supplier side worth paying for.

### 12.2 Site ROI. worked examples

Two worked examples, one F&B supplier and one D2C merchant, to show the economics are substrate-agnostic.

**Example A. mid-market F&B ingredient distributor.** 1,000,000 agent queries per month and 20 agent-originated transactions per month averaging $2,000 each.

| Line item | Value | Source |
|-----------|-------|--------|
| Pre-Facet bandwidth cost attributable to agent traffic | -$400/mo | Supplier's Cloudflare bill, agent-bot share |
| Pre-Facet bot-defense licensing (Cloudflare Bot Management Pro) | -$200/mo | Published Cloudflare pricing |
| Pre-Facet revenue from agent traffic | $0 | Unmetered |
| Facet Pro subscription | -$299/mo | List price |
| Facet metered revenue (1M queries × $0.001 × 70% supplier share) | +$700/mo | Assumption: metering activated |
| Facet commerce take-rate (supplier share of 20 × $2K × 98%) | +$39,200/mo | Assumption: 20 transactions/mo |
| **Net supplier delta** | **+$39,801/mo** | Sum |

Payback: immediate. Even without commerce activation, metering plus bandwidth-and-bot-defense savings justify Pro tier.

**Example B. mid-market D2C merchant on Shopify Plus.** 400,000 agent queries per month (research-heavy pre-purchase agent traffic), 150 agent-originated transactions per month averaging $85 each.

| Line item | Value | Source |
|-----------|-------|--------|
| Pre-Facet bot-defense licensing | -$150/mo | Shopify's bot-protection add-on |
| Pre-Facet revenue from agent traffic | $0 | Unmetered |
| Facet Pro subscription | -$299/mo | List price |
| Facet metered revenue (400K queries × $0.001 × 70% merchant share) | +$280/mo | Assumption: metering activated |
| Facet commerce take-rate (merchant share of 150 × $85 × 98%) | +$12,495/mo | Assumption: 150 transactions/mo |
| **Net merchant delta** | **+$12,326/mo** | Sum |

Payback: immediate. The ROI mechanics are identical across segments because the underlying economics. bandwidth saved, scrapers refused, good agents paid. do not depend on what the site sells.

### 12.3 Agent-operator ROI

An agent operator (for example, a procurement agent running on behalf of an enterprise buyer) pays $0.001 per query and transaction fees. Pre-Facet alternative: scraping with residential proxies at approximately $5–$10 per 1,000 requests, plus CAPTCHA-solving at approximately $2–$5 per 1,000 solves, plus headless Chrome compute. Post-Facet: $1 per 1,000 queries, no proxies, no CAPTCHAs, and structured responses that eliminate parsing cost. The net effect on the agent operator is a 5–10x reduction in cost per data-acquisition event at the scale of Facet-enabled suppliers.

---

## 13. Adoption Funnel

The post-scraping substrate has one structural problem every similar category has faced before it: **the site operator does not know how much traffic they are already absorbing**. Bandwidth, compute, and structured-data extraction flow out of a commercial site every day without the operator seeing who took what or what it was worth. Awareness is the first barrier, not price, features, or protocol maturity.

### 13.1 The asymmetric-information opening move

Every shock-and-awe sales motion in adjacent infrastructure categories. phishing simulation (KnowBe4), external vulnerability scanning (Qualys), bot-traffic intelligence (Cloudflare AI Audit). opens the same way: a free classified report that makes an invisible problem visible on the customer's own data. Facet opens with the equivalent for agent traffic.

### 13.2 The Agent Traffic Audit

The Agent Traffic Audit is a free, consent-first, locally-classified 30-day report that tells a site operator which AI operators are already hitting their site, what was extracted, and how much that traffic would be worth under Facet's pricing tiers (full technical spec in the accompanying `AGENT_TRAFFIC_AUDIT.md` doc). Three properties make it compound across hundreds of deployments:

1. **Consent-first.** The classifier is Apache-2.0 licensed and runs by default inside the site operator's own environment. a Cloudflare Worker, a WordPress plugin, a Vercel edge adapter, or a Docker sidecar. Raw request logs never leave the operator's infrastructure. Only aggregated, CIDR-level classifications flow to Facet, and only when the operator explicitly enables that path.
2. **No scraping of the prospect.** The report is built from the operator's own logs plus public operator fingerprints (published IP ranges and user-agent patterns from Anthropic, OpenAI, Google, Perplexity, and community-curated registries), never from Facet-operated crawlers hitting the prospect's site. The audit's credibility and Facet's brand integrity both depend on this rule.
3. **Signed and auditable.** Every report carries an Ed25519 signature (§9.4) and the classifier is open-source, so the operator can independently verify that the numbers came from Facet and were not edited in transit.

A typical report classifies 30 days of traffic into named operators. Anthropic Claude, OpenAI Operator/GPTBot, Google Gemini / Mariner, Perplexity Sonar, Meta AI, and the long tail of unidentified residential-proxy and datacenter scrapers. and projects the revenue-at-tier that traffic would produce under Facet metering. For a typical mid-market F&B ingredient distributor, the report shows 100K+ agent requests per month at $145–$2,340 per month in projected Facet revenue, of which approximately zero is currently monetized.

### 13.3 Compounding loops

The audit is not a one-off pitch artifact. It is the first free product Facet ships and the top of a self-reinforcing funnel:

- **Audit → Terminal install.** The operator installs the Facet Terminal to monetize the same traffic the audit classified. Phase 1 target: ≥ 30% of audit recipients install within 21 days.
- **Terminal install → Fingerprint Registry contribution.** Every KYAPay-authenticated agent query inside an installed Terminal produces a verified operator fingerprint. With the operator's opt-in consent and anonymization, those fingerprints feed back into the public Fingerprint Registry, making subsequent audits more accurate.
- **More accurate audits → higher shock coefficient → more installs.** The classifier gets better as adoption compounds, which tightens the report's precision, which strengthens the next cohort of audits. Each new Terminal deployment improves the free product that brings in the next ten.

No competitor scraping-defense product produces this compounding loop because none of them are simultaneously the measurement product and the monetization product.

### 13.4 Distribution paths

Phase 1 ships the Cloudflare Worker deploy and the direct NDJSON upload. the two paths with the shortest time-to-report. Phase 2 adds a Shopify App Store listing, a WordPress.org WooCommerce plugin, a Vercel / Netlify edge adapter, and an enterprise API ingest path for operators that stream logs from their own pipelines. Phase 3 extends through edge-CDN partnerships (Cloudflare App Marketplace, Akamai, Fastly) so the audit is discoverable from the same surfaces where operators already pay for bot-traffic visibility. Phase 4 publishes the Fingerprint Registry as a standalone reference-data SKU and contributes it upstream to the KYAPay standards track.

### 13.5 Anti-pattern: the adversarial audit

For completeness, one path Facet explicitly does not take: Facet does not deploy its own scrapers against a prospect's site and send them the evidence. That motion contradicts Facet's own brand promise, opens meaningful legal exposure under trespass-to-chattels, ToS, CCPA, and the EU Data Act, collapses the KYAPay standards-gravity alignment, and is a non-repeatable stunt rather than a compounding loop. Every credible shock-and-awe motion in an adjacent category. KnowBe4, Qualys, Cloudflare AI Audit. is built on consented or public data for precisely these reasons. The Agent Traffic Audit follows the same rule.

---

## 14. Call for Ecosystem Participation

**Agent operators.** If you operate autonomous agents (Claude Code, Operator, Mariner, custom), you are invited to (a) add `agents.txt` parsing to your crawler, (b) support KYAPay-based session authentication (with optional DID alternate), (c) participate in Phase 1 design-partner testing with the first five F&B suppliers. Contact: `ecosystem@facet.llc`.

**Supplier-side integrators.** If you operate PIM, ERP, or catalog software for F&B suppliers (Shopify B2B, NetSuite, Akeneo, custom), the Facet team invites integration conversations. The Schema Auto-Generator reads supplier catalogs; native integration reduces onboarding from minutes to seconds. Contact: `ecosystem@facet.llc`.

**Standards-body reviewers.** `agents.txt` v0.1 is published under Apache 2.0 on the Facet GitHub. Pre-IETF-draft review from W3C and IETF participants is welcome. The goal is formal IETF draft submission by Q4 of the execution plan. Contact: `standards@facet.llc`.

**Reference implementations.** Open-source reference implementations of the `agents.txt` parser, Facet Terminal SDK (Node, Deno, Python), and Ed25519 signature verifier will be published progressively. Track at `github.com/lynz-tonomi/facet` once the public repository ships.

---

## 15. References

Citations below are directionally accurate as of April 2026. URL verification is required before external publication; any marked `[verify]` must be resolved or reformatted as a dated publication citation.

1. Cloudflare Radar. AI Bot Traffic Analytics, Q1 2025 report. *Cloudflare Radar, 2025.* `[verify]`
2. Cloudflare AI Audit announcement. *Cloudflare Blog, 2024.* `[verify]`
3. Cloudflare pay-per-crawl expansion. *Cloudflare Blog, 2024–2025.* `[verify]`
4. Anthropic. Model Context Protocol specification and ecosystem directory. *Anthropic, November 2024 onward.* `[verify]`
5. Coinbase. x402 HTTP Payment Extension specification and reference implementations. *Coinbase, 2024.* `[verify]`
6. The New York Times Company v. Microsoft Corporation, OpenAI, Inc., et al. *U.S. District Court, Southern District of New York, filed December 2023.*
7. Reddit. Data API pricing and access policy transition. *Reddit company statements, 2023.* `[verify]`
8. Stack Overflow. Crawler and AI data-use policy updates. *Stack Overflow company statements, 2023–2024.* `[verify]`
9. Regulation (EU) 2024/1689 on artificial intelligence (EU AI Act). *EUR-Lex, August 2024.*
10. Howard, Jeremy. `llms.txt` specification. *Answer.AI, 2024.* `[verify]`
11. World Wide Web Consortium. Decentralized Identifiers (DIDs) v1.0. *W3C Recommendation, 2022.* `[verify]`

---

## Appendix A. Example HTTP Traces

A five-step agent buyer journey. Headers abbreviated for readability; real traces include additional standard headers (Date, Server, etc.).

**Step 1. Agent fetches `agents.txt`.**

```
GET /.well-known/agents.txt HTTP/1.1
Host: hillcountryflowers.com
User-Agent: Claude/1.0 (kya:agent/anthropic/claude-prod)

HTTP/1.1 200 OK
Content-Type: text/plain
Cache-Control: max-age=3600

Facet-Version: 0.2
Terminal: https://facet.hillcountryflowers.com/v1
KYA-Issuers: https://issuer.skyfire.xyz, https://kya.hillcountryflowers.com
Pricing-Hint: 0.001 USDC/query, 0.01 USDC/transactional
Rate-Limit: 5000/hour
Reputation-Minimum: 70
Contact: agents@hillcountryflowers.com
```

**Step 2. Agent searches.**

```
POST /v1/search HTTP/1.1
Host: facet.hillcountryflowers.com
Authorization: Bearer eyJhbGciOiJFZERTQSI...
Content-Type: application/json

{"query": "tulip arrangement under $125, sympathy occasion", "filters": {"delivery_zone": "austin-78704", "delivery_by": "2026-05-09T17:00:00Z"}}

HTTP/1.1 200 OK
X-Facet-Signature: ed25519 3oKXp...; key=facet-hillcountry-2026-q2; ts=2026-05-08T15:30:00Z
Content-Type: application/json

{"results": [{"product_id": "SKU-TULIP-MED", "name": "Spring Tulip Bouquet", "quote_token": "qt_abc123..."}]}
```

**Step 3. Agent requests quote.**

```
POST /v1/quote HTTP/1.1
Host: facet.hillcountryflowers.com
Authorization: Bearer eyJhbGciOiJFZERTQSI...
Content-Type: application/json

{"product_id": "SKU-TULIP-MED", "delivery_zone": "austin-78704", "delivery_by": "2026-05-09T17:00:00Z"}

HTTP/1.1 200 OK
X-Facet-Signature: ed25519 7pLx9...; key=facet-hillcountry-2026-q2; ts=2026-05-08T15:30:15Z
Content-Type: application/json

{"price_usd": 95, "available": true, "reservation_token": "rt_xyz789...", "expires_at": "2026-05-08T15:31:15Z"}
```

**Step 4. Agent reserves.**

```
POST /v1/reserve HTTP/1.1
Host: facet.hillcountryflowers.com
Authorization: Bearer eyJhbGciOiJFZERTQSI...
Content-Type: application/json

{"reservation_token": "rt_xyz789..."}

HTTP/1.1 402 Payment Required
X-Payment-Required: usdc:base:0xHillCountryAddress:95
X-Facet-Signature: ed25519 4kNm2...; key=facet-hillcountry-2026-q2; ts=2026-05-08T15:30:30Z
Content-Type: application/json

{"reservation_id": "rsv_2026050815...", "settlement_address": "0xHillCountryAddress", "amount_usdc": 95}
```

**Step 5. Agent settles.**

```
POST /v1/settle HTTP/1.1
Host: facet.hillcountryflowers.com
Authorization: Bearer eyJhbGciOiJFZERTQSI...
X-Payment: <x402-payment-proof>
Content-Type: application/json

{"reservation_id": "rsv_2026050815..."}

HTTP/1.1 200 OK
X-Facet-Signature: ed25519 9qRx5...; key=facet-hillcountry-2026-q2; ts=2026-05-08T15:31:00Z
Content-Type: application/json

{"order_id": "ord_2026050815...", "status": "confirmed", "fulfillment_eta": "2026-05-09"}
```

---

## Appendix B. Glossary

**Agent.** An autonomous software system that executes tasks on behalf of a principal (human user or organization) without continuous human direction.

**Terminal.** Facet's multi-tenant Edge Function, exposed to agents at a per-supplier subdomain (e.g. `facet.<supplier>.com/v1`) CNAMEd to a shared edge. Serves agent requests for every supplier on the platform.

**facet.yaml.** The manifest file emitted by the Schema Auto-Generator. Describes a supplier's catalog, commerce primitives, and policy in a format the Terminal Runtime consumes.

**DID (Decentralized Identifier).** A W3C-standardized self-sovereign identifier that resolves to a document containing public keys and metadata. Used for agent-operator identity in Facet.

**x402.** Coinbase's HTTP 402 Payment Required extension. Enables programmatic USDC payment as a native HTTP exchange.

**MCP (Model Context Protocol).** Anthropic's JSON-RPC-based protocol for LLMs to interact with structured tools and data sources. Facet Terminals are native MCP servers.

**schema.org.** A collaborative vocabulary for structured data on the web. Facet emits schema.org JSON-LD alongside MCP schemas for compatibility with the broader structured-data ecosystem.

**JSON-RPC.** A stateless, lightweight RPC protocol using JSON. The transport for MCP tool calls.

**JWKS (JSON Web Key Set).** Published key set at `/.well-known/facet-keys.json` for verifying Ed25519 response signatures.

**Ed25519.** An elliptic-curve digital signature algorithm (EdDSA over Curve25519). Facet uses Ed25519 for response signatures because of its small key size, fast verification, and deterministic signature generation.

---

## 0. v1.1 update note (2026-04-30)

This whitepaper was originally written when Facet was positioned as an agent-commerce gateway for transactional sites (Catalog primitive only). The 2026-04-30 strategic update extends Facet's coverage to **eight business-archetype primitives** (Catalog, Paywalled Content, Subscription, Booking, Date-Bound Inventory, Auction, Quote/RFQ, Credentialed/Regulated) plus a thin View+Handoff primitive for non-transactional listings, anchored by a **Universal Business Index (UBI)** foundation that indexes every business with any web/maps/social presence (~65–80M globally). New §6.5 introduces the primitive layer; renamed §8 + new §8.5 clarify how the four atomic verbs from the original §8 compose into each primitive. Companion canonical references: `docs/founding/PRIMITIVES.md` (per-primitive deep-dive) and `docs/founding/UBI_MODEL.md` (UBI architecture). The protocol layer (KYAPay + MCP + x402 + RFC 9421) is unchanged; the manifest spec bumps from v1.0 → v1.1 (purely additive. see `specs/agents.txt-v1.1.md`).

## 0.1 v1.2 update note (2026-05-01)

Adds a **knowledge graph layer** over UBI: `kg_nodes` / `kg_edges` / `kg_reports` provide pgvector semantic search and N-hop typed-edge traversal across the directory. New §6.5.11 introduces the layer and its three Terminal endpoints (`POST /v1/graph/match`, `GET /v1/graph/related`, `GET /v1/graph/path`); the existing §6.5.11 coverage table becomes §6.5.12. Schema, ingestion paths, RPC signatures, and phasing live in `UBI_MODEL.md` §6.5; the file-by-file execution plan is at `tasks/facet-graphify-integration-plan-2026-05-01.md`. No verb changes, no primitive additions, no protocol-layer impact. purely a substrate capability under the existing 8-primitive surface.
