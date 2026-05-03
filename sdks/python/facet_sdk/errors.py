"""Typed errors raised by the Facet Terminal client."""

from typing import Any


class FacetError(Exception):
    """Raised on any non-2xx response from the Facet Terminal."""

    def __init__(self, message: str, status: int, body: Any) -> None:
        super().__init__(message)
        self.status = status
        self.body = body


class PaymentRequiredError(FacetError):
    """Raised when /v1/reserve hits an x402 payment-required wall.

    The `required` attribute carries the x402 payment instructions the
    caller needs to satisfy before retrying.
    """

    def __init__(self, required: dict[str, Any], body: Any) -> None:
        super().__init__("payment required: x402", 402, body)
        self.required = required
