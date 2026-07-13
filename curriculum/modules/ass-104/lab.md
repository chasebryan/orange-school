# Lab: operate the Harbor release and incident lifecycle

## Goal

Build and audit an independent bounded lifecycle for a fictional Harbor
library. Define its release, compatibility, support, withdrawal, and incident
policies; reject illegal transitions; preserve update and withdrawal evidence;
and run a recovery drill without claiming that any external action occurred.

## Setup

From the repository root, inspect and run the supplied Atlas model:

~~~sh
cd curriculum/modules/ass-104
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/lifecycle_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

Use Python 3.11 or newer and only the standard library. Create a fresh
temporary directory with <code>mktemp -d</code>. Keep every generated source,
record, failure, and restored result below it. Do not copy, import, rename, or
mechanically translate <code>lifecycle_model.py</code>. Harbor uses different
states, caps, record names, and scenarios. Do not use a network, real contact
address, real vulnerability, production signing key, or Orange artifact.

## Tasks

1. **Define lifecycle policy — ASS-104-01.** Write
   <code>harbor-policy.md</code>. Give exact identities for fictional artifacts,
   source, build evidence, channels, owners, and claims. Define support start
   and end, platforms, compatibility directions, migration origins, response
   targets, retirement notice, archive behavior, update selection, withdrawal,
   revocation, and rollback prevention. Distinguish availability,
   compatibility, support, and safety.
2. **Publish the intake and triage contract — ASS-104-02.** Write
   <code>response-contract.md</code>. Define bounded report bytes, attachments,
   fields, identities, duplicate handling, acknowledgment, triage and
   escalation targets, disclosure coordination, hostile-input treatment, and
   authorized viewers. Define severity inputs without treating a severity as
   truth. Explain when a disputed claim becomes suspended.
3. **Build an independent state machine — ASS-104-01 and ASS-104-02.** Create
   <code>harbor_lifecycle.py</code> with immutable exact-type records and
   separate validation and transition entry points. Use at most six revisions,
   12 events, three evidence references per event, three downstreams, 24
   identifier characters, and logical tick 500. Define distinct state names.
   Check each cap before retaining the next item. Use stable code/message pairs.
4. **Enforce legal ordering — ASS-104-02.** Require candidate review before
   release, triage before impact-claim suspension, claim suspension before
   containment, containment before advisory, and exactly one of update or
   withdrawal before closure. For an update, require migration evidence,
   rollback-floor advancement, and notification. For withdrawal, require
   advisory, selection denial, and notification. Reject unknown actions,
   payload smuggling, repeated states, skipped states, non-increasing time, and
   foreign records.
5. **Make the endpoints feasible — ASS-104-03.** Construct one legal update
   scenario that simultaneously reaches revision 6, 12 events, three evidence
   references on one event, three unique downstream references, identifier
   length 24, and logical tick 500. Show the endpoint arithmetic before
   running. Attempt revision 7, event 13, evidence item 4, downstream 4,
   identifier 25, and tick 501 separately so the expected diagnostic is not
   masked by another cap.
6. **Preserve deliberate failures and restoration — ASS-104-03.** Preserve at
   least six failures: publish before review; contain before claim suspension;
   update before advisory; close before migration; duplicate notification;
   and rollback below the security floor. For each, capture separate stdout and
   stderr, record the immediate nonzero status, restore only the missing legal
   step, rerun, and record the immediate zero status. Explain which obligation
   caught the error.
7. **Exercise withdrawal and revocation — ASS-104-01 and ASS-104-02.** Run a
   second incident where no safe update exists. Publish a fictional advisory,
   withdraw selection, revoke a fictional release authority, notify all three
   downstream identities, deny current and older installation attempts, and
   close with residual risk recorded. Do not call withdrawal a patch or
   deletion from caches.
8. **Create canonical evidence — ASS-104-03.** Serialize a fully validated
   record with an explicitly documented field order or sorted-key JSON. Hash
   its exact UTF-8 bytes. Replay twice from a fresh process and require
   byte-identical output. Reject unsupported host objects, Booleans in integer
   fields, string subclasses where exact strings are required, malformed event
   sequences, duplicate evidence, and a forged invariant-breaking snapshot.
9. **Map communications and claims — ASS-104-02 and ASS-104-04.** Write
   <code>advisory.md</code> and <code>notification-ledger.csv</code>. Include
   affected, unaffected, fixed, and withdrawn versions; impact and
   preconditions; workaround limits; update and migration steps; rollback
   warning; timeline; revision history; constituency; attempted delivery;
   acknowledgment; requested action; and follow-up. Mark every fictional or
   unperformed action explicitly.
10. **Run a recovery drill — ASS-104-03.** From a new directory, reconstruct
    exact inputs, replay the timeline, allow the fixed revision, deny rollback,
    detect one corrupted record, rebuild the advisory, and verify the
    downstream ledger identities. Preserve command, Python version, working
    directory, hashes, channels, immediate statuses, and logical work count.
11. **Audit the trust boundary — ASS-104-04.** In <code>trust.md</code>, list
    the written policy, report encoding, transition implementation, validator,
    serializer, hash, artifact loader, Python runtime, operating system,
    hardware, commands, and human mappings to evidence and external actions.
    Explicitly reject claims of actual publication, delivery, acknowledgment,
    key revocation, vulnerability validity, legal compliance, update-system
    security, production readiness, or any Orange behavior.

## Verification

Run Harbor from the isolated workspace and capture the immediate statuses:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B harbor_lifecycle.py \
  >lifecycle.stdout 2>lifecycle.stderr
lifecycle_status=$?
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v test_harbor_lifecycle.py \
  >tests.stdout 2>tests.stderr
tests_status=$?
printf 'lifecycle=%s tests=%s\n' "$lifecycle_status" "$tests_status"
~~~

Both statuses must be zero after every deliberate failure and restoration has
been preserved separately. Review the policy, transition table, validator,
update and withdrawal records, advisory, notification ledger, recovery drill,
and trust inventory. Confirm that all exact and one-beyond endpoints ran, the
rollback floor is distinct from compatibility, notification records do not
claim receipt, and closure cannot bypass its remedy-specific evidence.

Finally rerun the repository evidence independently:

~~~sh
cd /absolute/path/to/orange-school
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  curriculum/modules/ass-104/checks/lab_smoke.py
~~~

## Reflection

Write six to nine sentences answering: Which policy field was easiest to leave
ambiguous? What evidence justified suspending a claim before final root cause?
Why did containment not qualify as remediation? Which update-path gate
prevented the most dangerous shortcut? How did withdrawal differ from
revocation? Which downstream evidence was weakest? What did canonical replay
establish? What did the recovery drill fail to establish? Which additional
authority and evidence would be required to apply this process to a real
Orange release?
