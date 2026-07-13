# Lab: Beacon claim closure

## Goal

Build and challenge a bounded assurance bundle for **Beacon**, a fictional
offline event-log encoder. Produce scoped component and integration claims,
canonical evidence identities, complete assumption and TCB closure, and
fail-closed reports. The lab is distinct from the packet-codec worked example:
its subjects, claims, evidence methods, dependencies, and deliberate failures
must be Beacon-specific.

## Setup

From the repository root:

~~~sh
mkdir -p /tmp/ass-101-beacon
cp curriculum/modules/ass-101/examples/claim_model.py /tmp/ass-101-beacon/
cd /tmp/ass-101-beacon
export PYTHONDONTWRITEBYTECODE=1
export PYTHONHASHSEED=0
python3 -B claim_model.py
~~~

The last command has status 0 and no stdout or stderr. Create
<code>beacon_bundle.py</code> and <code>test_beacon.py</code> only in this
temporary directory. Do not use network access or undeclared packages. Record
<code>python3 --version</code>, the absolute path of the copied model, and its
SHA-256 before beginning.

## Tasks

1. Define the exact Beacon subject as one encoder artifact and profile:
   unsigned 32-bit event code, payload length from 0 through 256, canonical
   big-endian bytes, and at most 20 frozen cases. Write separate claims for
   field encoding, bound rejection, and their integration. Give every claim a
   finite scope and at least two meaningful exclusions. **ASS-101-01**
2. Add assumptions for the selected profile, the frozen expected-byte oracle,
   and the input-case source. Give each an owner, falsifier, and explicit state.
   Show one <code>unverified</code> state withdrawing support, then restore it to
   <code>confirmed</code>. **ASS-101-01**, **ASS-101-04**
3. Produce at least one test, one inspection, and one provenance evidence
   record. Each record names its precise subject and method, artifact digest,
   assumptions, TCB, and bounded facts. Recompute every identity independently
   and assert equality. Change only one fact and assert that the identity
   changes. Explain why neither digest proves correctness or authorship.
   **ASS-101-02**
4. Create claims <code>field-claim</code> and <code>bound-claim</code> with direct
   evidence. Create <code>beacon-profile-claim</code> depending on both. First
   omit integration evidence and assert exact status <code>UNSUPPORTED</code>
   and reason <code>no direct evidence; dependencies do not compose
   automatically</code>. Then add direct round-trip evidence and obtain
   <code>SUPPORTED</code>. **ASS-101-03**, **ASS-101-04**
5. Compute and print the integration claim's sorted dependency closure. Its
   assumption and TCB inventories must include the union used by the claim,
   its evidence, and both transitive claims. Omit one inherited TCB entry,
   assert finding <code>tcb-closure-missing</code> and status
   <code>INVALID</code>, then restore it. **ASS-101-03**
6. Add adversarial cases for an unknown evidence identity, unknown dependency,
   duplicate claim identifier, self-dependency, two-claim cycle, noncanonical
   exclusion order, a syntactically valid but incorrect evidence identity,
   failed direct evidence, inconclusive direct evidence, false assumption,
   unreviewed TCB entry, and compromised TCB entry. Assert the exact finding,
   exception, status, or reason for each. **ASS-101-02**, **ASS-101-04**
7. Independently construct all exact endpoints and smallest overflows: 32/33
   assumptions, 32/33 TCB entries, 64/65 evidence records, 32/33 claims, 16/17
   facts, 16/17 references, 300/301 characters, and dependency depth 8/9. Do
   not let an earlier cap mask the boundary under test. **ASS-101-03**,
   **ASS-101-04**
8. Preserve four deliberate-failure/restored-pass pairs: failed integration
   evidence, missing integration evidence, an unverified assumption, and an
   omitted inherited TCB entry. For each, record the exact command, stdout,
   stderr, and immediate process status before any restoration. **ASS-101-04**
9. Produce <code>claim-report.md</code> separating claim statements, model
   facts, evidence observations, assumptions, TCB entries, derived statuses,
   non-proofs, and residual risks. State explicitly that the lab establishes
   no Orange language, compiler, runtime, library, safety, security,
   conformance, or release claim. **ASS-101-01** through **ASS-101-04**

## Verification

First verify the supplied model from the repository root:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B curriculum/modules/ass-101/checks/lab_smoke.py
~~~

Expected stdout and immediate status:

~~~text
ass-101 lab smoke: PASS
status: 0
~~~

Then, from <code>/tmp/ass-101-beacon</code>, run your independent lab check:

~~~sh
python3 -B test_beacon.py
~~~

It must write exactly <code>beacon lab: PASS</code> plus a newline to stdout,
nothing to stderr, and exit 0. Run it from a second fresh temporary working
directory by absolute path. Hash the checker, bundle, report, and captured
stdout. Repeat with <code>PYTHONHASHSEED=17</code>; the report and evidence
identities must be byte-identical.

## Reflection

In 250 to 400 words, identify the strongest Beacon claim you can honestly make
and the first event that would withdraw it. Explain why supported components do
not establish a supported integration, why content identity is not provenance,
which non-production artifacts belong in the assurance TCB, and what evidence
would be needed to expand the claim beyond the finite profile.

