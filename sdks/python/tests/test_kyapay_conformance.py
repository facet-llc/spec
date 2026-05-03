"""Run the KYAPay JWT conformance vectors against the Python verifier."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from facet_sdk import VerifierOptions, verify_kya_token

VECTORS_DIR = Path(__file__).resolve().parents[3] / "test-vectors" / "kyapay"
VECTORS = sorted(VECTORS_DIR.glob("*.json"))


@pytest.mark.parametrize("path", VECTORS, ids=lambda p: p.stem)
def test_kyapay_vector(path: Path) -> None:
    v = json.loads(path.read_text())
    inp = v["input"]

    opts = VerifierOptions(
        audience=inp["verify_options"]["audience"],
        expected_issuers=inp["verify_options"].get("expected_issuers"),
        jwks=inp.get("jwks"),
        current_time=inp["now"],
    )

    result = verify_kya_token(inp["jwt"], opts)

    assert result.verified == v["expected"]["verified"], (
        f"{v['name']}: expected verified={v['expected']['verified']}, "
        f"got {result.verified} (errors: {result.errors})"
    )

    if not v["expected"]["verified"]:
        for token in v["expected"]["errors"]:
            assert any(token.lower() in e.lower() for e in result.errors), (
                f"{v['name']}: expected error containing '{token}', got {result.errors}"
            )

    if v["expected"]["verified"] and "claims" in v["expected"]:
        assert result.claims is not None
        for k, expected_v in v["expected"]["claims"].items():
            assert result.claims.get(k) == expected_v, (
                f"{v['name']}: claim {k}={result.claims.get(k)}, expected {expected_v}"
            )
