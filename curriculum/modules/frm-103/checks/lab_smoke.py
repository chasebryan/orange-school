#!/usr/bin/env python3
"""Portable boundary and adversarial evidence for FRM-103."""

from __future__ import annotations

from itertools import product
from pathlib import Path
import subprocess
import sys
import tempfile


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from automation_model import (  # noqa: E402
    AutomationError,
    CNF,
    MAX_CERTIFICATE_NODES,
    MAX_CLAUSES,
    MAX_SEARCH_NODES,
    MAX_VARIABLES,
    ModelCertificate,
    RefutedClause,
    SearchResult,
    Split,
    check_model,
    check_result,
    check_unsat_certificate,
    checked_solve,
    search,
    validate_cnf,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect(code: str, message: str, action) -> None:
    try:
        action()
    except AutomationError as error:
        require(error.code == code, f"expected {code}, got {error.code}")
        require(error.message == message, f"message changed: {error.message!r}")
        require(str(error) == f"{code}: {message}", "rendered diagnostic changed")
        return
    raise AssertionError(f"expected {code}")


def exclusion_problem() -> CNF:
    """Exclude all assignments to variables 1..5 using exactly 32 clauses."""

    clauses = []
    for values in product((False, True), repeat=5):
        clauses.append(
            tuple(-variable if values[variable - 1] else variable for variable in range(1, 6))
        )
    return CNF(MAX_VARIABLES, tuple(clauses))


def expand_rightmost(certificate):
    """Grow a 63-node refutation to the smallest binary overflow: 65."""

    if type(certificate) is RefutedClause:
        return Split(6, certificate, certificate)
    return Split(
        certificate.variable,
        certificate.when_false,
        expand_rightmost(certificate.when_true),
    )


def check_statuses_and_independent_checking() -> None:
    sat = CNF(2, ((1, 2), (-1, 2)))
    sat_candidate = search(sat)
    require(sat_candidate.status == "sat", "satisfiable input did not produce SAT")
    require(
        sat_candidate.certificate == ModelCertificate((False, True)),
        "deterministic SAT witness changed",
    )
    require(check_model(sat, sat_candidate.certificate) == 1, "SAT witness did not check")
    require(check_result(sat, sat_candidate).status == "sat", "SAT result did not check")

    unsat = CNF(1, ((1,), (-1,)))
    unsat_candidate = search(unsat)
    require(unsat_candidate.status == "unsat", "contradiction did not produce UNSAT")
    require(check_unsat_certificate(unsat, unsat_candidate.certificate) == 3, "UNSAT tree changed")
    require(check_result(unsat, unsat_candidate).status == "unsat", "UNSAT result did not check")

    unknown = search(unsat, node_budget=1)
    require(unknown == SearchResult("unknown", None, 1), "budget exhaustion changed")
    checked_unknown = check_result(unsat, unknown)
    require(checked_unknown.status == "unknown", "UNKNOWN result changed")
    require("not established" in checked_unknown.claim, "UNKNOWN was strengthened")

    six_variable_unresolved = CNF(6, ((1, 2, 3, 4, 5), (6,)))
    result = search(six_variable_unresolved)
    require(result.status in ("sat", "unknown"), "sound status vocabulary escaped")


def check_joint_endpoints() -> None:
    endpoint = exclusion_problem()
    require(endpoint.variable_count == MAX_VARIABLES, "variable endpoint changed")
    require(len(endpoint.clauses) == MAX_CLAUSES, "clause endpoint changed")
    require(all(len(clause) == 5 for clause in endpoint.clauses), "literal endpoint changed")
    require(validate_cnf(endpoint) is endpoint, "endpoint CNF did not validate")

    exact = search(endpoint, node_budget=MAX_SEARCH_NODES)
    require(exact.status == "unsat", "63-node endpoint did not finish")
    require(exact.search_nodes == MAX_SEARCH_NODES, "search endpoint count changed")
    require(
        check_unsat_certificate(endpoint, exact.certificate) == MAX_CERTIFICATE_NODES,
        "certificate endpoint count changed",
    )
    one_short = search(endpoint, node_budget=MAX_SEARCH_NODES - 1)
    require(one_short.status == "unknown", "62-node search made a logical conclusion")
    require(one_short.search_nodes == MAX_SEARCH_NODES - 1, "short-budget count changed")

    overflow = expand_rightmost(exact.certificate)
    expect(
        "C005",
        "certificate node count exceeds 63",
        lambda: check_unsat_certificate(endpoint, overflow),
    )

    # Five decisions give depth 6. Splitting once more is the isolated depth-7
    # attempt and remains far below the node cap.
    chain_problem = CNF(6, ((1,), (2,), (3,), (4,), (5,), (-5,)))
    chain = search(chain_problem).certificate
    require(check_unsat_certificate(chain_problem, chain) == 11, "depth endpoint changed")

    def deepen_rightmost(certificate):
        if type(certificate) is RefutedClause:
            return Split(6, certificate, certificate)
        return Split(
            certificate.variable,
            certificate.when_false,
            deepen_rightmost(certificate.when_true),
        )

    expect(
        "C006",
        "certificate depth exceeds 6",
        lambda: check_unsat_certificate(chain_problem, deepen_rightmost(chain)),
    )

    expect("I002", "variable count must be an integer from 1 through 6", lambda: validate_cnf(CNF(7, ((1,),))))
    expect("I003", "CNF must contain from 1 through 32 clauses", lambda: validate_cnf(CNF(1, ((1,),) * 33)))
    expect("I004", "each clause must contain from 1 through 5 literals", lambda: validate_cnf(CNF(1, ((1,) * 6,))))
    expect("I006", "search budget must be an integer from 1 through 63", lambda: search(CNF(1, ((1,),)), 64))


def check_malformed_and_adversarial_certificates() -> None:
    class SpoofedStatus:
        def __eq__(self, other: object) -> bool:
            return other == "sat"

    problem = CNF(2, ((1,), (-1, 2)))
    expect("I001", "unsupported CNF object", lambda: validate_cnf(object()))
    expect("I002", "variable count must be an integer from 1 through 6", lambda: validate_cnf(CNF(True, ((1,),))))
    expect("I003", "CNF must contain from 1 through 32 clauses", lambda: validate_cnf(CNF(1, ())))
    expect("I004", "each clause must contain from 1 through 5 literals", lambda: validate_cnf(CNF(1, ((1,), []))))
    expect("I005", "literal must be a nonzero integer within the declared variables", lambda: validate_cnf(CNF(1, ((0,),))))
    expect("I005", "literal must be a nonzero integer within the declared variables", lambda: validate_cnf(CNF(1, ((True,),))))

    expect("M001", "SAT result requires a model certificate", lambda: check_model(problem, object()))
    expect("M002", "model must assign every declared variable exactly once", lambda: check_model(problem, ModelCertificate((True,))))
    expect("M003", "model assignments must be Boolean values", lambda: check_model(problem, ModelCertificate((1, True))))
    expect("M004", "model does not satisfy every clause", lambda: check_model(problem, ModelCertificate((False, False))))

    expect("C001", "unsupported UNSAT certificate object", lambda: check_unsat_certificate(problem, object()))
    expect("C002", "refuted-clause index is outside the CNF", lambda: check_unsat_certificate(problem, RefutedClause(True)))
    expect("C003", "referenced clause is not falsified by this branch", lambda: check_unsat_certificate(problem, RefutedClause(0)))
    expect("C004", "split variable is outside the CNF", lambda: check_unsat_certificate(problem, Split(3, RefutedClause(0), RefutedClause(0))))

    repeated = Split(1, RefutedClause(0), Split(1, RefutedClause(0), RefutedClause(0)))
    expect("C008", "split variable is repeated on this branch", lambda: check_unsat_certificate(CNF(1, ((1,), (-1,))), repeated))

    cyclic = Split(1, RefutedClause(0), RefutedClause(0))
    object.__setattr__(cyclic, "when_false", cyclic)
    expect("C007", "cyclic certificate", lambda: check_unsat_certificate(CNF(1, ((1,), (-1,))), cyclic))

    shared = Split(2, RefutedClause(0), RefutedClause(1))
    shared_tree = Split(1, shared, shared)
    require(
        check_unsat_certificate(CNF(2, ((2,), (-2,))), shared_tree) == 7,
        "shared certificate subtree was not recounted per visit",
    )
    expect(
        "C001",
        "unsupported UNSAT certificate object",
        lambda: check_unsat_certificate(
            CNF(1, ((1,), (-1,))), Split(1, None, RefutedClause(1))
        ),
    )

    expect("R001", "unsupported search-result object", lambda: check_result(problem, object()))
    expect("R002", "search-node count is outside the declared bound", lambda: check_result(problem, SearchResult("unknown", None, True)))
    expect(
        "R003",
        "status must be sat, unsat, or unknown",
        lambda: check_result(
            problem, SearchResult(SpoofedStatus(), ModelCertificate((True, True)), 1)
        ),
    )
    expect("R003", "status must be sat, unsat, or unknown", lambda: check_result(problem, SearchResult("timeout", None, 1)))
    expect("R004", "unknown result must not carry a certificate", lambda: check_result(problem, SearchResult("unknown", ModelCertificate((True, True)), 1)))


def check_deliberate_failures_and_recovery() -> None:
    sat = CNF(2, ((1, 2), (-1, 2)))
    expect(
        "M004",
        "model does not satisfy every clause",
        lambda: check_model(sat, ModelCertificate((False, False))),
    )
    require(check_model(sat, ModelCertificate((False, True))) == 1, "restored SAT model failed")

    unsat = CNF(1, ((1,), (-1,)))
    valid = search(unsat)
    corrupted = Split(1, RefutedClause(1), RefutedClause(1))
    expect(
        "C003",
        "referenced clause is not falsified by this branch",
        lambda: check_unsat_certificate(unsat, corrupted),
    )
    require(check_result(unsat, valid).status == "unsat", "restored UNSAT certificate failed")

    forged = SearchResult("unsat", ModelCertificate((True,)), 1)
    expect(
        "C001",
        "unsupported UNSAT certificate object",
        lambda: check_result(unsat, forged),
    )
    require(checked_solve(unsat).status == "unsat", "fail-closed workflow did not recover")


def check_worked_program() -> None:
    with tempfile.TemporaryDirectory(prefix="frm-103-smoke-") as temporary:
        result = subprocess.run(
            [sys.executable, "-B", str(EXAMPLES / "worked_automation.py")],
            cwd=temporary,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        require(result.returncode == 0, f"worked program failed: {result.stderr}")
        require(result.stderr == "", "worked program wrote stderr")
        require("SAT candidate model: (False, True)" in result.stdout, "SAT output changed")
        require("UNSAT certificate nodes: 3" in result.stdout, "UNSAT output changed")
        require("satisfiability is not established" in result.stdout, "UNKNOWN scope changed")
        require("not an Orange or production-solver claim" in result.stdout, "scope warning missing")
        require(list(Path(temporary).iterdir()) == [], "worked program created a repository-external artifact")


def main() -> int:
    check_statuses_and_independent_checking()
    check_joint_endpoints()
    check_malformed_and_adversarial_certificates()
    check_deliberate_failures_and_recovery()
    check_worked_program()
    print("frm-103 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
