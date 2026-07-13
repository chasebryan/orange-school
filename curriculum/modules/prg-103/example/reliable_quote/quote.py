"""Calculate a bounded quote without silently repairing invalid input."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


MIN_QUANTITY: Final = 1
MAX_QUANTITY: Final = 100
MIN_UNIT_PRICE_CENTS: Final = 0
MAX_UNIT_PRICE_CENTS: Final = 1_000_000
MAX_CONTEXT_CHARS: Final = 80


@dataclass(frozen=True)
class InputError:
    """Structured context for one rejected input field."""

    code: str
    field: str
    received: str
    message: str

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str)
            for value in (self.code, self.field, self.received, self.message)
        ):
            raise TypeError("error fields must be text")
        if not self.code or not self.field or not self.message:
            raise ValueError("error code, field, and message must be non-empty")
        if len(self.received) > MAX_CONTEXT_CHARS:
            raise ValueError("received-value context exceeds its bound")


@dataclass(frozen=True)
class QuoteSuccess:
    """A quote whose fields satisfy the module's documented invariants."""

    quantity: int
    unit_price_cents: int
    total_cents: int

    def __post_init__(self) -> None:
        if any(
            type(value) is not int
            for value in (self.quantity, self.unit_price_cents, self.total_cents)
        ):
            raise TypeError("quote fields must be integers")
        if not MIN_QUANTITY <= self.quantity <= MAX_QUANTITY:
            raise ValueError("quantity is outside the accepted range")
        if not MIN_UNIT_PRICE_CENTS <= self.unit_price_cents <= MAX_UNIT_PRICE_CENTS:
            raise ValueError("unit price is outside the accepted range")
        if self.total_cents != self.quantity * self.unit_price_cents:
            raise ValueError("total must equal quantity times unit price")


@dataclass(frozen=True)
class QuoteFailure:
    """A rejected quote request; this variant contains no computed total."""

    error: InputError

    def __post_init__(self) -> None:
        if not isinstance(self.error, InputError):
            raise TypeError("failure must contain one InputError")


QuoteResult = QuoteSuccess | QuoteFailure


def _bounded_context(value: object) -> str:
    """Return safe, bounded diagnostic context for a rejected value."""

    rendered = f"{type(value).__name__}:{value!r}"
    if len(rendered) <= MAX_CONTEXT_CHARS:
        return rendered
    return f"{rendered[: MAX_CONTEXT_CHARS - 3]}..."


def _failure(code: str, field: str, received: object, message: str) -> QuoteFailure:
    return QuoteFailure(
        InputError(
            code=code,
            field=field,
            received=_bounded_context(received),
            message=message,
        )
    )


def _parse_ascii_decimal(
    field: str,
    text: object,
    minimum: int,
    maximum: int,
) -> int | QuoteFailure:
    if not isinstance(text, str):
        return _failure("not_text", field, text, "expected text containing ASCII digits")
    if not text.isascii() or not text.isdecimal():
        return _failure(
            "not_ascii_decimal",
            field,
            text,
            "expected one or more ASCII decimal digits with no sign or whitespace",
        )

    value = int(text)
    if not minimum <= value <= maximum:
        return _failure(
            "out_of_range",
            field,
            text,
            f"expected a value from {minimum} through {maximum}",
        )
    return value


def calculate_quote(quantity_text: str, unit_price_cents_text: str) -> QuoteResult:
    """Validate two text fields and return exactly one explicit result variant.

    Accepted quantity input is ASCII decimal text representing 1 through 100.
    Accepted unit-price input is ASCII decimal text representing 0 through
    1,000,000 cents. Leading zeroes are accepted. Whitespace, signs, separators,
    non-ASCII digits, and values outside the ranges are rejected.
    """

    quantity = _parse_ascii_decimal(
        "quantity",
        quantity_text,
        MIN_QUANTITY,
        MAX_QUANTITY,
    )
    if isinstance(quantity, QuoteFailure):
        return quantity

    unit_price_cents = _parse_ascii_decimal(
        "unit_price_cents",
        unit_price_cents_text,
        MIN_UNIT_PRICE_CENTS,
        MAX_UNIT_PRICE_CENTS,
    )
    if isinstance(unit_price_cents, QuoteFailure):
        return unit_price_cents

    return QuoteSuccess(
        quantity=quantity,
        unit_price_cents=unit_price_cents,
        total_cents=quantity * unit_price_cents,
    )
