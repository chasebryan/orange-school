#!/usr/bin/env python3
"""Run the bounded, non-secure CRY-103 worked case."""

from __future__ import annotations

from protocol_record import build_record, encode_bound_context
from toy_group import (
    TOY_GENERATOR,
    TOY_PRIME,
    TOY_SUBGROUP_ORDER,
    toy_agreement_value,
    toy_public_value,
)


def main() -> int:
    alice_scalar = 3
    bob_scalar = 7
    alice_public = toy_public_value(alice_scalar)
    bob_public = toy_public_value(bob_scalar)
    alice_result = toy_agreement_value(alice_scalar, bob_public)
    bob_result = toy_agreement_value(bob_scalar, alice_public)
    if alice_result != bob_result:
        raise AssertionError("toy agreement mechanics diverged")

    messages = (
        b"initiator-offer:orange-school-kem-record-v1",
        b"responder-select:orange-school-kem-record-v1",
        b"public-recipient-key-id:training-responder-7",
    )
    record = build_record(
        messages,
        protocol_id="orange-school-transfer",
        protocol_version=1,
        role="initiator",
        initiator_key_id="training-initiator-3",
        responder_key_id="training-responder-7",
        purpose="bind a public teaching transcript",
    )
    context = encode_bound_context(record, messages)

    print(
        "toy finite-field profile: "
        f"p={TOY_PRIME}, q={TOY_SUBGROUP_ORDER}, g={TOY_GENERATOR}"
    )
    print(f"toy public values: {alice_public}, {bob_public}")
    print(f"toy public teaching result: {alice_result}")
    print(f"record profile: {record['profile_id']}")
    print(f"public transcript hash: {record['transcript_hash']}")
    print(f"bound context bytes: {len(context)}")
    print(
        "security boundary: mechanics only; no encryption, signature, KEM, "
        "or production security"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
