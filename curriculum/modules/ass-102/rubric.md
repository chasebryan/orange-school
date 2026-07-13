# Rubric: Sentinel admission gauntlet

## Rubric

The assessment is worth 100 points. Passing requires at least **80/100** and
every critical criterion. A high total cannot compensate for a shared oracle
presented as independent, an unbound corpus, an unobserved critical mutant, an
unreproducible failure, or an assurance claim broader than the evidence.

## Critical criteria

- Threat hypotheses, generated cases, lineage, canonical corpus bytes, and
  identities are exact, bounded, immutable, independently checked, and cover
  parser, implementation, certificate, policy, artifact, oracle, and
  integration risks.
- At least three meaningfully diverse oracle strategies remain distinguishable;
  properties, metamorphic relations, and differential comparisons have explicit
  domains/preconditions and expose injected oracle errors rather than silently
  voting them away.
- At least 15 target mutants are classified and at least 12 are killed; no
  surviving or unclassified mutant weakens deny, rollback, certificate,
  artifact, or cross-request integration binding in the assessed profile.
- Five category-spanning counterexamples are deterministically minimized under
  their original predicates, and six deliberate target failures are preserved
  before byte-reproducible restored passes.
- Every resource endpoint and smallest overflow is isolated with the intended
  exact diagnostic, including the feasible 52-evaluation maximum and the
  proof that no admitted corpus can request 53 evaluations.
- The final report distinguishes measured coverage from exercised hypotheses,
  records oracle/target/TCB limitations and residual risk, and makes no
  exhaustive, proof, external-system, or Orange claim.

## Scoring

- **ASS-102-01 — hypotheses, generation, lineage, and identity (25):** 6 for
  exact falsifiable hypotheses and mapping; 6 for structured, malformed,
  endpoint, mutation, and regression generation; 5 for immutable canonical
  records and reference validation; 5 for independently reconstructed corpus
  bytes and semantic-field identity changes; 3 for exact provenance and lineage.
- **ASS-102-02 — oracle design and complementary testing (25):** 7 for three
  diverse oracles, shared-dependency audit, and exposed oracle injections; 6
  for properties with valid domains; 6 for checked metamorphic relations; 4 for
  structured differential outcomes and fail-closed target behavior; 2 for
  explaining remaining common-mode oracle risk.
- **ASS-102-03 — mutants and counterexamples (25):** 8 for the complete
  category-balanced mutant ledger and required kills; 6 for stable first
  counterexamples; 6 for deterministic, predicate-preserving minimization with
  honest minimality labels; 5 for six immutable failure/restored-pass pairs.
- **ASS-102-04 — bounds, reproducibility, and calibrated conclusions (25):** 7
  for every feasible endpoint, smallest overflow, interacting-cap arithmetic,
  and exact diagnostic; 6 for deterministic offline replay across working
  directories and hash seeds; 6 for differentiated coverage and instrumentation
  limits; 6 for identities, withdrawal conditions, trust boundary, non-proofs,
  and residual risks.

The four outcome categories total 100 points. Pass only with 80/100 or more and
all critical criteria.

## Feedback and retry

Feedback identifies the first unreproduced observation or invalid inference,
preserves its exact corpus, oracle, target, mutant, command, and status, and maps
it to an ASS-102 outcome. The learner must not overwrite a failure during
repair. Missing executable evidence cannot be replaced by explanation alone.

A retry uses an assessor-supplied manifest profile and frozen expected table;
renames the corpus schema; reduces input, case, relation, and minimization caps;
changes at least two policy decisions; adds a certificate field; replaces at
least five mutants; and supplies one oracle fault that survives the previous
relation set. The learner must recompute generators, lineage, canonical bytes,
identities, feasible endpoints, properties, relations, oracle disagreements,
mutant classifications, minima, failure/restoration evidence, coverage table,
and calibrated report. The 80/100 threshold and every critical criterion apply
again.
