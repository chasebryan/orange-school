# Current status

Snapshot: 2026-07-12

## School

Curriculum version `0.9.0-dev` provides:

- one machine-readable prerequisite and competency graph;
- the full planned beginner-to-professional pathway;
- five role specialization definitions and capstones;
- a released computing-practice stage covering terminal work, Git history,
  testing, debugging, automation, and CI evidence;
- released Python foundations for program structure, bounded algorithms, type
  contracts, explicit failures, tests, and systematic debugging;
- a released C17/Rust bridge for memory, ownership, bounds, explicit errors,
  and a narrow audited FFI boundary;
- released logic, proof, number theory, algebra, prime-field arithmetic,
  probability, exact enumeration, and evidence-scope foundations;
- released cryptographic goals and attacker models; symmetric and public-key
  primitive/construction boundaries; nonce, key, PKI, and failure analysis; and
  standards, errata, provenance, and vector evidence;
- released representation and bounded arithmetic; C/Rust memory ownership and
  FFI; object, link, ABI, target, SIMD-dispatch, leakage-model, artifact, and
  empirical side-channel evidence foundations;
- released bounded lexing and parsing; name, type, effect, and operational
  semantics; typed IR lowering; artifact validation; and scoped preservation
  evidence foundations;
- released specifications, contracts, invariants, refinement, proof kernels,
  explicit trust, checked automation certificates, probabilistic games,
  reductions, and concrete-bound foundations;
- released claim/evidence/TCB closure, adversarial validation, canonical
  hostile-bundle replay, release lifecycle, rollback prevention, withdrawal,
  and vulnerability-response foundations;
- released current-Orange modules for the implemented frontend and accepted
  S3a typed-literal/reference-evaluation surface;
- a strict module contract and assessment policy;
- structural, content, and example validators; and
- explicit blockers for unimplemented Orange capabilities.

The catalog contains 54 modules: 36 released, 0 planned, and 18 blocked. 31
host-language smoke checks and 11 pinned Orange examples pass. Every general
foundation module is learner-ready. The professional Orange track remains
unavailable because its remaining modules depend on the unfinished S3 surface
and absent S4-S8 capabilities.

## Orange dependency

At pinned merged revision `ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`,
Orange stages S1 and S2 are complete and accepted pre-alpha slice S3a is
implemented. The current teachable language surface is:

- exact source identities and UTF-8 byte spans;
- deterministic Orange 2026 lexing;
- one bounded grammar containing an edition declaration, one module, empty
  `spec` or `impl` declarations, and closed typed `spec` literals;
- structured stable diagnostics;
- exact contextual `Int` and `Word[8]` literal semantics, same-kind declaration
  uniqueness, a source-ordered noncanonical Typed Reference Core, and
  deterministic `orangec eval`; and
- `orangec lex`, `orangec check`, and `orangec eval`.

S3 remains active and incomplete. Parameters, operators, calls, bindings,
control flow, dynamic failure, typed implementations, contracts, effects,
specification/implementation refinement, and canonical Core identity remain
absent. S4 through S8 are pending; proof and claim checking, native artifacts,
FFI, admitted cryptography packages, evidence bundles, releases, updates, and
incident workflows therefore remain blocked curriculum surfaces.

## Honest completion statement

The curriculum architecture and all prerequisite foundations are established,
and a learner can begin and master today’s Orange frontend and narrow S3a
surface. The repository goal remains incomplete: no learner can yet complete
the professional track because Orange itself does not expose the required S3
remainder or S4-S8 professional workflows.
