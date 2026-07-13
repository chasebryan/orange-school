#!/usr/bin/env python3
"""Build bounded inventory representations from NAME=QUANTITY records."""

import sys

MAX_ENTRIES = 50
MAX_NAME_LENGTH = 16
MAX_QUANTITY = 1_000


def valid_name(name):
    """Names are short lowercase ASCII words with optional hyphens."""
    if not 1 <= len(name) <= MAX_NAME_LENGTH:
        return False
    if not name.isascii() or name.startswith("-") or name.endswith("-"):
        return False
    return all(character.islower() or character == "-" for character in name)


def parse_entry(text):
    """Return one fixed two-field record as a tuple."""
    if text.count("=") != 1:
        raise ValueError(f"entry must have NAME=QUANTITY form: {text!r}")
    name, quantity_text = text.split("=", 1)
    if not valid_name(name):
        raise ValueError(f"invalid item name: {name!r}")
    try:
        quantity = int(quantity_text)
    except ValueError as error:
        raise ValueError(f"quantity must be an integer: {quantity_text!r}") from error
    if not 0 <= quantity <= MAX_QUANTITY:
        raise ValueError(f"quantity must be from 0 through {MAX_QUANTITY}")
    return name, quantity


def build_inventory(entry_texts):
    """Return a name-to-quantity dictionary after validating all entries."""
    if not 1 <= len(entry_texts) <= MAX_ENTRIES:
        raise ValueError(f"supply from 1 through {MAX_ENTRIES} entries")

    inventory = {}
    for text in entry_texts:
        name, quantity = parse_entry(text)
        if name in inventory:
            raise ValueError(f"duplicate item name: {name!r}")
        inventory[name] = quantity
    return inventory


def make_report(entry_texts):
    inventory = build_inventory(entry_texts)
    out_of_stock = set()
    for name, quantity in inventory.items():
        if quantity == 0:
            out_of_stock.add(name)
    ordered_names = tuple(sorted(inventory))
    total_units = sum(inventory.values())
    return "\n".join(
        (
            f"items: {len(inventory)}",
            f"total units: {total_units}",
            f"names ordered: {', '.join(ordered_names)}",
            f"out of stock: {', '.join(sorted(out_of_stock)) or 'none'}",
        )
    )


def main(arguments):
    if not arguments:
        print(
            "usage: python3 inventory_lookup.py NAME=QUANTITY [NAME=QUANTITY ...]",
            file=sys.stderr,
        )
        return 2

    try:
        report = make_report(arguments)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
