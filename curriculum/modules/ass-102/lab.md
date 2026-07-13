# Lab: Portcullis import adversary

## Goal

Build and challenge a bounded adversarial suite for **Portcullis**, a fictional
offline museum-record import decision. The decision combines a record parser,
quota arithmetic, a count certificate, an exact role policy, and artifact
identity. Preserve a canonical corpus, kill deliberate implementation mutants,
minimize their counterexamples, and make a claim no broader than the finite
evidence.

Portcullis is distinct from the worked example. Do not reuse its commands,
case bytes, target functions, expected outcomes, or leading-zero mutant.

## Setup

From the repository root:

~~~sh
mkdir -p /tmp/ass-102-portcullis
cp curriculum/modules/ass-102/examples/adversary_model.py /tmp/ass-102-portcullis/
cd /tmp/ass-102-portcullis
export PYTHONDONTWRITEBYTECODE=1
export PYTHONHASHSEED=0
python3 -B adversary_model.py
~~~

The last command exits 0 with no stdout or stderr. Record Python's version, the
copied file's absolute path, size, and SHA-256. Create only
<code>portcullis.py</code>, <code>test_portcullis.py</code>, captured evidence,
and <code>portcullis-report.md</code> in this temporary directory. Use Python
3.11+ standard library only and no network access.

Use this finite profile:

- an import request is ASCII and at most 128 bytes;
- collection ID is canonical uppercase <code>C</code> plus four decimal digits;
- declared record count is 0 through 40 with no leading zero except zero;
- quota arithmetic admits current and requested counts from 0 through 40 and
  allows a total no greater than 40;
- a count certificate is the exact ASCII tuple
  <code>collection|declared-count|observed-count</code> and is valid only when
  both counts match for the same collection;
- only exact role <code>curator</code> may perform <code>import</code>;
- artifact identity is full lowercase SHA-256 of the exact manifest bytes; and
- the final decision allows only when every component accepts and the manifest
  identity is bound to the same request.

## Tasks

1. Write at least six falsifiable threat hypotheses, including all five subject
   kinds and one integration hypothesis. Each names the subject/profile,
   divergence, oracle basis, searched set, exclusions, and failure observation.
   Map every case to one or more hypotheses. **ASS-102-01**
2. Build 20 to 28 canonically sorted cases: at least six structured-valid,
   eight malformed, all relevant 0/1/39/40/41 endpoints, and five derived
   mutations. Record origin and parent/operator lineage. Include truncation,
   duplicate field, non-ASCII, case change, count disagreement, and changed
   manifest under an old identity. **ASS-102-01**
3. Implement a table-driven oracle and a separately structured target. Do not
   derive expected values by calling the target or copy the same parser into
   both. Audit shared Python, integer, ASCII, JSON, and SHA-256 dependencies.
   Inject an oracle error into a copy of one expected record and demonstrate
   that a relation, frozen secondary table, or exhaustive finite subdomain
   exposes it. **ASS-102-02**
4. State and test at least eight properties. Include total structured outcomes,
   deny by default, exact certificate binding, quota monotonicity in scope,
   artifact substitution rejection, and integration fail-closed behavior.
   State each generated domain and precondition. **ASS-102-02**
5. Define at least six metamorphic relations with explicit preconditions:
   quota operand commutation, count increase at the limit, role-case change,
   certificate collection substitution, manifest-byte substitution, and a
   structured request transformation of your choice. Check each relation on
   the oracle before using it against the target. **ASS-102-02**
6. Implement five single-change target mutants, one per subject kind: for
   example accept a five-digit collection, wrap quota at 41, ignore the
   certificate collection, case-fold the role, and compare only a digest
   prefix. Your actual mutations must be Portcullis-specific and recorded.
   Require the suite to kill every non-equivalent mutant with the first stable
   differential, property, or metamorphic finding. **ASS-102-03**
7. Minimize at least three killed-mutant counterexamples under their original
   predicates. Record original and minimized hex, evaluation count and budget,
   and whether one-byte-deletion minimality completed. Re-run every minimized
   input against the restored target. **ASS-102-03**
8. Compute the canonical corpus identity twice and assert equality. Change only
   one case byte and assert inequality. Independently reconstruct the canonical
   JSON bytes instead of calling <code>corpus_identity</code>, and assert that
   their SHA-256 matches. Explain why this is identity, not authorship,
   completeness, correctness, or freshness. **ASS-102-01**, **ASS-102-04**
9. Isolate all exact endpoints and smallest overflows: 128/129 input bytes, 8/9
   threats, 32/33 cases, 16/17 relations, 8/9 case references, 240/241 text
   characters, 64 admitted run evaluations, and a minimizer budget request of
   128/129. Assert the exact diagnostic intended for each boundary. Show
   <code>32 + 2 * 16 = 64</code> and explain why 65 is not an admitted endpoint.
   **ASS-102-04**
10. Preserve five deliberate-failure/restored-pass pairs covering parser,
    arithmetic, certificate, policy, and artifact mutants. For each record the
    exact command, corpus and target identity, stdout, stderr, and immediate
    status before restoration. Do not overwrite failures. **ASS-102-03**,
    **ASS-102-04**
11. Write <code>portcullis-report.md</code> with threat table, generation
    strategy, corpus identity, oracle construction and shared TCB, properties,
    relations, mutant table, minima, exact bounds, failures/restorations,
    exercised-hypothesis count, uncovered space, and residual risk. Explicitly
    exclude exhaustive coverage, proof, external Portcullis operation, and all
    Orange syntax, semantics, compiler, runtime, library, safety, security,
    conformance, and release claims. **ASS-102-01** through **ASS-102-04**

## Verification

First verify the supplied model from the repository root:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B curriculum/modules/ass-102/checks/lab_smoke.py
~~~

Expected stdout and immediate status:

~~~text
ass-102 lab smoke: PASS
status: 0
~~~

Then run the independent lab checker from the temporary directory:

~~~sh
python3 -B test_portcullis.py
~~~

It must write exactly <code>portcullis lab: PASS</code> plus a newline to stdout,
nothing to stderr, and exit 0. Run it again by absolute path with a different
fresh working directory. Repeat with <code>PYTHONHASHSEED=29</code>. The restored
report, canonical bytes, corpus identity, minimized cases, sorted findings, and
stdout must be byte-identical. Hash the checker, target, corpus export, report,
and captured output.

## Reflection

In 300 to 450 words, state the strongest Portcullis claim the finite campaign
supports and the first event that withdraws it. Explain one way the oracle and
target could share a defect, one threat not represented by the corpus, why
killing all five mutants does not establish adequacy against all defects, why a
one-deletion-minimal case may not be globally shortest, and what additional
evidence would be required before assessing a real import service.
