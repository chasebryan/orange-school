#!/usr/bin/env python3
"""Narrative SAT, UNSAT, and UNKNOWN run for FRM-103."""

from automation_model import CNF, checked_solve, search


sat_problem = CNF(2, ((1, 2), (-1, 2)))
sat_candidate = search(sat_problem)
sat_checked = checked_solve(sat_problem)
print(f"SAT candidate model: {sat_candidate.certificate.assignments}")
print(f"SAT checked claim: {sat_checked.claim}")

unsat_problem = CNF(1, ((1,), (-1,)))
unsat_checked = checked_solve(unsat_problem)
print(f"UNSAT certificate nodes: {unsat_checked.certificate_nodes}")
print(f"UNSAT checked claim: {unsat_checked.claim}")

unknown_checked = checked_solve(unsat_problem, node_budget=1)
print(f"UNKNOWN checked claim: {unknown_checked.claim}")
print("scope: bounded CNF courseware; not an Orange or production-solver claim")
