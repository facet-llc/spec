"""Client for the hosted Facet Terminal."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import quote

import httpx

from facet_sdk.errors import FacetError, PaymentRequiredError


@dataclass
class SearchOptions:
    q: str
    k: int | None = None
    naics: str | None = None
    geo: str | None = None


class FacetTerminal:
    """Client for the hosted Facet Terminal.

    Wraps the six v0.1 endpoints (capabilities, search, quote, reserve,
    settle, audit) with KYAPay authorization and typed errors.

    Example:
        facet = FacetTerminal(get_kya_token=lambda: os.environ["KYA_TOKEN"])
        result = facet.search_listings(SearchOptions(q="dallas plumbing"))
        listing = result["results"][0]
        quote = facet.request_quote({"listing_id": listing["id"]})
        reservation = facet.reserve({"quote_id": quote["quote_id"]})
        receipt = facet.settle({
            "reservation_id": reservation["reservation_id"],
            "x402_payment": {"tx_hash": "0x...", "chain": "base"},
        })
        audit = facet.get_audit_record(receipt["txn_id"])
    """

    def __init__(
        self,
        get_kya_token: Callable[[], str],
        base_url: str = "https://facet.llc",
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.get_kya_token = get_kya_token
        self.client = client if client is not None else httpx.Client(timeout=10.0)

    def get_capabilities(self) -> dict[str, Any]:
        return self._send("GET", "/v1/capabilities")

    def search_listings(self, opts: SearchOptions) -> dict[str, Any]:
        params: dict[str, str] = {"q": opts.q}
        if opts.k is not None:
            params["k"] = str(opts.k)
        if opts.naics is not None:
            params["naics"] = opts.naics
        if opts.geo is not None:
            params["geo"] = opts.geo
        return self._send("GET", "/v1/search", params=params)

    def request_quote(self, req: dict[str, Any]) -> dict[str, Any]:
        return self._send("POST", "/v1/quote", json=req)

    def reserve(self, req: dict[str, Any]) -> dict[str, Any]:
        return self._send("POST", "/v1/reserve", json=req)

    def settle(self, req: dict[str, Any]) -> dict[str, Any]:
        return self._send("POST", "/v1/settle", json=req)

    def get_audit_record(self, txn_id: str) -> dict[str, Any]:
        if not txn_id or not isinstance(txn_id, str):
            raise ValueError("txn_id must be a non-empty string")
        return self._send("GET", f"/v1/audit/{quote(txn_id, safe='')}")

    def _send(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> dict[str, Any]:
        token = self.get_kya_token()
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        url = f"{self.base_url}{path}"
        res = self.client.request(method, url, headers=headers, params=params, json=json)

        body: Any
        if "application/json" in res.headers.get("content-type", ""):
            try:
                body = res.json()
            except Exception:
                body = None
        else:
            body = res.text

        if res.status_code == 402:
            required = body.get("x402_required") if isinstance(body, dict) else None
            if required:
                raise PaymentRequiredError(required, body)
            raise FacetError("payment required (no x402 instructions in body)", 402, body)

        if res.status_code >= 400:
            message = (
                body.get("error", {}).get("message")
                if isinstance(body, dict)
                else None
            ) or f"{method} {path} failed: {res.status_code}"
            raise FacetError(message, res.status_code, body)

        return body if isinstance(body, dict) else {"data": body}
