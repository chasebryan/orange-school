#!/usr/bin/env python3
"""Replay the FRM-102 worked certificates."""

from proof_kernel import (
    And,
    AndElimLeft,
    Atom,
    Axiom,
    AxiomSpec,
    Hyp,
    Imp,
    ImpElim,
    ImpIntro,
    Kernel,
)


ready = Atom("Ready")
safe = Atom("Safe")

# No axioms: (Ready and Safe) -> Ready.
projection = ImpIntro("pair", And(ready, safe), AndElimLeft(Hyp("pair")))
closed = Kernel().check(projection, Imp(And(ready, safe), ready))
print("closed conclusion:", closed.conclusion)
print("closed axioms:", closed.axioms_used)

# The registry, rather than the proof object, chooses an axiom's proposition.
kernel = Kernel((AxiomSpec("deployment_ready", ready),))
identity = ImpIntro("r", ready, Hyp("r"))
from_trust = ImpElim(identity, Axiom("deployment_ready"))
trusted = kernel.check(from_trust, ready)
print("trusted conclusion:", trusted.conclusion)
print("trusted axioms:", trusted.axioms_used)
print("proof nodes:", trusted.proof_nodes)

