"""Generate KYAPay JWT conformance test vectors.

Produces vectors covering the verifier's mandatory checks per SPEC.md
section 3 plus the additional defenses in @facet/sdk-js v0.0.2:
trust gate, kid enforcement, https issuer enforcement, custom-claim
type validation, clock tolerance.

Run this whenever the test keys rotate or the vector format changes.

Requirements: pyjwt, cryptography.
"""
import base64
import json
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import jwt as pyjwt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "kyapay")
os.makedirs(OUT, exist_ok=True)

# Deterministic test issuer + audience
ISSUER = "https://issuer.example.com"
AUDIENCE = "https://merchant.example.com"
KID = "facet-test-2026-05"
NOW = 1730000000  # 2024-10-27 fixed

# Generate a fresh ES256 keypair (private key never persists to disk).
private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
public_key = private_key.public_key()

public_numbers = public_key.public_numbers()
def b64u_int(n: int, length: int) -> str:
    return base64.urlsafe_b64encode(n.to_bytes(length, "big")).rstrip(b"=").decode()

jwk = {
    "kty": "EC",
    "crv": "P-256",
    "x": b64u_int(public_numbers.x, 32),
    "y": b64u_int(public_numbers.y, 32),
    "kid": KID,
    "alg": "ES256",
    "use": "sig",
}
jwks = {"keys": [jwk]}

private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

base_claims = {
    "iss": ISSUER,
    "aud": AUDIENCE,
    "sub": "did:facet:agent-1",
    "iat": NOW - 60,
    "nbf": NOW - 60,
    "exp": NOW + 3600,
    "agent_id": "did:facet:agent-1",
    "scope": "search quote settle",
}


def sign(claims, alg="ES256", headers=None, omit_kid=False):
    h = {"alg": alg, "typ": "kya+jwt"}
    if not omit_kid:
        h["kid"] = KID
    if headers:
        h.update(headers)
    if alg == "ES256":
        return pyjwt.encode(claims, private_pem, algorithm=alg, headers=h)
    if alg == "HS256":
        return pyjwt.encode(claims, "shared-secret-not-allowed-in-v0.1", algorithm=alg, headers=h)
    raise ValueError(alg)


def write_vector(filename, vector):
    path = os.path.join(OUT, filename)
    with open(path, "w") as f:
        json.dump(vector, f, indent=2)
    print(f"  wrote {path}")


def opts(**overrides):
    base = {"audience": AUDIENCE, "expected_issuers": [ISSUER]}
    base.update(overrides)
    return base


# 1. Valid happy path
write_vector("01-valid-kya-jwt.json", {
    "name": "valid-kya-jwt",
    "description": "ES256-signed kya+jwt with all claims valid at now=" + str(NOW),
    "spec_section": "SPEC.md section 3",
    "input": {
        "jwt": sign(base_claims),
        "jwks": jwks,
        "verify_options": opts(),
        "now": NOW,
    },
    "expected": {
        "verified": True,
        "claims": {k: v for k, v in base_claims.items() if k in ("iss", "aud", "sub", "agent_id", "scope")},
        "errors": [],
    },
})

# 2. Expired
expired_claims = dict(base_claims, iat=NOW - 7200, exp=NOW - 60)
write_vector("02-expired.json", {
    "name": "expired",
    "description": "exp claim is in the past relative to now. Verifier MUST reject.",
    "spec_section": "SPEC.md section 3",
    "input": {
        "jwt": sign(expired_claims),
        "jwks": jwks,
        "verify_options": opts(),
        "now": NOW,
    },
    "expected": {"verified": False, "errors": ["expired"]},
})

# 3. Wrong audience
write_vector("03-wrong-audience.json", {
    "name": "wrong-audience",
    "description": "aud claim does not match verify_options.audience. Reject.",
    "spec_section": "SPEC.md section 3",
    "input": {
        "jwt": sign(dict(base_claims, aud="https://other-merchant.example.com")),
        "jwks": jwks,
        "verify_options": opts(),
        "now": NOW,
    },
    "expected": {"verified": False, "errors": ["audience mismatch"]},
})

# 4. Wrong algorithm
write_vector("04-wrong-algorithm.json", {
    "name": "wrong-algorithm",
    "description": "Token signed with HS256. v0.1 verifiers MUST accept only ES256.",
    "spec_section": "SPEC.md section 3",
    "input": {
        "jwt": sign(base_claims, alg="HS256"),
        "jwks": jwks,
        "verify_options": opts(),
        "now": NOW,
    },
    "expected": {"verified": False, "errors": ["unsupported algorithm"]},
})

# 5. Tampered signature: byte-flip after b64 decode (proper byte-level tamper)
v5_jwt_valid = sign(base_claims)
v5_header, v5_payload, v5_sig_b64 = v5_jwt_valid.split(".")
v5_sig_bytes = bytearray(base64.urlsafe_b64decode(v5_sig_b64 + "=" * (-len(v5_sig_b64) % 4)))
v5_sig_bytes[0] ^= 0xFF
v5_tampered_b64 = base64.urlsafe_b64encode(bytes(v5_sig_bytes)).rstrip(b"=").decode()
write_vector("05-tampered-signature.json", {
    "name": "tampered-signature",
    "description": "First byte of decoded signature flipped. Cryptographic verification MUST fail.",
    "spec_section": "SPEC.md section 3",
    "input": {
        "jwt": f"{v5_header}.{v5_payload}.{v5_tampered_b64}",
        "jwks": jwks,
        "verify_options": opts(),
        "now": NOW,
    },
    "expected": {"verified": False, "errors": ["signature verification failed"]},
})

# 6. No expectedIssuers, no jwks: trust gate must refuse
write_vector("06-no-expected-issuers.json", {
    "name": "no-expected-issuers",
    "description": "Caller passed neither expectedIssuers nor jwks. Verifier MUST refuse.",
    "spec_section": "SPEC.md section 3 (trust gate)",
    "input": {
        "jwt": sign(base_claims),
        "verify_options": {"audience": AUDIENCE},
        "now": NOW,
    },
    "expected": {"verified": False, "errors": ["allowlist"]},
})

# 7. Missing kid: verifier MUST reject (no first-key fallback)
write_vector("07-missing-kid.json", {
    "name": "missing-kid",
    "description": "JWT header lacks kid. Verifier MUST refuse rather than fall back to the first JWKS key.",
    "spec_section": "SPEC.md section 3",
    "input": {
        "jwt": sign(base_claims, omit_kid=True),
        "jwks": jwks,
        "verify_options": opts(),
        "now": NOW,
    },
    "expected": {"verified": False, "errors": ["kid"]},
})

# 8. HTTP issuer (no jwks, requires remote fetch over insecure scheme)
write_vector("08-http-issuer.json", {
    "name": "http-issuer",
    "description": "iss is http:// (not https). Verifier MUST refuse remote JWKS fetch over cleartext.",
    "spec_section": "SPEC.md section 3",
    "input": {
        "jwt": sign(dict(base_claims, iss="http://issuer.example.com")),
        "verify_options": opts(expected_issuers=["http://issuer.example.com"]),
        "now": NOW,
    },
    "expected": {"verified": False, "errors": ["https"]},
})

# 9. Malformed custom claim: agent_id is a number, not a string
write_vector("09-bad-custom-claim.json", {
    "name": "bad-custom-claim",
    "description": "agent_id is a number instead of a string. Verifier MUST reject.",
    "spec_section": "SPEC.md section 3 (custom claim validation)",
    "input": {
        "jwt": sign(dict(base_claims, agent_id=42)),
        "jwks": jwks,
        "verify_options": opts(),
        "now": NOW,
    },
    "expected": {"verified": False, "errors": ["agent_id"]},
})

# 10. nbf in the future, but within clock tolerance
write_vector("10-nbf-within-tolerance.json", {
    "name": "nbf-within-tolerance",
    "description": "nbf is 10s after now; default 30s clockTolerance allows it.",
    "spec_section": "SPEC.md section 3",
    "input": {
        "jwt": sign(dict(base_claims, iat=NOW + 10, nbf=NOW + 10)),
        "jwks": jwks,
        "verify_options": opts(),
        "now": NOW,
    },
    "expected": {"verified": True, "errors": []},
})

print(f"done. wrote 10 vectors to {OUT}")
