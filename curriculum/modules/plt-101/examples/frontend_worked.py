#!/usr/bin/env python3
"""Print one deterministic Pebble frontend result."""

from __future__ import annotations

from frontend import ast_shape, parse_source


SOURCE = "let width = 2 + 3 * 4;\nemit width;\n"


def main() -> int:
    result = parse_source(SOURCE)
    if result.diagnostics or result.program is None:
        for diagnostic in result.diagnostics:
            print(f"{diagnostic.code}:{diagnostic.span.line_start}:{diagnostic.span.column_start}: {diagnostic.message}")
        return 1
    print(f"tokens: {len(result.tokens)}")
    print(f"shape: {ast_shape(result.program)!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
