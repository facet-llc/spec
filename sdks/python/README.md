# facet-sdk (Python)

Reference Python SDK for the [Facet Protocol](https://github.com/facet-llc/protocol). Verifier, Terminal client, and Ed25519 audit-record verifier in one package.

```bash
pip install facet-sdk
```

## Verify a KYAPay JWT

```python
from facet_sdk import VerifierOptions, verify_kya_token

result = verify_kya_token(
    jwt,
    VerifierOptions(
        audience="https://my-merchant.example.com",
        expected_issuers=["https://issuer.example.com"],
    ),
)

if result.verified:
    print("agent claims:", result.claims)
else:
    print("verification failed:", result.errors)
```

The verifier fetches the issuer's JWKS from `<iss>/.well-known/jwks.json` and caches per process. To skip the fetch (tests, air-gapped, pinned keys), pass `jwks=`:

```python
result = verify_kya_token(
    jwt,
    VerifierOptions(audience="...", jwks={"keys": [...]}),
)
```

## Drive the Terminal

```python
import os
from facet_sdk import FacetTerminal, SearchOptions, PaymentRequiredError

facet = FacetTerminal(get_kya_token=lambda: os.environ["KYA_TOKEN"])

search = facet.search_listings(SearchOptions(q="dallas plumbing", k=3))
listing = search["results"][0]
quote = facet.request_quote({"listing_id": listing["id"]})
reservation = facet.reserve({"quote_id": quote["quote_id"]})

try:
    receipt = facet.settle({
        "reservation_id": reservation["reservation_id"],
        "x402_payment": {"tx_hash": "0x...", "chain": "base"},
    })
    audit = facet.get_audit_record(receipt["txn_id"])
    print("audit:", audit)
except PaymentRequiredError as err:
    print(f"pay {err.required['amount']} {err.required['currency']} to {err.required['to']}")
```

## Verify an audit record

```python
from facet_sdk import AuditVerifierOptions, verify_audit_record

result = verify_audit_record(
    record,
    AuditVerifierOptions(jwks={"keys": [merchant_signing_jwk]}),
)
```

## Run the conformance suite

The SDK ships with both KYAPay and Ed25519 audit vectors:

```bash
pip install -e ".[test]"
pytest
```

Vectors live in `../../test-vectors/` at the repo root. Same vectors the TypeScript SDK runs.

## Status

`v0.0.1` ships:

- `verify_kya_token()` with mandatory ES256 + JWKS resolution + claim checks
- `FacetTerminal` client for all six v0.1 endpoints
- `verify_audit_record()` Ed25519 verifier per `AUDIT.md`
- Conformance against the KYAPay (10) and audit (4) vector suites

`v0.1.0` will add:

- Async client variants (`AsyncFacetTerminal` on `httpx.AsyncClient`)
- Multi-rail payment support (Visa VIC, Mastercard SCOF) per KYAPay `stp` claim
- Generated TypedDicts from the JSON schemas

## License

Apache 2.0. See the [protocol repo](https://github.com/facet-llc/protocol/blob/main/LICENSE).
