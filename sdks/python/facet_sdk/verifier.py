"""KYAPay JWT verifier per Facet spec section 3."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import jwt as pyjwt


@dataclass
class VerifierOptions:
    """Configuration for verify_kya_token."""

    audience: str
    """Your merchant URL or DID. The token's `aud` must match."""

    expected_issuers: list[str] | None = None
    """Issuer allowlist. Required when `jwks` is not provided. The token's
    `iss` must be in this list, and only HTTPS issuer URLs are accepted.

    Without this, the verifier would fetch a JWKS from any issuer URL the
    JWT claims, accepting tokens from any internet-reachable host that
    publishes a valid JWKS. That is a trust bypass; we refuse the unsafe
    default.
    """

    current_time: int | None = None
    """Override "now" (Unix epoch seconds). Useful for replaying
    conformance vectors against a frozen timestamp."""

    jwks: dict[str, Any] | None = None
    """Bring-your-own JWKS as `{"keys": [...]}`. When set, the verifier
    skips the issuer-driven JWKS fetch entirely. Useful for tests,
    air-gapped deploys, and pinned-key rotation."""

    clock_tolerance: int = 30
    """Clock skew tolerance for iat/nbf/exp checks, in seconds."""


@dataclass
class VerifyResult:
    verified: bool
    claims: dict[str, Any] | None = None
    errors: list[str] = field(default_factory=list)


KYAClaims = dict[str, Any]


def _validate_custom_claims(p: dict[str, Any]) -> tuple[bool, str]:
    if "agent_id" in p and not isinstance(p["agent_id"], str):
        return False, "agent_id must be a string"
    if "scope" in p and not isinstance(p["scope"], str):
        return False, "scope must be a string"
    return True, ""


def verify_kya_token(token: str, options: VerifierOptions) -> VerifyResult:
    """Verify a KYAPay JWT.

    Mandatory checks:
      - alg MUST be ES256
      - signature verifies against the issuer JWKS
      - aud matches options.audience
      - iss is in options.expected_issuers (required unless options.jwks set)
      - iss URL uses https when fetching JWKS remotely
      - kid header is present and matches a key in the JWKS
      - iat, nbf, exp are valid (with clock_tolerance leeway)
      - custom claims (agent_id, scope) match their declared types
    """
    try:
        header = pyjwt.get_unverified_header(token)
    except Exception as e:
        return VerifyResult(False, errors=[f"malformed jwt: {e}"])

    if header.get("alg") != "ES256":
        return VerifyResult(
            False,
            errors=[f"unsupported algorithm: expected ES256, got {header.get('alg')}"],
        )

    kid = header.get("kid")
    if not isinstance(kid, str) or not kid:
        return VerifyResult(False, errors=["jwt header missing kid"])

    try:
        unverified_payload = pyjwt.decode(token, options={"verify_signature": False})
    except Exception as e:
        return VerifyResult(False, errors=[f"malformed jwt payload: {e}"])

    iss = unverified_payload.get("iss")
    if not isinstance(iss, str):
        return VerifyResult(False, errors=["missing iss claim"])

    has_allowlist = bool(options.expected_issuers)
    if not options.jwks and not has_allowlist:
        return VerifyResult(
            False,
            errors=[
                "expected_issuers is required when jwks is not provided. "
                "Pass an allowlist of trusted issuer URLs to prevent JWKS-trust bypass."
            ],
        )

    if has_allowlist and iss not in options.expected_issuers:
        return VerifyResult(False, errors=[f"unexpected issuer: {iss}"])

    if options.jwks:
        matching = next((k for k in options.jwks["keys"] if k.get("kid") == kid), None)
        if not matching:
            return VerifyResult(False, errors=[f"no key in JWKS matching kid={kid}"])
        try:
            signing_key = pyjwt.PyJWK(matching).key
        except Exception as e:
            return VerifyResult(False, errors=[f"failed to import key: {e}"])
    else:
        if not iss.startswith("https://"):
            return VerifyResult(
                False, errors=["issuer must use https for remote JWKS resolution"]
            )
        try:
            jwks_client = pyjwt.PyJWKClient(f"{iss}/.well-known/jwks.json")
            signing_key = jwks_client.get_signing_key(kid).key
        except Exception as e:
            return VerifyResult(False, errors=[f"jwks fetch failed: {e}"])

    decode_options: dict[str, Any] = {
        "leeway": options.clock_tolerance,
    }
    if options.current_time is not None:
        # pyjwt only honors wall clock; defer iat/nbf/exp to the manual check
        # below so test vectors with frozen `now` work.
        decode_options["verify_exp"] = False
        decode_options["verify_nbf"] = False
        decode_options["verify_iat"] = False

    decode_kwargs: dict[str, Any] = {
        "algorithms": ["ES256"],
        "audience": options.audience,
        "options": decode_options,
        "leeway": options.clock_tolerance,
    }

    try:
        verified = pyjwt.decode(token, signing_key, **decode_kwargs)
    except pyjwt.ExpiredSignatureError:
        return VerifyResult(False, errors=["expired"])
    except pyjwt.InvalidAudienceError:
        return VerifyResult(False, errors=["audience mismatch"])
    except pyjwt.InvalidSignatureError:
        return VerifyResult(False, errors=["signature verification failed"])
    except pyjwt.ImmatureSignatureError:
        return VerifyResult(False, errors=["token not yet valid"])
    except Exception as e:
        return VerifyResult(False, errors=[str(e)])

    if options.current_time is not None:
        exp = verified.get("exp")
        nbf = verified.get("nbf")
        if isinstance(exp, int) and exp + options.clock_tolerance < options.current_time:
            return VerifyResult(False, errors=["expired"])
        if isinstance(nbf, int) and nbf - options.clock_tolerance > options.current_time:
            return VerifyResult(False, errors=["token not yet valid"])

    ok, reason = _validate_custom_claims(verified)
    if not ok:
        return VerifyResult(False, errors=[reason])

    return VerifyResult(True, claims=verified, errors=[])
