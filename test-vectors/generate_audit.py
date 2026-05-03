"""Generate Ed25519 audit-record conformance vectors per AUDIT.md.

Vectors cover: happy path, tampered field, wrong key, missing required field.

Requirements: cryptography. Run from repo root or test-vectors/.
"""
import base64
import json
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "audit")
os.makedirs(OUT, exist_ok=True)

KID_A = "merchant-2026-05-A"
KID_B = "merchant-2026-05-B"


def gen_keypair(kid):
    priv = Ed25519PrivateKey.generate()
    pub_raw = priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    jwk = {
        "kty": "OKP",
        "crv": "Ed25519",
        "x": base64.urlsafe_b64encode(pub_raw).rstrip(b"=").decode(),
        "kid": kid,
        "alg": "EdDSA",
        "use": "sig",
    }
    return priv, jwk


def canonicalize(record):
    """Per AUDIT.md: drop sig+kid, sort keys, no whitespace."""
    filtered = {k: v for k, v in record.items() if k not in ("sig", "kid")}
    return json.dumps(filtered, sort_keys=True, separators=(",", ":"))


def sign(record, priv, kid):
    canonical = canonicalize(record).encode("utf-8")
    sig = priv.sign(canonical)
    record["kid"] = kid
    record["sig"] = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
    return record


def write_vector(filename, vector):
    path = os.path.join(OUT, filename)
    with open(path, "w") as f:
        json.dump(vector, f, indent=2)
    print(f"  wrote {path}")


priv_a, jwk_a = gen_keypair(KID_A)
priv_b, jwk_b = gen_keypair(KID_B)
jwks_just_a = {"keys": [jwk_a]}
jwks_a_and_b = {"keys": [jwk_a, jwk_b]}

base_record = {
    "txn_id": "txn_abc123",
    "iat": 1730000000,
    "merchant": "did:facet:merchant-1",
    "agent": "did:facet:agent-1",
    "amount": "250.00",
    "currency": "USDC",
    "tx_hash": "0x" + "ab" * 32,
}

# 1. Valid happy path
record1 = sign(dict(base_record), priv_a, KID_A)
write_vector("01-valid-audit.json", {
    "name": "valid-audit",
    "description": "Ed25519-signed audit record with all required fields. Verifier returns verified=true.",
    "spec_section": "AUDIT.md",
    "input": {"record": record1, "jwks": jwks_just_a},
    "expected": {"verified": True, "errors": []},
})

# 2. Tampered amount: sign valid, then mutate amount
record2 = sign(dict(base_record), priv_a, KID_A)
record2["amount"] = "1.00"  # tamper after signing
write_vector("02-tampered-amount.json", {
    "name": "tampered-amount",
    "description": "amount field changed after signing. Verifier MUST reject.",
    "spec_section": "AUDIT.md",
    "input": {"record": record2, "jwks": jwks_just_a},
    "expected": {"verified": False, "errors": ["signature verification failed"]},
})

# 3. Wrong key: sign with key A, only key B is in JWKS
record3 = sign(dict(base_record), priv_a, KID_A)
write_vector("03-wrong-key.json", {
    "name": "wrong-key",
    "description": "Record signed with key A; JWKS contains only key B. Verifier MUST reject (no matching kid).",
    "spec_section": "AUDIT.md",
    "input": {"record": record3, "jwks": {"keys": [jwk_b]}},
    "expected": {"verified": False, "errors": ["no key in JWKS matching kid"]},
})

# 4. Missing required field
record4 = sign(dict(base_record), priv_a, KID_A)
del record4["agent"]
write_vector("04-missing-required-field.json", {
    "name": "missing-required-field",
    "description": "agent field stripped. Verifier MUST reject before checking signature.",
    "spec_section": "AUDIT.md",
    "input": {"record": record4, "jwks": jwks_just_a},
    "expected": {"verified": False, "errors": ["missing required field: agent"]},
})

print(f"done. wrote 4 vectors to {OUT}")
