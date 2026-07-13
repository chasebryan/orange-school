# Lab: requirements model for offline recovery

## Goal

Build and challenge a bounded security-requirements model for an offline
recovery workflow. State goals and a game-style notion, distinguish secret
keys, nonces, and security randomness, trace trust and composition boundaries,
and preserve evidence showing what the structural evaluator does and does not
establish.

This lab practices **CRY-101-01**, **CRY-101-02**, and **CRY-101-03**. It does
not implement or select a cryptographic algorithm.

## Setup

From the repository root, enter the module and verify the supplied example:

~~~sh
cd curriculum/modules/cry-101
module_root="$(pwd -P)"
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/worked_case.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

The last command must print exactly <code>cry-101 lab smoke: PASS</code> and
exit 0. The programs use only Python's standard library and local files.

Create a separate workspace and retain its path:

~~~sh
workdir="$(mktemp -d)"
cd -- "$workdir"
pwd
~~~

Run learner files with
<code>PYTHONPATH="$module_root/examples"</code>. Keep every created file under
the temporary workspace. No network, administrator access, external package,
secret value, cryptographic implementation, permission change, or deletion
command is required.

Use this scenario:

> A source workstation exports one recovery snapshot to removable media. A
> custodian carries the media to an isolated restore service. The media and its
> contents are untrusted: an attacker may copy, observe, replace, reorder,
> replay, or roll back packages. The attacker cannot compromise the source,
> restore service, approved platform key service, or custodian during the
> assessed transfer. Media destruction can deny recovery and remains an
> explicit unsatisfied availability risk.

## Tasks

1. **Define assets and consequences — CRY-101-01.** Create
   <code>requirements.md</code>. Define at least two assets: snapshot contents
   during transfer and restore acceptance state. For each, give its owner,
   lifetime, confidentiality/integrity/authenticity/freshness/availability
   goals as applicable, declared leakage, unacceptable outcome, and failure
   response. Do not use “secure,” “encrypted,” or “authenticated” as a
   substitute for a testable property.
2. **Specify the attacker — CRY-101-01.** List observation, storage-write,
   replay, and rollback capabilities; adaptive choices; resource and query
   bounds; and the scenario's exclusions. Explain why media deletion prevents
   a general availability claim. Add one changed model in which restore-service
   process compromise is allowed and identify every earlier claim that no
   longer follows.
3. **Write one game-style notion — CRY-101-01.** Define a two-choice
   confidentiality experiment for equal-length recovery snapshots. State
   setup, public inputs and leakage, adversary interfaces, adaptive behavior,
   challenge selection, forbidden trivial queries, exact win event, one-half
   baseline, advantage expression, time/query bounds, and assumptions. Label
   this a proposed requirement definition, not proof that an unspecified
   product meets it. Then write a separate freshness win event for acceptance
   of a previously accepted package identifier; explain why the primitive
   confidentiality game does not cover it.
4. **Draw trust and assumption maps — CRY-101-02.** Identify the source-to-media
   and media-to-restore boundaries. For each, state zones, bytes and metadata
   crossing, canonical parsing or validation point, release order, failure
   action, and diagnostic limits. Declare at least three assumptions with an
   owner, falsification signal, dependents, and containment response. Include
   durable nonce allocation, durable restore replay state, and conformance of
   the selected approved component to its policy.
5. **Separate material contracts — CRY-101-02.** Make a table with one secret
   snapshot key, one package nonce, and key-generation randomness. For every
   value state purpose, source, whether secrecy, unpredictability, authenticity,
   or uniqueness is required, the exact scope, lifetime, storage, consumers,
   and failure response. The nonce must be public and unique within the stated
   key epoch; explain why random-looking output alone would not prove that
   condition. The randomness row must name an approved platform random-bit
   facility in the hypothetical design without calling it from learner code.
6. **Build the bounded model — CRY-101-03.** Create
   <code>lab_model.py</code> and import the data types and evaluator from
   <code>security_requirements</code>. Encode the assets, attacker, assumptions,
   boundaries, three material declarations, goal-specific requirements, and at
   least two composition dependencies from your prose. One dependency must
   propagate a nonce-state failure; another must connect canonical encoding to
   the exact fields accepted by the restore service. Print
   <code>render_evaluation</code>'s result and exit nonzero when
   <code>structurally_complete</code> is false.
7. **Make the evidence failure-sensitive — CRY-101-03.** Create
   <code>test_lab_model.py</code> with <code>unittest</code>. Verify the complete
   model has no findings. Independently mutate it to remove a declared goal's
   requirement, remove nonce uniqueness, cite an unknown assumption, leave a
   trust boundary unused, and contradict secret/public material properties.
   Assert the exact finding code for each defect. Add invalid-construction tests
   for an empty capability set, an invalid identifier, a raw string in place of
   an enum, and more than 16 assets. Preserve one failing run caused by a
   deliberately wrong expected code, restore the expectation, and preserve the
   passing run.
8. **Audit composition and failure.** Create <code>failure-map.md</code> with a
   row for approved component behavior, secret-key control, nonce allocation,
   canonical encoding, restore replay state, endpoint integrity, and removable
   media availability. For each row state the dependent goal, trust owner,
   detection evidence, immediate action, recovery action, residual harm, and
   whether the item is inside the game from task 3. Explicitly state what a
   zero-finding evaluator result cannot establish.

## Verification

From the temporary workspace, run:

~~~sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$module_root/examples" \
  python3 -B lab_model.py > model.stdout 2> model.stderr
model_status=$?
printf 'model status: %s\n' "$model_status"

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$module_root/examples" \
  python3 -B -m unittest -v > tests.stdout 2> tests.stderr
test_status=$?
printf 'test status: %s\n' "$test_status"
~~~

Both final statuses must be 0. Inspect, rather than merely count, the evidence:

- every asset goal has an attacker-linked requirement and unacceptable
  outcome;
- game interfaces, restrictions, baseline, win event, bounds, and assumptions
  are explicit;
- key, nonce, and randomness properties remain distinct;
- both trust crossings define validation-before-release and a failure path;
- mutated models produce the intended finding codes;
- the failure map carries component premises into application claims; and
- no output describes structural completeness, unit tests, or a hypothetical
  standard component as proof of deployed security.

Finally rerun the unchanged module smoke check from the module directory with
<code>PYTHONDONTWRITEBYTECODE=1</code>. Preserve Python version, absolute
workspace, exact commands, stdout, stderr, and immediate statuses.

## Reflection

Write five to seven sentences:

- Which confidentiality statement changed most when you named visible
  metadata?
- Why is a public counter a plausible nonce but not key-generation randomness?
- Which premise crosses the largest number of composition edges?
- What becomes false after replay-state rollback even if record authentication
  still succeeds?
- What did the evaluator find, and which truth and implementation questions
  still require human analysis?
