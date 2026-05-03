"""Ed25519 audit-record verifier per AUDIT.md."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

REQUIRED_FIELDS = ("txn_id", "iat", "merchant", "agent", "sig", "kid")


@dataclass
class AuditVerifierOptions:
    jwks: dict[str, Any]


@dataclass
class AuditVerifyResult:
    verified: bool
    errors: list[str] = field(default_factory=list)


def _b64u_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _canonicalize(record: dict[str, Any]) -> str:
    """Per AUDIT.md: drop sig+kid, sort top-level keys, no whitespace."""
    filtered = {k: v for k, v in record.items() if k not in ("sig", "kid")}
    return json.dumps(filtered, sort_keys=True, separators=(",", ":"))


def verify_audit_record(
    record: dict[str, Any], options: AuditVerifierOptions
) -> AuditVerifyResult:
    """Verify an Ed25519-signed audit record per AUDIT.md.

    Mandatory checks:
      - all required fields present
      - kid in record matches a JWK in options.jwks
      - JWK is kty=OKP, crv=Ed25519, alg=EdDSA
      - signature verifies over canonical(record without sig+kid)
    """
    for field_name in REQUIRED_FIELDS:
        if field_name not in record:
            return AuditVerifyResult(False, errors=[f"missing required field: {field_name}"])

    matching = next((k for k in options.jwks["keys"] if k.get("kid") == record["kid"]), None)
    if not matching:
        return AuditVerifyResult(
            False, errors=[f"no key in JWKS matching kid={record['kid']}"]
        )

    if matching.get("kty") != "OKP" or matching.get("crv") != "Ed25519":
        return AuditVerifyResult(
            False,
            errors=[
                f"audit signing key must be Ed25519 OKP; got "
                f"kty={matching.get('kty')}, crv={matching.get('crv')}"
            ],
        )

    try:
        pub_key_bytes = _b64u_decode(matching["x"])
        public_key = Ed25519PublicKey.from_public_bytes(pub_key_bytes)
    except Exception as e:
        return AuditVerifyResult(False, errors=[f"failed to import key: {e}"])

    try:
        sig_bytes = _b64u_decode(record["sig"])
    except Exception:
        return AuditVerifyResult(False, errors=["malformed sig (not base64url)"])

    if len(sig_bytes) != 64:
        return AuditVerifyResult(
            False, errors=[f"sig length must be 64 bytes, got {len(sig_bytes)}"]
        )

    canonical = _canonicalize(record).encode("utf-8")
    try:
        public_key.verify(sig_bytes, canonical)
    except InvalidSignature:
        return AuditVerifyResult(False, errors=["signature verification failed"])

    return AuditVerifyResult(True, errors=[])
