# Learner pathways

## One entry, several exits

Every learner starts at `ori-001`. Experienced learners may use assessments as
placement tests, but the graph never assumes prior knowledge that is not
assessed.

The planned shared path is:

| Order | Stage | Focus | Current availability |
| ---: | --- | --- | --- |
| 0 | Orientation | Learning workflow, placement, claim discipline | Released |
| 1 | Computing practice | Terminal, files, Git, tests, debugging, CI | Released |
| 2 | Programming | Program structure, data, types, errors, algorithms, C, Rust | Released |
| 3 | Mathematical foundations | Logic, proof, number theory, algebra, probability | Released |
| 4 | Cryptography | Security notions, primitives, constructions, standards, vectors | Released |
| 5 | Systems | Arithmetic, memory, ABI, targets, SIMD, leakage | Released |
| 6 | Languages and formal methods | Syntax, semantics, compilers, contracts, proofs, games | Released |
| 7 | Assurance | Claims, TCBs, testing, reproducibility, lifecycle response | Released |
| 8 | Orange Today | Implemented 2026 lexer, parser, S3a typed literals, CLI, diagnostics, conformance | Released |
| 9 | Orange professional core | Remaining semantics through packages, replay, and operations | Blocked on the S3 remainder and S4-S8 |
| 10 | Role specialization | One deep professional pathway and capstone | Blocked on the S3 remainder and S4-S8 |

The catalog is the exact module order. This page explains the intent rather
than duplicating every prerequisite edge.

First programming and executable-mathematics labs use Python's standard
library. Systems modules then teach the C and Rust needed for memory, compiler,
artifact, and FFI work. Host-language success is never presented as Orange
success.

## Why Orange Today appears after foundations

The released Orange modules may be sampled early, immediately after the basic
terminal module. They deliberately teach source text, lexing, parsing, the
narrow closed-literal S3a semantic slice, diagnostics, and honest non-claims.
Completing them is not equivalent to learning general programming or
cryptographic engineering.

The full professional track returns to Orange only after the learner has the
mathematics, systems, cryptography, language, formal-methods, and assurance
foundations required to understand why Orange is designed as it is.

## Five role specializations

All roles share the professional core and then emphasize different evidence.

### Cryptographic implementer (`P-01`)

Design and implement leakage-aware, target-conscious cryptographic code; connect
it to specifications; measure it; and defend its safety, refinement, and
artifact claims. The capstone primarily exercises J-03 and J-04, with J-05 and
J-08 as supporting workflows.

### Verification engineer (`P-02`)

Create invariants, refinements, proof terms or certificates, replay evidence,
expose assumptions, and analyze the trusted base. The capstone primarily
exercises J-03 and J-06.

### Cryptographer or standards author (`P-03`)

Translate exact standards text and errata into readable executable
specifications, parameterize constructions, define security games, and generate
canonical vectors. The capstone primarily exercises J-02, supported by J-03,
J-07, and J-08.

### Library maintainer or integrator (`P-04`)

Ship misuse-resistant C/Rust interfaces, validate target dispatch and failure
behavior, maintain compatibility, and execute updates or withdrawals. The
capstone primarily exercises J-05 and J-07, with J-01 and J-08.

### Auditor or downstream consumer (`P-05`)

Treat bundles as hostile inputs, verify identity and trust closure, replay
evidence offline, inspect artifacts, and report exactly which claims survive.
The capstone primarily exercises J-06 and J-08.

## Portfolio evidence

Before a specialization capstone, every learner produces:

1. a foundations project demonstrating reproducible programming and testing;
2. a standards-grounded cryptography analysis;
3. a formal assurance artifact with explicit assumptions and failure cases;
4. a current-Orange conformance portfolio containing accepted and rejected
   Orange 2026 source; and
5. the shared future Orange professional project once S3 is completed and
   S4-S8 are implemented.

No future portfolio item is currently represented as available.
