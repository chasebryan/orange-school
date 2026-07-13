# Claims, evidence, assumptions, and trusted bases

Assurance work does not turn confidence into certainty by adding a green badge.
It records a claim narrowly enough to challenge, connects it to inspectable
evidence, carries every assumption and dependency into the conclusion, and
stops saying "supported" when any required support is absent.

This module uses **Keystone**, an independent finite Python teaching model. It
is not Orange syntax or tooling. Its results establish no property of the
Orange language, compiler, runtime, libraries, project process, or releases.

## Learning objectives

- **ASS-101-01:** Write versioned claim records with an exact subject, scope,
  exclusions, assumptions, and falsifiable language rather than an unbounded
  quality label.
- **ASS-101-02:** Classify test, analysis, formal, inspection, and provenance
  evidence; give it a canonical content identity; and state the narrow
  conclusion and non-proofs of each evidence type.
- **ASS-101-03:** Compute claim-dependency, assumption, evidence, and trusted
  computing base closure while detecting missing references, excessive depth,
  cycles, and invalid composition arguments.
- **ASS-101-04:** Derive deterministic fail-closed claim statuses and produce a
  calibrated, offline-replayable report with exact endpoints, deliberate
  failures, and residual-risk statements.

## Prerequisites

Pass <code>cry-104</code>, <code>frm-101</code>, and <code>cmp-103</code>. You
should be able to reproduce pinned evidence, separate a model from the system it
models, inspect a finite dependency graph, and explain why testing selected
executions differs from proving a universally quantified statement.

The executable material requires Python 3.11 or newer, uses only the standard
library, performs no network access, and writes generated evidence only to a
fresh temporary directory.

## Lesson

### A claim record is a falsifiable sentence, not a mood

"The codec is correct" does not identify a checkable obligation. A useful claim
record names at least:

1. a stable claim identifier;
2. the exact subject: artifact, version, profile, configuration, or revision;
3. one proposition that could be contradicted;
4. a finite scope in which the proposition is asserted;
5. explicit exclusions that a reader might otherwise assume are included;
6. assumptions whose failure withdraws support;
7. direct evidence and dependent claims;
8. the trusted computing base (TCB) on which the argument relies; and
9. a derived status, not an author-selected status.

Compare these two records:

~~~text
weak:   the parser is safe

scoped: artifact 4f... rejects inputs longer than 1024 bytes before allocation
        under profile parser-v3; concurrency, allocator correctness, memory
        safety, and all inputs absent from the recorded suite are excluded
~~~

The second claim can still be wrong, but a reviewer can locate its subject,
challenge its exclusions, identify a counterexample, and decide whether the
evidence actually bears on it. "Versioned" means that changing the relevant
artifact, profile, dependency, configuration, or evidence produces a new
record or withdraws the prior conclusion. A claim must not silently drift to a
different subject.

### Evidence has a type and a narrow reach

Keystone distinguishes five evidence kinds:

- **test:** observations from selected executions; strong for reproducible
  examples and counterexamples, but not general absence of defects;
- **analysis:** results derived from a declared model or algorithm; limited by
  its inputs, abstraction, rules, and implementation;
- **formal:** a proof or exhaustive check in an encoded formal system; limited
  by the theorem statement, encoding, axioms, proof kernel, and model fit;
- **inspection:** a recorded human or mechanical review of declared artifacts
  and sites; limited by reviewer competence, coverage, and artifact identity;
- **provenance:** evidence connecting an artifact to a declared origin and
  process; it does not by itself establish correctness, safety, or security.

An evidence record says who or what produced it, its subject, method, result,
artifact SHA-256, assumptions, TCB entries, and bounded facts. Keystone uses
<code>pass</code>, <code>fail</code>, and <code>inconclusive</code>. "Pass" means
the stated method met its stated expectation. It never means every possible
claim about the subject is true.

A digest gives bytes a stable name. It is not a proof of authorship, benign
intent, semantic equivalence, freshness, or correctness. Keystone computes an
evidence identity from UTF-8 bytes of JSON with:

~~~text
schema = ass-101-evidence-v1
sorted object keys
no insignificant whitespace
ASCII escapes for non-ASCII characters
ordered, already-canonical reference arrays and fact keys
the evidence result included in the payload
~~~

The identity is <code>sha256:&lt;64 lowercase hex digits&gt;</code>. Equal canonical
records get equal identities; changing even <code>pass</code> to
<code>fail</code> changes the identity. The evaluator recomputes the identity
and marks linked claims invalid when it does not match. Content addressing
makes substitution visible only when the expected identity itself is obtained
through a trusted channel.

### Assumptions are support obligations

An assumption record includes a statement, owner, falsifier, and state:
<code>confirmed</code>, <code>unverified</code>, or <code>false</code>. A
professional argument records who must monitor the assumption and what event
would invalidate it. "The manifest is the selected authoritative source" and
"the deployed profile is v3" are different assumptions with different owners
and falsifiers.

Keystone supports a claim only when every declared and inherited assumption is
confirmed. Both false and unverified assumptions withdraw support. This does
not necessarily refute the claim's proposition: it says the recorded argument
no longer supports it. Treating "not yet checked" as true is not conservative.

### Dependency closure carries obligations upward

A system claim may depend on component claims. The **dependency closure** of a
claim is the transitive set reached by following its dependency identifiers.
For each root claim, a reviewer must close four inventories:

~~~text
root claim
  + every transitive dependent claim
  + evidence linked by those claims
  + assumptions used by those claims and evidence
  + TCB entries used by those claims and evidence
~~~

Keystone rejects unknown identifiers, self-dependency, cycles, closure deeper
than eight edges, and a root inventory that omits an inherited assumption or
TCB entry. It sorts reports and findings, so hash-table iteration and host hash
seeds do not change the report.

A cycle such as <code>a -> b -> a</code> is not mutually supporting evidence.
Neither claim has an independently grounded base. A deep graph can also make a
review claim operationally uncheckable; Keystone's depth cap is a teaching
resource limit, not a universal assurance rule.

### The TCB is what must be right for the argument to work

The trusted computing base is not only production runtime code. For an
assurance result it can include:

- the compiler, interpreter, proof kernel, test harness, and analysis tool;
- manifests, expected-output oracles, specifications, and configuration;
- libraries or operating-system facilities used by the check;
- people or procedures when a human judgment is a required step; and
- the channel that binds expected identities to artifacts.

Keystone records a component identifier, role, version, artifact digest, and
review state. <code>reviewed</code> means reviewed for the declared argument,
not perfect. <code>unreviewed</code> or <code>compromised</code> withdraws claim
support. A complete TCB inventory makes dependence visible; it does not prove
the TCB correct.

### Support does not compose automatically

Suppose a framing routine passes all of its tests and a checksum routine passes
all of its tests. Those facts do not establish that the combined protocol
frames the same bytes it checksums, uses the right order, propagates errors, or
handles shared state correctly. Component claims can be dependencies of an
integration claim, but the integration claim still needs direct evidence that
bears on their interaction.

Keystone therefore marks a claim with supported dependencies but no direct
evidence <code>UNSUPPORTED</code>, with exact reason:

~~~text
no direct evidence; dependencies do not compose automatically
~~~

Direct integration evidence also does not prove arbitrary environmental or
emergent behavior. Its method and scope still bound the conclusion.

### Status is derived and fail closed

Keystone derives four statuses in this order:

| Status | Meaning in this model |
| --- | --- |
| <code>INVALID</code> | The record cannot support a conclusion: an identity, reference, cycle, closure depth, or inherited inventory is invalid. |
| <code>REFUTED</code> | Direct evidence linked to the claim reports <code>fail</code>. One in-scope counterexample defeats that claim record. |
| <code>UNSUPPORTED</code> | The structure is usable, but evidence is absent or inconclusive, an assumption is not confirmed, a TCB entry is not reviewed, or a dependency is not supported. |
| <code>SUPPORTED</code> | Every declared direct and transitive support obligation in the bounded record passes. |

<code>SUPPORTED</code> is not a synonym for true, verified system, secure,
release-ready, or proven. It is a statement about the recorded argument. The
overall bundle status uses the most conservative present status:
<code>INVALID</code>, then <code>REFUTED</code>, then <code>UNSUPPORTED</code>,
then <code>SUPPORTED</code>.

### Bounds make the check reproducible

The model accepts at most 32 assumptions, 32 TCB entries, 64 evidence records,
and 32 claims. A reference or fact collection contains at most 16 entries;
text contains at most 300 Python characters; dependency closure has at most
eight edges from a root. Collections are immutable tuples. Reference arrays,
fact keys, and exclusions are sorted and unique. Digests use exactly 64
lowercase hexadecimal characters.

The smoke independently constructs every endpoint and its smallest overflow:
32/33 assumptions, 32/33 TCB entries, 64/65 evidence records, 32/33 claims,
16/17 facts, 16/17 references, 300/301 characters, and closure depth 8/9.
At these fixed caps, canonicalization is bounded. Index construction is linear
in claims, evidence, assumptions, and TCB entries. Closure discovery is cached,
but inventory closure still walks each root's transitive claims, evidence, and
sorted sets; a conservative whole-bundle upper bound is
O(C * (C + D + E + A + T) * log(C + E + A + T)). The implementation does not claim exact memory bytes, constant time,
real-time behavior, or safety against a hostile Python runtime.

## Worked example

The [claim model](examples/claim_model.py) and
[worked bundle](examples/claim_worked.py) describe a fictional bounded packet
codec. Two component claims and one integration claim close over three evidence
records, two assumptions, and two TCB entries.

From the repository root, run:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B curriculum/modules/ass-101/examples/claim_worked.py pass
~~~

The immediate status is 0 and stdout ends with:

~~~text
overall: SUPPORTED
limitation: Bounded record-consistency evidence only; not proof of an external claim and not an Orange capability, conformance, safety, or release claim.
~~~

Now observe three deliberate failures:

~~~sh
python3 -B curriculum/modules/ass-101/examples/claim_worked.py failed-integration
# status 4; stdout contains: claim profile-claim: REFUTED

python3 -B curriculum/modules/ass-101/examples/claim_worked.py missing-integration
# status 3; stdout contains: dependencies do not compose automatically

python3 -B curriculum/modules/ass-101/examples/claim_worked.py unreviewed-runtime
# status 3; stdout contains: a trusted component is not reviewed
~~~

Each supported component remains visible in the missing-integration report,
but the profile claim fails closed. Re-run <code>pass</code> and record the
restored status 0 rather than merely asserting that the failure was fixed.

## Check your understanding

1. Rewrite "the updater is secure" as a scoped claim with a subject, version,
   finite scope, and at least three exclusions. **ASS-101-01**
2. Why does a SHA-256 content identity make substitution observable without
   proving authorship or correctness? **ASS-101-02**
3. A test passes 10,000 cases. Name four general conclusions that do not follow
   from that result alone. **ASS-101-02**
4. Why must an integration claim inventory the assumptions and TCB entries of
   its transitive dependencies? **ASS-101-03**
5. Draw a three-claim cycle and explain why none of the claims grounds the
   others. **ASS-101-03**
6. Two components are individually supported. What direct evidence would bear
   on their serialization boundary? **ASS-101-03**
7. Distinguish <code>REFUTED</code>, <code>UNSUPPORTED</code>, and
   <code>INVALID</code> using one concrete example of each. **ASS-101-04**
8. Why must an unreviewed test oracle be inside the assurance TCB even if it is
   not shipped to users? **ASS-101-04**

## Next step

Complete <code>lab.md</code>. Preserve both failure and restored-pass evidence.
Then complete the independent assessment without importing the Keystone model
or copying its packet-codec records.

## Sources

- [NIST SP 800-160 Volume 1 Revision 1, Engineering Trustworthy Secure Systems](https://csrc.nist.gov/pubs/sp/800/160/v1/r1/final) — assurance claims, evidence, trustworthiness, and lifecycle reasoning.
- [NIST SP 800-53A Revision 5, Assessing Security and Privacy Controls](https://csrc.nist.gov/pubs/sp/800/53/a/r5/final) — assessment methods, objects, evidence, findings, and limitations.
- [NIST SP 800-218, Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final) — traceable practices and evidence across software development.
- [RFC 9334, Remote ATtestation procedureS (RATS) Architecture](https://www.rfc-editor.org/rfc/rfc9334.html) — claims, evidence, appraisal, trust relationships, and attestation limits.
