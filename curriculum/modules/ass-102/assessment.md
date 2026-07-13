# Assessment: Sentinel admission gauntlet

## Instructions

Build **Sentinel**, an independent bounded adversarial-validation harness for a
fictional offline package-admission decision. Do not import, copy, edit, or
mechanically translate Gauntlet, the worked targets, or the Portcullis lab.
Implement new data types, validation paths, corpus schema, canonical encoder,
oracle strategies, generators, relations, comparison logic, mutation runner,
minimizer, and diagnostic vocabulary with Python 3.11 standard-library code.

Work in a fresh temporary directory without network access. Submit source,
tests, corpus bytes and identity, target and mutant identities, generated
reports, hashes, exact commands, stdout, stderr, immediate statuses, and
preserved counterexamples. A final passing run must not erase prior failures.

Sentinel's exact subject is one fictional package profile:

- canonical manifest parser for package name, unsigned version, artifact
  length, full SHA-256, signer key ID, and channel;
- mathematical version and length comparisons over declared finite ranges;
- certificate checker binding package, version, digest, signer, and channel;
- policy allowing exact signer/channel/package combinations and denying every
  absent combination; and
- artifact check over the exact admitted bytes, followed by an integration
  decision that binds all component results to the same request.

This is an assurance assessment, not a package-manager implementation. Do not
execute admitted bytes, use real credentials, or claim external or Orange
behavior.

## Knowledge check

Answer before implementing:

1. Rewrite "attack the package validator" as three falsifiable hypotheses with
   exact subjects, oracle bases, searched sets, and failure observations.
   **ASS-102-01**
2. Contrast seed, structured, malformed, mutation-derived, and regression cases.
   What lineage and identity fields make each replayable? **ASS-102-01**
3. Define example, property, metamorphic, and differential oracles. Give one
   Sentinel use and one failure mode for each. **ASS-102-02**
4. Two separately named functions share one parsing helper. Why are they not
   independent parser oracles? How can a third oracle reduce, but not eliminate,
   common-mode risk? **ASS-102-02**
5. Distinguish input mutation from target mutation. What does a killed,
   surviving, invalid, timed-out, or equivalent mutant establish?
   **ASS-102-03**
6. Distinguish one-byte-deletion minimal, locally minimal under several
   operators, and globally shortest counterexamples. **ASS-102-03**
7. Give four meanings of coverage and one non-implication for each. Why is a
   count of exercised hypotheses not a correctness percentage? **ASS-102-04**
8. Explain how corpus identity, target identity, oracle identity, generator
   seed/configuration, and expected-identity distribution enter a reproducible
   claim. **ASS-102-01**, **ASS-102-04**
9. Give at least eight Orange or external-system properties this Python model
   cannot establish. **ASS-102-04**

## Independent task

1. Define immutable exact-type records for hypotheses, cases, lineage,
   relations, observations, findings, mutation results, minimized
   counterexamples, and reports. Reject mutable collections, host Booleans in
   integer fields, duplicate or noncanonical identifiers, unknown references,
   self-parenting, parent cycles, malformed digests, and unsupported enum values
   with stable exact diagnostics. **ASS-102-01**
2. Define at least seven threat hypotheses spanning parser, implementation,
   certificate checker, policy, artifact binding, oracle failure, and integrated
   package admission. Each record includes an exact subject/profile, possible
   divergence, oracle authority, generated domain, exclusions, and a falsifying
   observation. Every case maps to at least one hypothesis; every hypothesis has
   at least two cases. **ASS-102-01**
3. Use independent caps of 96 bytes per input, 7 hypotheses, 28 cases, 12
   metamorphic relations, 6 references per case, 200 characters per text field,
   52 run evaluations, 96 minimizer evaluations, and 78 findings. Check caps
   before retaining or traversing the first excessive item. Isolate exact
   endpoints and smallest overflows: 96/97, 7/8, 28/29, 12/13, 6/7, 200/201,
   and minimizer requests 96/97. Demonstrate
   <code>28 + 2 * 12 = 52</code>; do not invent an unreachable 53-evaluation
   admitted corpus. **ASS-102-04**
4. Define canonical schema <code>sentinel-corpus-v1</code> using UTF-8 JSON,
   sorted object keys, no insignificant whitespace, ASCII escaping, ordered
   unique arrays, lowercase input hex, and all hypothesis, lineage, relation,
   generator-profile, and expected-result fields that affect interpretation.
   Compute full SHA-256. Independently construct canonical bytes for at least 16
   records and compare them to the encoder. Change each semantic field in turn
   and require a different identity. **ASS-102-01**, **ASS-102-04**
5. Build 24 to 28 cases, including valid structured records, every finite
   endpoint, deliberate grammar violations, duplicate and reordered fields,
   non-ASCII, length mismatch, version rollback, certificate subject/digest/key
   substitution, unknown and case-changed channel, default-policy probes, and
   artifact mutation under the old digest. Include at least eight
   mutation-derived cases with parent/operator lineage. **ASS-102-01**
6. Implement three diverse oracle strategies: a frozen table reviewed from the
   profile for at least 16 cases; a small separately represented executable
   specification for all admitted cases; and exhaustive enumeration of one
   genuinely finite policy or boundary subdomain. Keep disagreements as
   findings. Audit shared runtime, integer, text, hash, profile, and
   normalization dependencies. Inject one defect into each oracle strategy and
   show the remaining strategy or an applicable relation exposes it.
   **ASS-102-02**
7. State and test at least ten properties with generator domains and
   preconditions. Include total structured outcomes, canonical parse/re-encode,
   deny by default, monotonic version comparison, exact length, exact artifact
   binding, certificate subject binding, component-to-integration identity
   consistency, deterministic replay, and exception fail-closed behavior.
   **ASS-102-02**
8. Define at least eight metamorphic relations. Include field reorder rejection,
   case change, package substitution, version increase and rollback, certificate
   digest substitution, artifact-byte substitution, and equivalent
   reserialization only where the profile permits it. Validate every relation
   against the oracle set before applying it to the target. Preserve oracle
   relation failures separately from target relation failures. **ASS-102-02**
9. Differentially compare normalized structured outcomes from the executable
   specification and an independently structured target for every corpus case.
   Treat target exception, timeout, malformed outcome, and missing observation
   as distinct fail-closed findings. Demonstrate that Boolean-only comparison
   would miss at least one code or bound divergence. **ASS-102-02**
10. Create at least 15 single-change target mutants, at least two in each of the
    five subject categories. Include acceptance of noncanonical grammar,
    version wrap or wrong endpoint, certificate field omission, policy
    case-fold/default allow, digest prefix comparison, and an integration mix-up
    that combines component results from different package requests. Record
    target/mutant identities and classify every mutant. Kill at least 12; no
    surviving or unclassified mutant may weaken deny, certificate binding,
    rollback, artifact identity, or integration identity in the assessed
    profile. **ASS-102-03**
11. For at least five killed mutants spanning all subject categories, minimize
    the first counterexample under the exact original predicate. Use at least
    deletion, numeric shrink, and structured-field removal operators, each with
    a deterministic order and shared 96-evaluation cap. Record original and
    minimized bytes, operator trace, evaluations, completed minimality notion,
    and restored-target result. Do not call a budget-exhausted or locally
    minimal result globally shortest. **ASS-102-03**
12. Preserve six deliberate-failure/restored-pass pairs: parser
    noncanonicality, version boundary, certificate subject binding, policy
    default or case, artifact identity, and cross-request integration. Capture
    exact command, corpus/oracle/target/mutant identities, stdout, stderr, and
    immediate status. A failing command must exit nonzero; restoration must use
    the unmutated target and exit zero. **ASS-102-03**, **ASS-102-04**
13. Add at least 24 adversarial harness-self-tests: mutable input, Boolean where
    integer is required, duplicate ID, noncanonical order, unknown hypothesis,
    unknown parent, parent cycle, unknown relation endpoint, same oracle/target
    object, oracle exception, target exception, wrong outcome type, stale corpus
    identity, every resource overflow, relation-oracle violation, finding cap,
    false initial minimization predicate, and exhausted minimization budget.
    Assert the first exact diagnostic and preserve the triggering value.
    **ASS-102-01** through **ASS-102-04**
14. Produce <code>sentinel-report.md</code> with scoped hypotheses; exact profile;
    corpus/generator identity and lineage; oracle construction, disagreements,
    and TCB; properties and relations; differential results; mutant table and
    score denominator; minimized counterexamples; exact endpoints; preserved
    failures/restorations; and a coverage table distinguishing hypothesis,
    grammar, policy-rule, branch, and state coverage. Unknown or unmeasured
    coverage must say <code>not measured</code>, not zero or complete.
    **ASS-102-01** through **ASS-102-04**
15. End the report with the strongest finite claim, withdrawal conditions,
    uncovered input/environment space, shared-oracle risks, instrumentation
    limits, non-proofs, and residual risks. State that the assessment does not
    prove the Python runtime, SHA-256 implementation, Sentinel profile, or an
    external package manager, and establishes no Orange syntax, semantics,
    compiler, runtime, library, proof, safety, security, conformance, or release
    claim. **ASS-102-04**

## Completion criteria

Use the [rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. The assessor must reproduce the work offline on Python 3.11 or newer
from a fresh temporary directory. The final checker writes exactly
<code>sentinel assessment: PASS</code> plus a newline, writes nothing to stderr,
and exits 0. It must produce byte-identical restored reports, canonical corpus
bytes, identities, sorted findings, mutant classifications, minimized cases,
and stdout under <code>PYTHONHASHSEED=0</code> and 29.

Every exact endpoint, smallest overflow, oracle defect, property, relation,
target mutant, first counterexample, minimization trace, deliberate failure,
restored pass, coverage exclusion, and calibrated non-proof must be observable
from submitted commands and preserved immutable evidence. Generated work that
cannot be bound to the submitted corpus and target identities does not count.
