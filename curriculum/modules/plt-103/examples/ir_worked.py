#!/usr/bin/env python3
"""Print one deterministic Cairn lowering and artifact result."""

from __future__ import annotations

import hashlib

from ir_pipeline import (
    Add,
    Choose,
    IntLiteral,
    Less,
    Let,
    Name,
    decode,
    encode,
    evaluate_source,
    execute_ir,
    lower,
)


EXPRESSION = Let(
    "base",
    Add(IntLiteral(20), IntLiteral(1)),
    Choose(
        Less(Name("base"), IntLiteral(22)),
        Add(Name("base"), Name("base")),
        IntLiteral(0),
    ),
)


def main() -> int:
    source_value = evaluate_source(EXPRESSION)
    program = lower(EXPRESSION)
    artifact = encode(program)
    decoded_value = execute_ir(decode(artifact))
    if source_value != decoded_value:
        return 1
    print(f"source: {source_value.type_name} {source_value.value}")
    print(f"instructions: {len(program.instructions)}")
    print(f"artifact-bytes: {len(artifact)}")
    print(f"artifact-sha256: {hashlib.sha256(artifact).hexdigest()}")
    print(f"decoded: {decoded_value.type_name} {decoded_value.value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
