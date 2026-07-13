"""Bounded CNF search and independently checked teaching certificates.

This is Python 3.11 courseware, not an Orange component, production solver,
or proof that this implementation is sound.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias


MAX_VARIABLES = 6
MAX_CLAUSES = 32
MAX_CLAUSE_LITERALS = 5
MAX_SEARCH_NODES = 63
MAX_CERTIFICATE_NODES = 63
MAX_CERTIFICATE_DEPTH = 6


class AutomationError(ValueError):
    """Stable fail-closed input or certificate rejection."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class CNF:
    variable_count: int
    clauses: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class ModelCertificate:
    assignments: tuple[bool, ...]


@dataclass(frozen=True)
class RefutedClause:
    clause_index: int


@dataclass(frozen=True)
class Split:
    variable: int
    when_false: "UnsatCertificate"
    when_true: "UnsatCertificate"


UnsatCertificate: TypeAlias = RefutedClause | Split
Certificate: TypeAlias = ModelCertificate | UnsatCertificate


@dataclass(frozen=True)
class SearchResult:
    status: str
    certificate: Certificate | None
    search_nodes: int


@dataclass(frozen=True)
class CheckedResult:
    status: str
    certificate_nodes: int
    claim: str


def validate_cnf(problem: object) -> CNF:
    """Validate the complete bounded input before search or checking."""

    if type(problem) is not CNF:
        raise AutomationError("I001", "unsupported CNF object")
    if (
        type(problem.variable_count) is not int
        or not 1 <= problem.variable_count <= MAX_VARIABLES
    ):
        raise AutomationError("I002", "variable count must be an integer from 1 through 6")
    if (
        type(problem.clauses) is not tuple
        or not 1 <= len(problem.clauses) <= MAX_CLAUSES
    ):
        raise AutomationError("I003", "CNF must contain from 1 through 32 clauses")
    for clause in problem.clauses:
        if (
            type(clause) is not tuple
            or not 1 <= len(clause) <= MAX_CLAUSE_LITERALS
        ):
            raise AutomationError("I004", "each clause must contain from 1 through 5 literals")
        for literal in clause:
            if (
                type(literal) is not int
                or literal == 0
                or abs(literal) > problem.variable_count
            ):
                raise AutomationError(
                    "I005", "literal must be a nonzero integer within the declared variables"
                )
    return problem


def _literal_value(literal: int, assignment: dict[int, bool]) -> bool | None:
    value = assignment.get(abs(literal))
    if value is None:
        return None
    return value if literal > 0 else not value


def _clause_is_false(clause: tuple[int, ...], assignment: dict[int, bool]) -> bool:
    values = tuple(_literal_value(literal, assignment) for literal in clause)
    return all(value is False for value in values)


def _clause_is_true(clause: tuple[int, ...], assignment: dict[int, bool]) -> bool:
    return any(_literal_value(literal, assignment) is True for literal in clause)


def check_model(problem: object, certificate: object) -> int:
    """Independently validate a complete SAT model witness."""

    checked = validate_cnf(problem)
    if type(certificate) is not ModelCertificate:
        raise AutomationError("M001", "SAT result requires a model certificate")
    if (
        type(certificate.assignments) is not tuple
        or len(certificate.assignments) != checked.variable_count
    ):
        raise AutomationError("M002", "model must assign every declared variable exactly once")
    if any(type(value) is not bool for value in certificate.assignments):
        raise AutomationError("M003", "model assignments must be Boolean values")
    assignment = {
        variable: certificate.assignments[variable - 1]
        for variable in range(1, checked.variable_count + 1)
    }
    if not all(_clause_is_true(clause, assignment) for clause in checked.clauses):
        raise AutomationError("M004", "model does not satisfy every clause")
    return 1


def check_unsat_certificate(problem: object, certificate: object) -> int:
    """Check that a split tree covers all assignments with refuted clauses."""

    checked = validate_cnf(problem)
    active: set[int] = set()
    nodes = 0

    def visit(current: object, assignment: dict[int, bool], depth: int) -> None:
        nonlocal nodes
        if nodes >= MAX_CERTIFICATE_NODES:
            raise AutomationError("C005", "certificate node count exceeds 63")
        if depth > MAX_CERTIFICATE_DEPTH:
            raise AutomationError("C006", "certificate depth exceeds 6")
        nodes += 1
        identity = id(current)
        if identity in active:
            raise AutomationError("C007", "cyclic certificate")
        active.add(identity)
        try:
            if type(current) is RefutedClause:
                if (
                    type(current.clause_index) is not int
                    or not 0 <= current.clause_index < len(checked.clauses)
                ):
                    raise AutomationError("C002", "refuted-clause index is outside the CNF")
                clause = checked.clauses[current.clause_index]
                if not _clause_is_false(clause, assignment):
                    raise AutomationError(
                        "C003", "referenced clause is not falsified by this branch"
                    )
                return
            if type(current) is Split:
                if (
                    type(current.variable) is not int
                    or not 1 <= current.variable <= checked.variable_count
                ):
                    raise AutomationError("C004", "split variable is outside the CNF")
                if current.variable in assignment:
                    raise AutomationError("C008", "split variable is repeated on this branch")
                assignment[current.variable] = False
                visit(current.when_false, assignment, depth + 1)
                assignment[current.variable] = True
                visit(current.when_true, assignment, depth + 1)
                del assignment[current.variable]
                return
            raise AutomationError("C001", "unsupported UNSAT certificate object")
        finally:
            active.remove(identity)

    visit(certificate, {}, 1)
    return nodes


def search(problem: object, node_budget: int = MAX_SEARCH_NODES) -> SearchResult:
    """Produce a candidate model or refutation, or report bounded unknown.

    The producer is deliberately separate from ``check_result``. Callers must
    not treat its status as checked evidence merely because the producer said
    so.
    """

    checked = validate_cnf(problem)
    if type(node_budget) is not int or not 1 <= node_budget <= MAX_SEARCH_NODES:
        raise AutomationError("I006", "search budget must be an integer from 1 through 63")
    nodes = 0

    def explore(assignment: dict[int, bool]) -> tuple[str, Certificate | None]:
        nonlocal nodes
        if nodes >= node_budget:
            return "unknown", None
        nodes += 1

        for index, clause in enumerate(checked.clauses):
            if _clause_is_false(clause, assignment):
                return "unsat", RefutedClause(index)

        if all(_clause_is_true(clause, assignment) for clause in checked.clauses):
            complete = tuple(assignment.get(variable, False) for variable in range(1, checked.variable_count + 1))
            return "sat", ModelCertificate(complete)

        # Certificates admit five split levels. A sixth unresolved variable is
        # a sound UNKNOWN, not permission to emit a certificate the checker
        # cannot replay within its depth envelope.
        if len(assignment) >= MAX_CERTIFICATE_DEPTH - 1:
            return "unknown", None

        variable = next(
            variable
            for variable in range(1, checked.variable_count + 1)
            if variable not in assignment
        )
        assignment[variable] = False
        false_status, false_certificate = explore(assignment)
        assignment[variable] = True
        true_status, true_certificate = explore(assignment)
        del assignment[variable]

        if false_status == "sat":
            return false_status, false_certificate
        if true_status == "sat":
            return true_status, true_certificate
        if false_status == "unknown" or true_status == "unknown":
            return "unknown", None
        assert isinstance(false_certificate, (RefutedClause, Split))
        assert isinstance(true_certificate, (RefutedClause, Split))
        return "unsat", Split(variable, false_certificate, true_certificate)

    status, certificate = explore({})
    return SearchResult(status, certificate, nodes)


def check_result(problem: object, result: object) -> CheckedResult:
    """Fail closed unless a candidate has the certificate its status needs."""

    checked = validate_cnf(problem)
    if type(result) is not SearchResult:
        raise AutomationError("R001", "unsupported search-result object")
    if (
        type(result.search_nodes) is not int
        or not 1 <= result.search_nodes <= MAX_SEARCH_NODES
    ):
        raise AutomationError("R002", "search-node count is outside the declared bound")
    if type(result.status) is not str:
        raise AutomationError("R003", "status must be sat, unsat, or unknown")
    if result.status == "sat":
        certificate_nodes = check_model(checked, result.certificate)
        return CheckedResult("sat", certificate_nodes, "a checked model satisfies this bounded CNF")
    if result.status == "unsat":
        certificate_nodes = check_unsat_certificate(checked, result.certificate)
        return CheckedResult(
            "unsat", certificate_nodes, "a checked split certificate refutes every assignment"
        )
    if result.status == "unknown":
        if result.certificate is not None:
            raise AutomationError("R004", "unknown result must not carry a certificate")
        return CheckedResult(
            "unknown", 0, "this candidate carries no proof; satisfiability is not established"
        )
    raise AutomationError("R003", "status must be sat, unsat, or unknown")


def checked_solve(problem: object, node_budget: int = MAX_SEARCH_NODES) -> CheckedResult:
    """Run the producer and fail-closed checker in sequence."""

    result = search(problem, node_budget)
    return check_result(problem, result)
