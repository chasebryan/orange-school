# Rubric: independent Flint proof certificates

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Propositions, judgments, and certificate rules | 20 | Exact Flint syntax, written inference rules, assumption scope/discharge, and axiom distinction |
| Kernel and resource integrity | 30 | Faithful checking, stable failures, cycle/malformed defenses, exact bounds, and no partial success |
| Trust and claim discipline | 20 | Used-axiom provenance, complete trust inventory, conditional acceptance claim, and explicit non-proofs |
| Verification and failure sensitivity | 20 | Complete rules, jointly feasible endpoints, malformed cases, replay, and six observed mutation/restoration pairs |
| Reproducibility | 10 | Temporary path, source hashes, commands, separate channels, statuses, and bounded-work argument |
| **Total** | **100** |  |

The passing threshold is **80/100**, and every critical criterion below must
pass. A high total cannot compensate for a failed critical criterion.

## Critical criteria

1. **Rule integrity:** earn at least 16/20 for proposition and certificate
   rules. Every introduction, elimination, assumption-scope, branch, and
   discharge edge must match the written Flint judgment.
2. **Kernel integrity:** earn at least 24/30. The checker must reject every
   malformed, cyclic, unbound, wrongly typed, mismatched, and over-limit object
   before acceptance, with the registry controlling axiom propositions.
3. **Trust integrity:** earn at least 16/20. Every accepted theorem must retain
   open assumptions and exactly used axioms, and the submission must inventory
   the checker and host trust base without an unsupported soundness or Orange
   claim.
4. **Failure-sensitive evidence:** earn at least 16/20. All rules and isolated
   endpoint/next-operation cases must execute, and all six deliberate mutations
   must fail observably before their restored forms pass.

## Scoring

- **Propositions, judgments, and certificate rules (20):** 6 for exact
  immutable syntax and names; 9 for complete written rules including
  disjunction branch discharge; 5 for correct assumption/axiom distinctions.
- **Kernel and resource integrity (30):** 12 for faithful inference and exact
  structural checks; 8 for stable malformed/cycle rejection; 10 for visit,
  depth, proposition, context, and registry boundaries checked before work.
- **Trust and claim discipline (20):** 7 for exact assumption and used-axiom
  provenance; 8 for a concrete trusted-computing-base inventory; 5 for
  conditional conclusions and explicit theorem, host, security, and Orange
  non-claims.
- **Verification and failure sensitivity (20):** 5 for positive rule cases; 5
  for invalid and jointly feasible endpoints; 4 for deterministic replay; 6
  for six captured mutation-failure/restoration pairs.
- **Reproducibility (10):** 6 for paths, versions, hashes, commands, channels,
  and immediate statuses; 4 for justified work/retention bounds without exact
  host-memory claims.

Pass only with at least 80/100 and all four critical criteria.

## Feedback and retry

Feedback identifies the first incorrect inference premise, discharge boundary,
formula comparison, registry dependency, resource check, malformed-object
path, mutation record, or trust claim. It maps the missing evidence to
**FRM-102-01**, **FRM-102-02**, **FRM-102-03**, or **FRM-102-04**. Preserve the
original submission and evidence before retrying.

A retry uses assessor-selected atom names, reordered constructors, a changed
label grammar, changed caps, a different axiom registry, two new disjunction
branch cases, and two new mutations. The learner must restate rules, rebuild
endpoint shapes, regenerate hashes and channel/status evidence, and revise the
trust inventory. Prose cannot replace executable evidence for a failed rule,
bound, registry, replay, or mutation criterion.

