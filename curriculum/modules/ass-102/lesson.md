# Adversarial validation

Ordinary examples ask whether a system works on inputs its author expected.
Adversarial validation starts from a falsifiable failure hypothesis and searches
for the smallest recorded input that contradicts the expected behavior. A good
campaign can find a defect. A campaign that finds none establishes only that
its declared oracles, generators, properties, relations, mutants, corpus, and
budgets did not expose one.

This module uses **Gauntlet**, an independent, finite Python teaching model. It
is not Orange syntax or tooling. Its results establish no property of the
Orange language, compiler, runtime, libraries, project process, or releases.

## Learning objectives

- **ASS-102-01:** Turn scoped threat hypotheses into bounded structured,
  malformed, endpoint, and mutated cases with explicit lineage and a canonical
  corpus identity.
- **ASS-102-02:** Apply independent oracles, properties, metamorphic relations,
  and differential comparisons across parsers, implementations,
  proof/certificate checkers, policies, and artifacts.
- **ASS-102-03:** Use implementation mutation and deterministic counterexample
  minimization to challenge a suite, preserve failures and restored passes, and
  distinguish a killed mutant from demonstrated correctness.
- **ASS-102-04:** Report exact resource endpoints, exercised hypotheses,
  uncovered space, oracle and coverage limits, trust dependencies, and only the
  assurance claim supported by the finite evidence.

## Prerequisites

Pass <code>ass-101</code> and <code>prg-103</code>. You should be able to scope a
claim, preserve immutable failure evidence, write deterministic tests, separate
a test double from a real dependency, and interpret a failing assertion without
silently replacing it.

The executable material requires Python 3.11 or newer, uses only the standard
library, performs no network access, and writes no repository files. Its smoke
check launches only bounded subprocesses with bytecode generation disabled.

## Lesson

### Begin with a threat hypothesis

"Fuzz the parser" names an activity, not an obligation. A useful threat
hypothesis names a subject, a possible divergence, the authority that decides
the expected result, and the input space being searched:

~~~text
subject:       decimal parser profile v1
hypothesis:    a noncanonical leading-zero numeral may be accepted
oracle basis:  grammar decimal := "0" | nonzero digit*
searched set:  recorded inputs of at most 128 bytes in corpus identity X
failure:       target and oracle return unequal structured outcomes
exclusions:    Unicode normalization, concurrency, allocation failure, Orange
~~~

The hypothesis guides generation and gives a failure meaning. Without it,
adding more inputs can increase a count while leaving the important risk
untouched. Gauntlet records five hypotheses, one for each teaching subject:

| Subject | Example adversarial question | Narrow oracle |
| --- | --- | --- |
| parser | Does malformed or noncanonical syntax reach an accepting state? | A versioned grammar and bounded semantic rules |
| implementation | Do endpoints, alternate forms, or arithmetic behavior diverge? | A separately implemented mathematical model |
| certificate checker | Does a malformed or false witness pass a checker? | The exact proposition the certificate is meant to witness |
| policy | Can case, whitespace, defaults, or ordering turn deny into allow? | A complete finite decision table or policy semantics |
| artifact binding | Can changed content be accepted under the old identity? | An exact byte-to-identity relation and trusted expected identity |

A proof checker deserves adversarial testing too. A proof can be valid while a
parser, theorem encoding, certificate importer, or policy wrapper binds it to
the wrong statement. Testing a checker does not prove its soundness; it can
expose counterexamples to an implementation or integration claim.

### Generate valid structure and deliberate malformation

Pure random bytes are useful for some parsers but rarely reach deep states in a
structured system. Use complementary sources:

1. **Seeds** are small representative records whose provenance is known.
2. **Structured generation** builds values from the declared grammar, type,
   policy, or certificate model, including exact endpoints.
3. **Malformed generation** violates one named obligation: truncate one field,
   duplicate a key, change a tag, introduce a noncanonical number, or substitute
   a digest.
4. **Mutation** derives a new case from a recorded parent with one named
   operator. Its lineage must survive corpus export.
5. **Regression cases** preserve every discovered counterexample even after the
   defect is corrected.

Do not let one cap hide another. To test an input-length endpoint, construct a
single case at exactly 128 bytes without first exceeding the case or reference
cap. To test 32 cases, keep each case small and use one threat reference. State
whether a generator is exhaustive over a finite set, pseudo-random under a
recorded seed, coverage-guided, or merely a hand-selected corpus.

Gauntlet cases store immutable <code>bytes</code>, a subject kind, origin,
sorted threat identifiers, and optional parent/operator lineage. It rejects a
mutable <code>bytearray</code>. That prevents later mutation of a recorded case;
it does not make the source, generator, or expected result trustworthy.

### Give the corpus exact byte identity

"The same tests passed" is not reproducible unless "same" is checkable.
Gauntlet serializes a corpus with:

~~~text
schema: ass-102-corpus-v1
UTF-8 JSON; sorted object keys; no insignificant whitespace; ASCII escaping
threats, cases, and relations sorted by unique identifier
case bytes encoded as lowercase hexadecimal
origin, parent, operator, subject kind, and threat references included
SHA-256 over the exact serialization
~~~

The identity has form <code>sha256:&lt;64 lowercase hex digits&gt;</code>. Changing
one case byte or one hypothesis changes the identity. The digest does not prove
authorship, correctness, completeness, freshness, benign intent, or that the
expected digest arrived through a trustworthy channel. Those remain separate
claims and dependencies.

### Properties state what must hold for many cases

An example asserts a result for one input. A property quantifies over a declared
generated set. Useful properties include:

- totality at the test boundary: every admitted input returns a structured
  outcome rather than escaping with an exception;
- parser/pretty-printer round trips over the canonical generated subset;
- deny-by-default for every role/action pair absent from a finite allow table;
- accepted certificates imply the exact checked relation; and
- changing artifact bytes while holding an expected digest fixed rejects.

The generator is part of the property. "For all generated cases" may cover only
32 values. It is not "for all possible inputs." If a property restates the same
buggy implementation, both can agree and still be wrong.

### Metamorphic relations compare related executions

Sometimes the exact answer is difficult to compute, but a relation between
answers is known. A **metamorphic relation** names a source transformation and
the expected relationship between source and follow-up outcomes. Gauntlet uses:

- commuted bounded addition must return the same result;
- changed artifact content under the old digest must return a different result;
- adding a leading zero to a nonzero canonical numeral must make the follow-up
  reject while the source is accepted; and
- changing a role's case must not preserve an exact-case allow result.

The relation itself is an oracle and can be false, incomplete, or inapplicable.
Check its preconditions. Gauntlet applies each relation to the oracle first and
reports <code>oracle-relation-violation</code> if the declared oracle does not
satisfy it. Agreement with several relations still is not a complete expected
result for every input.

### Differential testing needs meaningful independence

Differential testing sends the same input to two implementations and compares
normalized outcomes. A difference is evidence that at least one side, the
normalizer, or the stated equivalence is wrong. Agreement is weaker: both sides
can share the same defect.

Oracle independence is architectural, not cosmetic. Two wrapper functions that
call the same parser are not independent. Better oracle sources include:

- a small executable specification built from a different representation;
- a frozen table reviewed against a normative specification;
- exhaustive enumeration of a genuinely finite domain;
- a mature implementation with separately assessed provenance; or
- multiple diverse oracles whose disagreements remain visible.

Record shared dependencies such as the Python integer model or SHA-256
implementation in the assurance TCB. Gauntlet rejects the exact same callable
object as oracle and target, but cannot prove semantic independence. Its worked
oracle and target have separate control flow yet share Python and
<code>hashlib</code>; the artifact comparison is therefore not independent of a
defect in that shared primitive.

Outcomes are structured as <code>(accepted, code, value)</code>. Comparing only
process status, a Boolean, or text with unstable addresses can hide meaningful
divergence. Conversely, comparing irrelevant formatting can manufacture false
differences. Define normalization before the campaign.

### Mutation testing challenges the tests

Input mutation changes a test case. **Implementation mutation** changes the
target to simulate a defect. A suite **kills** a mutant when it produces the
specified observable failure. A surviving mutant may reveal a missing test, a
weak oracle, an unreachable change, or an equivalent mutant whose observable
behavior is unchanged in scope.

Gauntlet's worked mutant accepts one-to-three decimal digits, including leading
zeros. The corpus kills it twice: a differential mismatch at
<code>p-leading-zero</code> and a violation of <code>canonical-decimal</code>.
This shows that the finite suite detects that injected defect. It does not show
that the parser has no other defects, and a 100% score over one mutant is not a
general adequacy measure.

A professional mutation report preserves:

~~~text
exact target artifact and mutation operator
build/configuration identity
killed, survived, invalid, timed-out, and equivalent classifications
first stable counterexample and diagnostic
total mutants in the declared set and exclusions
restored unmutated pass
~~~

### Minimize without erasing the failure

Small counterexamples are easier to review and retain. A minimizer must preserve
the same failure predicate, not merely any failure. Gauntlet greedily tries each
single-byte deletion and restarts after a successful deletion. It returns:

- the remaining bytes;
- the number of predicate evaluations, including the required initial
  counterexample check; and
- whether every one-byte deletion was checked without exhausting the budget.

If <code>one_minimal</code> is true, no single byte can be deleted while
preserving the predicate. That is not a globally shortest input: replacing
bytes or deleting chunks could find a smaller case. If the 128-evaluation
budget ends first, report the candidate but do not call it one-minimal.

Minimization can accidentally change the defect class. The predicate in the
worked example remains exactly "oracle outcome differs from leading-zero-mutant
outcome." It retains <code>50 3a 30 37</code>, ASCII <code>P:07</code>.

### Corpus coverage is not semantic coverage

Gauntlet reports **exercised threat hypotheses**: the union of threat IDs linked
by its cases. Five of five means each recorded hypothesis had at least one
case. It says nothing about:

- branch, path, state, value, grammar-production, policy-rule, or requirements
  coverage;
- inputs not generated under the fixed caps;
- concurrency, timing, memory pressure, undefined behavior, or environmental
  interactions;
- defects shared by target and oracle;
- soundness of a proof kernel, certificate scheme, or policy model; or
- external deployment artifacts not bound to the recorded corpus.

Instrumentation coverage is useful search feedback, not a correctness metric.
A covered branch may have an unchecked result, and an uncovered branch may be
unreachable. State the instrumentation version and artifact identity whenever
reporting it.

### Bounds and exact diagnostics make replay finite

Gauntlet checks each cap before retaining or traversing the first excessive
item:

| Resource | Counted unit | Accepted cap | Smallest rejected value |
| --- | --- | ---: | ---: |
| input | bytes in one case | 128 | 129 |
| threats | records in one corpus | 8 | 9 |
| cases | records in one corpus | 32 | 33 |
| relations | records in one corpus | 16 | 17 |
| references | threat IDs on one case | 8 | 9 |
| text | Python characters in one field | 240 | 241 |
| run work | one paired oracle-target case comparison or one cached relation-side inspection | 64 | not representable under the static caps |
| minimization | predicate evaluations | 128 | a requested budget of 129 is rejected |
| findings | distinct sorted findings | 94 | 95 is not representable under the static caps |

The run-work arithmetic is <code>cases + 2 * relations</code>. Its maximum is
<code>32 + 2 * 16 = 64</code>, so no admitted corpus can request 65. Each case
unit invokes both oracle and target; relation units inspect cached outcomes and
do not invoke them again. The model
rejects a corpus whose computed work exceeds 64 after collection validation;
the static caps make that guard redundant by design. Endpoint tests must not
claim an unreachable 65-unit corpus. The 94-finding maximum is feasible: 30
cases contribute paired oracle/target exceptions, two valid cases contribute
two differential mismatches, and 16 relations contribute paired oracle/target
relation violations, for <code>30*2 + 2 + 16*2 = 94</code>. More exceptions
leave too few valid outcomes for relation findings; more valid cases replace
two exception findings with at most one differential finding.

Case, relation, threat, and reference collections are immutable tuples, sorted
and unique where canonical order matters. A target exception becomes exact
finding <code>target-exception</code>; a non-<code>Outcome</code> return becomes
<code>target-outcome-type</code>. Neither becomes a pass. Findings are sorted.
The model claims neither exact heap bytes, real-time completion, constant-time
behavior, isolation from a hostile Python runtime, nor safety for arbitrary
external targets.

Ignoring bounded payload costs, a suite run is O(C + R), where C is case count
and R is relation count; canonical identity is linear in the bounded serialized
corpus plus SHA-256 cost. Greedy one-byte minimization can be O(B squared)
predicate input work for B bytes because deletion restarts, but both B and
predicate evaluations are capped here.

## Worked example

Run the five-subject corpus from the repository root:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B curriculum/modules/ass-102/examples/adversary_worked.py pass
~~~

It exits 0, writes nothing to stderr, and ends with:

~~~text
cases: 18
threats: 5/5
result: PASS
limitation: The report binds corpus bytes, not oracle or target callable identity. Finite model observations only; not exhaustive coverage, proof, or an Orange capability, safety, security, conformance, or release claim.
~~~

Now preserve a deliberate implementation failure:

~~~sh
python3 -B curriculum/modules/ass-102/examples/adversary_worked.py mutant
# immediate status 4
~~~

Stdout contains exactly these two findings:

~~~text
finding: differential-mismatch at p-leading-zero: target differs from oracle
finding: metamorphic-violation at canonical-decimal: followup-rejects
~~~

Minimize under the same predicate:

~~~sh
python3 -B curriculum/modules/ass-102/examples/adversary_worked.py minimize
# immediate status 4; stdout includes:
# minimized-hex: 503a3037
# minimizer-evaluations: 5
# one-minimal: true
~~~

Finally re-run <code>pass</code> and preserve its immediate status 0. The smoke
check repeats the passing report with <code>PYTHONHASHSEED=0</code> and 29 and
requires byte-identical stdout.

## Check your understanding

1. Why is "five of five threats exercised" not branch, semantic, or exhaustive
   coverage? **ASS-102-04**
2. Give one structured and one malformed generator for a certificate checker.
   What lineage must each generated case retain? **ASS-102-01**
3. If two implementations agree because both use the same defective parser,
   what differential-testing assumption failed? **ASS-102-02**
4. Define a metamorphic relation for a deny-by-default policy and state its
   preconditions. **ASS-102-02**
5. A mutant survives. Give four explanations other than "the system is
   correct." **ASS-102-03**
6. What does one-deletion-minimal exclude, and what can it still miss?
   **ASS-102-03**
7. Show why 65 run evaluations cannot be admitted under the 32-case and
   16-relation caps. **ASS-102-04**
8. Which shared dependencies undermine the independence of the worked artifact
   oracle and target? **ASS-102-02**, **ASS-102-04**

## Next step

Complete the lab and independent assessment, earning at least 80/100 and every
critical criterion. Preserve the first failing artifact before fixing it. Then
complete <code>ass-103</code> and combine both modules in <code>ass-104</code>,
where adversarial evidence must survive reproducible release and response
workflows.

## Sources

- Koen Claessen and John Hughes, [QuickCheck: a lightweight tool for random
  testing of Haskell programs](https://doi.org/10.1145/351240.351266), ICFP
  2000. Read for generated properties and counterexample reduction; Gauntlet is
  not a QuickCheck implementation.
- Earl T. Barr et al., [The Oracle Problem in Software Testing: A
  Survey](https://discovery.ucl.ac.uk/id/eprint/1471263/), IEEE TSE 2015. Read
  for oracle strategies and their limits.
- Zhi Quan Zhou et al., [How effectively does metamorphic testing alleviate the
  oracle problem?](https://vuir.vu.edu.au/33046/1/TSEmt.pdf), IEEE TSE 2014.
  Read for empirical limits as well as benefits of metamorphic testing.
- LLVM Project, [libFuzzer documentation](https://llvm.org/docs/LibFuzzer.html).
  Read for corpus seeding, coverage-guided mutation, replay, and minimization;
  Gauntlet does not invoke libFuzzer.
- OWASP Foundation, [Web Security Testing Guide: Fuzzing](https://owasp.org/www-project-web-security-testing-guide/latest/6-Appendix/C-Fuzzing).
  Read as broader adversarial-testing context, not as evidence about this
  offline model.
