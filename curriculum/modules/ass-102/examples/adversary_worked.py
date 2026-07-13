#!/usr/bin/env python3
"""Worked Gauntlet corpus spanning five adversarial-validation subjects."""

from __future__ import annotations

import hashlib
import re
import sys

from adversary_model import (
    Case,
    Corpus,
    Outcome,
    Relation,
    RelationExpectation,
    SubjectKind,
    Threat,
    derive_case,
    minimize_counterexample,
    run_suite,
)


LIMITATION = (
    "The report binds corpus bytes, not oracle or target callable identity. "
    "Finite model observations only; not exhaustive coverage, proof, or an "
    "Orange capability, safety, security, conformance, or release claim."
)


def _reject(code: str) -> Outcome:
    return Outcome(False, code, "")


def _accept(value: str) -> Outcome:
    return Outcome(True, "ok", value)


def reference_system(data: bytes) -> Outcome:
    """Specification oracle with strict, explicit parsing paths."""

    try:
        text = data.decode("ascii")
    except UnicodeDecodeError:
        return _reject("non-ascii")

    if text.startswith("P:"):
        token = text[2:]
        if re.fullmatch(r"(?:0|[1-9][0-9]{0,2})", token) is None:
            return _reject("parser-syntax")
        value = int(token, 10)
        return _accept(f"integer:{value}") if value <= 255 else _reject("parser-range")

    if text.startswith("I:"):
        match = re.fullmatch(r"I:(-?(?:0|[1-9][0-9]?))\+(-?(?:0|[1-9][0-9]?))", text)
        if match is None:
            return _reject("implementation-syntax")
        left, right = int(match.group(1)), int(match.group(2))
        if not (-99 <= left <= 99 and -99 <= right <= 99):
            return _reject("implementation-range")
        return _accept(f"sum:{left + right}")

    if text.startswith("C:"):
        match = re.fullmatch(r"C:([2-9][0-9]?)\|([2-9][0-9]?)\|([2-9][0-9]?)", text)
        if match is None:
            return _reject("certificate-syntax")
        number, divisor, quotient = (int(item) for item in match.groups())
        if number != divisor * quotient:
            return _reject("certificate-invalid")
        return _accept("certificate-valid")

    if text.startswith("Y:"):
        fields = text.split("|")
        if len(fields) != 2 or not fields[0].startswith("Y:"):
            return _reject("policy-syntax")
        role, action = fields[0][2:], fields[1]
        decisions = {("admin", "deploy"): "allow", ("auditor", "read"): "allow"}
        return _accept(decisions.get((role, action), "deny"))

    if text.startswith("A:"):
        fields = text.split(":")
        if len(fields) != 3 or not fields[1] or re.fullmatch(r"[0-9a-f]{64}", fields[2]) is None:
            return _reject("artifact-syntax")
        observed = hashlib.sha256(fields[1].encode("ascii")).hexdigest()
        return _accept("digest-match") if observed == fields[2] else _reject("artifact-mismatch")

    return _reject("unknown-subject")


def candidate_system(data: bytes, *, leading_zero_bug: bool = False) -> Outcome:
    """Separately implemented target; the option injects one parser mutant."""

    try:
        message = data.decode("ascii")
    except UnicodeDecodeError:
        return Outcome(False, "non-ascii", "")

    prefix, separator, body = message.partition(":")
    if not separator:
        return Outcome(False, "unknown-subject", "")
    if prefix == "P":
        pattern = r"[0-9]{1,3}" if leading_zero_bug else r"(?:0|[1-9][0-9]{0,2})"
        if re.fullmatch(pattern, body) is None:
            return Outcome(False, "parser-syntax", "")
        number = int(body)
        if number > 255:
            return Outcome(False, "parser-range", "")
        return Outcome(True, "ok", f"integer:{number}")
    if prefix == "I":
        parts = re.fullmatch(r"(-?(?:0|[1-9][0-9]?))\+(-?(?:0|[1-9][0-9]?))", body)
        if parts is None:
            return Outcome(False, "implementation-syntax", "")
        a, b = map(int, parts.groups())
        if min(a, b) < -99 or max(a, b) > 99:
            return Outcome(False, "implementation-range", "")
        return Outcome(True, "ok", "sum:" + str(a + b))
    if prefix == "C":
        pieces = body.split("|")
        if len(pieces) != 3 or any(re.fullmatch(r"[2-9][0-9]?", item) is None for item in pieces):
            return Outcome(False, "certificate-syntax", "")
        n, d, q = map(int, pieces)
        if d * q != n:
            return Outcome(False, "certificate-invalid", "")
        return Outcome(True, "ok", "certificate-valid")
    if prefix == "Y":
        pieces = body.split("|")
        if len(pieces) != 2:
            return Outcome(False, "policy-syntax", "")
        allowed = pieces in (["admin", "deploy"], ["auditor", "read"])
        return Outcome(True, "ok", "allow" if allowed else "deny")
    if prefix == "A":
        pieces = body.split(":")
        if len(pieces) != 2 or not pieces[0] or re.fullmatch(r"[0-9a-f]{64}", pieces[1]) is None:
            return Outcome(False, "artifact-syntax", "")
        digest = hashlib.sha256(pieces[0].encode("ascii")).hexdigest()
        if digest != pieces[1]:
            return Outcome(False, "artifact-mismatch", "")
        return Outcome(True, "ok", "digest-match")
    return Outcome(False, "unknown-subject", "")


def correct_target(data: bytes) -> Outcome:
    return candidate_system(data)


def leading_zero_mutant(data: bytes) -> Outcome:
    return candidate_system(data, leading_zero_bug=True)


def make_corpus() -> Corpus:
    digest = hashlib.sha256(b"release-7").hexdigest()
    threats = (
        Threat("artifact-binding", SubjectKind.ARTIFACT, "content may be checked against the wrong digest", "full fictional SHA-256 field"),
        Threat("certificate-gap", SubjectKind.CERTIFICATE, "a malformed or false multiplication witness may pass", "exact bounded multiplication relation"),
        Threat("implementation-boundary", SubjectKind.IMPLEMENTATION, "arithmetic syntax or endpoints may diverge", "mathematical integer addition over -99..99"),
        Threat("parser-confusion", SubjectKind.PARSER, "noncanonical or malformed numerals may be accepted", "canonical decimal grammar and 0..255 range"),
        Threat("policy-normalization", SubjectKind.POLICY, "case or whitespace normalization may grant access", "exact role-action decision table"),
    )
    parser_seed = Case("p-seven", SubjectKind.PARSER, b"P:7", "seed", ("parser-confusion",))
    cases = (
        Case("a-match", SubjectKind.ARTIFACT, f"A:release-7:{digest}".encode(), "structured", ("artifact-binding",)),
        Case("a-mismatch", SubjectKind.ARTIFACT, f"A:release-8:{digest}".encode(), "structured", ("artifact-binding",)),
        Case("a-short", SubjectKind.ARTIFACT, b"A:release-7:1234", "malformed", ("artifact-binding",)),
        Case("c-false", SubjectKind.CERTIFICATE, b"C:21|3|8", "structured", ("certificate-gap",)),
        Case("c-malformed", SubjectKind.CERTIFICATE, b"C:21|one|7", "malformed", ("certificate-gap",)),
        Case("c-valid", SubjectKind.CERTIFICATE, b"C:21|3|7", "structured", ("certificate-gap",)),
        Case("i-commuted", SubjectKind.IMPLEMENTATION, b"I:3+2", "structured", ("implementation-boundary",)),
        Case("i-high", SubjectKind.IMPLEMENTATION, b"I:99+99", "endpoint", ("implementation-boundary",)),
        Case("i-source", SubjectKind.IMPLEMENTATION, b"I:2+3", "seed", ("implementation-boundary",)),
        Case("i-syntax", SubjectKind.IMPLEMENTATION, b"I:01+2", "malformed", ("implementation-boundary",)),
        derive_case(parser_seed, identifier="p-leading-zero", data=b"P:07", operator="prepend-zero"),
        Case("p-nonascii", SubjectKind.PARSER, b"P:\xff", "malformed", ("parser-confusion",)),
        Case("p-range", SubjectKind.PARSER, b"P:256", "endpoint", ("parser-confusion",)),
        parser_seed,
        derive_case(parser_seed, identifier="p-truncated", data=b"P:", operator="truncate"),
        Case("y-admin", SubjectKind.POLICY, b"Y:admin|deploy", "structured", ("policy-normalization",)),
        Case("y-case", SubjectKind.POLICY, b"Y:Admin|deploy", "mutation", ("policy-normalization",), "y-admin", "change-case"),
        Case("y-deny", SubjectKind.POLICY, b"Y:auditor|deploy", "structured", ("policy-normalization",)),
    )
    relations = (
        Relation("addition-commutes", "i-source", "i-commuted", RelationExpectation.SAME),
        Relation("artifact-change", "a-match", "a-mismatch", RelationExpectation.DIFFERENT),
        Relation("canonical-decimal", "p-seven", "p-leading-zero", RelationExpectation.FOLLOWUP_REJECTS),
        Relation("policy-case-sensitive", "y-admin", "y-case", RelationExpectation.DIFFERENT),
    )
    return Corpus("gauntlet-five-subject-worked", threats, cases, relations)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in {"pass", "mutant", "minimize"}:
        print("usage: adversary_worked.py {pass|mutant|minimize}", file=sys.stderr)
        return 2
    corpus = make_corpus()
    target = correct_target if argv[1] == "pass" else leading_zero_mutant
    report = run_suite(corpus, oracle=reference_system, target=target)
    print(f"corpus: {report.corpus_identity}")
    print(f"cases: {len(report.observations)}")
    print(f"threats: {len(report.exercised_threats)}/{len(corpus.threats)}")
    for finding in report.findings:
        print(f"finding: {finding.code} at {finding.location}: {finding.detail}")
    if argv[1] == "minimize":
        result = minimize_counterexample(
            b"P:07", lambda data: reference_system(data) != leading_zero_mutant(data)
        )
        print(f"minimized-hex: {result.data.hex()}")
        print(f"minimizer-evaluations: {result.evaluations}")
        print(f"one-minimal: {str(result.one_minimal).lower()}")
    print("result: " + ("PASS" if report.passed else "FAIL"))
    print("limitation: " + LIMITATION)
    return 0 if report.passed else 4


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
