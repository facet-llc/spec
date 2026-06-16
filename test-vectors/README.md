# Test vectors

Conformance test vectors for KYAPay JWT verifiers.

## Format

Each `.json` file is a self-contained test vector:

```json
{
  "name": "...",
  "description": "...",
  "spec_section": "SPEC.md section 3",
  "input": {
    "jwt": "<eyJ...>",
    "jwks": { "keys": [ ... ] },
    "verify_options": {
      "audience": "...",
      "expected_issuers": [ "..." ]
    },
    "now": 1730000000
  },
  "expected": {
    "verified": true,
    "errors": []
  }
}
```

`now` is the Unix epoch timestamp the verifier should treat as "current time" when checking `iat`, `nbf`, and `exp`. Vectors are deterministic.

## Coverage

| File | Scenario |
|---|---|
| `kyapay/01-valid-kya-jwt.json` | Happy path. ES256, valid issuer, valid audience, within iat/exp window. |
| `kyapay/02-expired.json` | `exp` is before `now`. Verifier MUST reject. |
| `kyapay/03-wrong-audience.json` | `aud` does not match `verify_options.audience`. Reject. |
| `kyapay/04-wrong-algorithm.json` | Token signed with HS256. Verifier MUST reject; only ES256 is valid in v0.1. |
| `kyapay/05-tampered-signature.json` | Signature byte flipped. Verifier MUST reject. |

## Generate

The vectors in this directory were produced by `generate.py`. To regenerate (e.g., to rotate test keys):

```bash
cd test-vectors
python generate.py
```

Requires `pyjwt` and `cryptography`.

## Run against a verifier

Load each vector, run its `input` through a KYAPay verifier under the frozen
`input.now` clock, and assert the verdict equals `expected.verified`. Each
vector carries `input.jwt`, `input.verify_options`, and `input.now`, with
`expected.verified` (and, on failure, `expected.reason`).

A runnable verifier and a worked conformance harness live in the SDK repo,
[`github.com/facet-llc/sdk`](https://github.com/facet-llc/sdk).

## Stability

These vectors are part of the v0.1 conformance suite. Adding new vectors is non-breaking; modifying existing vectors is breaking and bumps the major version.
