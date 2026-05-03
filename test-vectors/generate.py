"""Generate KYAPay JWT conformance test vectors.

Produces five vectors covering the verifier's mandatory checks per SPEC.md
section 3. Run this whenever the test keys rotate or the vector format
changes.

Requirements: pyjwt, cryptography.
"""
import base64
import json
import os
import time

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

# Generate test ES256 keypair (deterministic for this run; not for prod)
private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
public_key = private_key.public_key()

# Export as JWK
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


def sign(claims, alg="ES256", headers=None):
    h = {"kid": KID, "alg": alg, "typ": "kya+jwt"}
    if headers:
        h.update(headers)
    if alg == "ES256":
        return pyjwt.encode(claims, private_pem, algorithm=alg, headers=h)
    elif alg == "HS256":
        return pyjwt.encode(claims, "shared-secret-not-allowed-in-v0.1", algorithm=alg, headers=h)
    raise ValueError(alg)


def write_vector(filename, vector):
    path = os.path.join(OUT, filename)
    with open(path, "w") as f:
        json.dump(vector, f, indent=2)
    print(f"  wrote {path}")


def common_options():
    return {
        "audience": AUDIENCE,
        "expected_issuers": [ISSUER],
    }


# 1. Valid happy path
v1_jwt = sign(base_claims)
write_vector("01-valid-kya-jwt.json", {
    "name": "valid-kya-jwt",
    "description": "ES256-signed kya+jwt with all claims valid at now=" + str(NOW),
    "spec_section": "SPEC.md section 3",
    "input": {
        "jwt": v1_jwt,
        "jwks": jwks,
        "verify_options": common_options(),
        "now": NOW,
    },
    "expected": {
        "verified": True,
        "claims": {k: v for k, v in base_claims.items() if k in ("iss", "aud", "sub", "agent_id", "scope")},
        "errors": [],
    },
})

# 2. Expired (exp before now)
expired_claims = dict(base_claims, iat=NOW - 7200, exp=NOW - 60)
v2_jwt = sign(expired_claims)
write_vector("02-expired.json", {
    "name": "expired",
    "description": "exp claim is in the past relative to now. Verifier MUST reject.",
    "spec_section": "SPEC.md section 3",
    "input": {
        "jwt": v2_jwt,
        "jwks": jwks,
        "verify_options": common_options(),
        "now": NOW,
    },
    "expected": {
        "verified": False,
        "errors": ["expired"],
    },
})

# 3. Wrong audience
wrong_aud_claims = dict(base_claims, aud="https://other-merchant.example.com")
v3_jwt = sign(wrong_aud_claims)
write_vector("03-wrong-audience.json", {
    "name": "wrong-audience",
    "description": "aud claim does not match verify_options.audience. Reject.",
    "spec_section": "SPEC.md section 3",
    "input": {
        "jwt": v3_jwt,
        "jwks": jwks,
        "verify_options": common_options(),
        "now": NOW,
    },
    "expected": {
        "verified": False,
        "errors": ["audience mismatch"],
    },
})

# 4. Wrong algorithm (HS256 instead of ES256)
v4_jwt = sign(base_claims, alg="HS256")
write_vector("04-wrong-algorithm.json", {
    "name": "wrong-algorithm",
    "description": "Token signed with HS256. v0.1 verifiers MUST accept only ES256.",
    "spec_section": "SPEC.md section 3",
    "input": {
        "jwt": v4_jwt,
        "jwks": jwks,
        "verify_options": common_options(),
        "now": NOW,
    },
    "expected": {
        "verified": False,
        "errors": ["unsupported algorithm"],
    },
})

# 5. Tampered signature (flip last char of sig)
v5_jwt_valid = sign(base_claims)
header, payload, sig = v5_jwt_valid.split(".")
flipped = sig[:-1] + ("a" if sig[-1] != "a" else "b")
v5_jwt = f"{header}.{payload}.{flipped}"
write_vector("05-tampered-signature.json", {
    "name": "tampered-signature",
    "description": "Last byte of signature flipped. Cryptographic verification MUST fail.",
    "spec_section": "SPEC.md section 3",
    "input": {
        "jwt": v5_jwt,
        "jwks": jwks,
        "verify_options": common_options(),
        "now": NOW,
    },
    "expected": {
        "verified": False,
        "errors": ["signature verification failed"],
    },
})

print(f"done. wrote 5 vectors to {OUT}")
