# Competency matrix

The canonical matrix is machine-readable in
[`curriculum/catalog.json`](../curriculum/catalog.json). This page is the human
view. A mapping means the named module is responsible for instruction, guided
practice, and assessment. Its status still controls whether that evidence is
available now.

## Foundations

| Competency | Evidence module or modules | Status |
| --- | --- | --- |
| CMP-01 — terminal, files, processes, exact commands | `cmp-101` | Released |
| CMP-02 — Git, tests, debugging, CI | `cmp-102`, `cmp-103` | Released |
| PRG-01 — program structure and state | `prg-101` | Released |
| PRG-02 — types, errors, tests, debugging | `prg-103` | Released |
| PRG-03 — data structures, algorithms, bounds | `prg-102` | Released |
| PRG-04 — C and Rust systems work | `prg-104` | Released |
| MAT-01 — logic and proof techniques | `mat-101` | Released |
| MAT-02 — number theory, algebra, finite fields | `mat-102`, `mat-103` | Released |
| MAT-03 — discrete probability and statistics | `mat-104` | Released |
| CRY-01 — goals, attackers, assumptions | `cry-101` | Released |
| CRY-02 — primitives, constructions, misuse | `cry-102`, `cry-103` | Released |
| CRY-03 — standards, errata, provenance, vectors | `cry-104` | Released |
| SYS-01 — representation, arithmetic, memory, ownership | `sys-101`, `sys-102` | Released |
| SYS-02 — objects, ABIs, targets, SIMD, dispatch | `sys-103`, `sys-104` | Released |
| SYS-03 — leakage and side-channel evidence | `sys-105`, `org-302` | Foundation released; Orange use blocked |
| PLT-01 — lexers, parsers, diagnostics, bounds | `plt-101`, `org-102` | Foundation and Orange frontend slice released |
| PLT-02 — semantics, names, types, effects | `plt-102`, `org-201` | Foundation and narrow S3a typed-literal use released; broader Orange semantics blocked |
| PLT-03 — compiler IR and preservation | `plt-103`, `org-401` | Foundation released; Orange use blocked |
| FRM-01 — specifications, contracts, refinement | `frm-101`, `org-202` | Foundation released; Orange use blocked |
| FRM-02 — proof checking and automation | `frm-102`, `frm-103`, `org-301` | Foundation released; Orange use blocked |
| FRM-03 — games and reductions | `frm-104`, `org-302` | Foundation released; Orange use blocked |
| ASS-01 — scoped claims, assumptions, TCB | `ori-001`, `ass-101`, `org-201`, `org-301` | Foundation and S3a claim-boundary use released; Orange proof use blocked |
| ASS-02 — adversarial validation | `ass-102`, `org-103` | Foundation and Orange frontend slice released |
| ASS-03 — reproducibility and offline replay | `ass-103`, `org-403` | Foundation released; Orange use blocked |
| ASS-04 — lifecycle and incident response | `ass-104`, `org-404` | Foundation released; Orange use blocked |

## Orange operations

| Competency | Journey | Evidence module | Status at pinned revision |
| --- | --- | --- | --- |
| ORG-01 — exact toolchain and honest capability statement | J-01 | `org-101` | Released for source-built pre-alpha frontend only |
| ORG-02 — Orange 2026 lexical behavior | — | `org-102` | Released |
| ORG-03 — complete current grammar and conformance | — | `org-103` | Released |
| ORG-04 — standard to admitted specification | J-02 | `org-202`, `pro-100` | Blocked on the S3 remainder |
| ORG-05 — implementation, proof, claim classification | J-03 | `org-301`, `pro-100` | Blocked on S4 |
| ORG-06 — native artifact and preservation chain | J-04 | `org-401`, `pro-100` | Blocked on S5/S6 |
| ORG-07 — generated C/Rust integration | J-05 | `org-402`, `pro-100` | Blocked on S6 |
| ORG-08 — hostile-input offline replay | J-06 | `org-403`, `pro-100` | Blocked on S7/S8 |
| ORG-09 — update, migration, deprecation, withdrawal | J-07 | `org-404`, `pro-100` | Blocked on S8 |
| ORG-10 — vulnerability and invalidated-claim response | J-08 | `org-404`, `pro-100` | Blocked on S8 |

J-01 is only introduced by today’s source-build exercise. The authoritative
journey requires release and support behavior that does not exist, so it is not
professionally satisfied.

## Role exits

| Competency | Specialization | Capstone | Status |
| --- | --- | --- | --- |
| ROLE-01 | `pro-201` cryptographic implementation | `cap-201` | Blocked |
| ROLE-02 | `pro-202` verification engineering | `cap-202` | Blocked |
| ROLE-03 | `pro-203` cryptography and standards | `cap-203` | Blocked |
| ROLE-04 | `pro-204` integration and maintenance | `cap-204` | Blocked |
| ROLE-05 | `pro-205` audit and downstream assurance | `cap-205` | Blocked |

## Journey coverage

| Journey | Foundation or introduction | Professional assessment surface |
| --- | --- | --- |
| J-01 | `org-101` | `pro-100`, `cap-204` |
| J-02 | `cry-104`, `org-202` | `pro-100`, `cap-203` |
| J-03 | `org-202`, `org-301`, `org-302` | `pro-100`, `cap-201`, `cap-202`, `cap-203` |
| J-04 | `org-401` | `pro-100`, `cap-201`, `cap-205` |
| J-05 | `org-402` | `pro-100`, `cap-204`, `cap-205` |
| J-06 | `ass-103`, `org-403` | `pro-100`, `cap-202`, `cap-204`, `cap-205` |
| J-07 | `ass-104`, `org-404` | `pro-100`, `cap-203`, `cap-204`, `cap-205` |
| J-08 | `ass-104`, `org-404` | all role-relevant capstones |

This is structural coverage, not a claim that the journeys are executable. The
released S3a exercise introduces no end-to-end journey. At the current Orange
revision, all eight authoritative journeys remain proposed and zero are
complete end to end.
