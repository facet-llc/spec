"""Run the Ed25519 audit-record vectors against the Python audit verifier."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from facet_sdk import AuditVerifierOptions, verify_audit_record

VECTORS_DIR = Path(__file__).resolve().parents[3] / "test-vectors" / "audit"
VECTORS = sorted(VECTORS_DIR.glob("*.json"))


@pytest.mark.parametrize("path", VECTORS, ids=lambda p: p.stem)
def test_audit_vector(path: Path) -> None:
    v = json.loads(path.read_text())
    inp = v["input"]

    result = verify_audit_record(inp["record"], AuditVerifierOptions(jwks=inp["jwks"]))

    assert result.verified == v["expected"]["verified"], (
        f"{v['name']}: expected verified={v['expected']['verified']}, "
        f"got {result.verified} (errors: {result.errors})"
    )

    if not v["expected"]["verified"]:
        for token in v["expected"]["errors"]:
            assert any(token.lower() in e.lower() for e in result.errors), (
                f"{v['name']}: expected error containing '{token}', got {result.errors}"
            )
