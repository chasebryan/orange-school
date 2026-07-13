# Release lifecycle and vulnerability response

A professional release is not finished when an artifact is uploaded. Its
owners must say what is supported, preserve enough identity to find affected
versions, receive and assess reports, stop invalid claims, deliver or withdraw
affected artifacts, notify downstream users, prevent unsafe rollback, and
practice recovery. Those are lifecycle obligations, not optional public-
relations work after engineering ends.

This module uses a bounded offline Python state machine to make ordering and
evidence obligations falsifiable. It does not publish releases or advisories,
contact a reporter, assign a real severity, revoke a real key, or make any
Orange compatibility, support, security, or release claim.

## Learning objectives

- **ASS-104-01:** Define a versioned release lifecycle with explicit artifact
  identity, compatibility and support policy, update and migration rules,
  rollback prevention, retirement, revocation, and withdrawal behavior.
- **ASS-104-02:** Operate a vulnerability response from bounded intake and
  triage through claim invalidation, containment, advisory, update or
  withdrawal, downstream notification, closure, and recovery.
- **ASS-104-03:** Preserve canonical timelines and failure-sensitive evidence,
  exercise exact endpoints and illegal transitions, and run deterministic
  recovery drills whose results can be replayed offline.
- **ASS-104-04:** Inventory the lifecycle trust boundary and state only claims
  supported by local records, distinguishing referenced actions from verified
  external execution and excluding unsupported Orange or production claims.

## Prerequisites

Pass <code>ass-102</code> and <code>ass-103</code>. You should be able to design
adversarial tests, distinguish a claim from its evidence, bind an artifact to
exact content, and replay a bounded evidence package offline. The supplied
courseware requires Python 3.11 or newer and only the standard library.

## Lesson

### A release begins with an inventory and a policy

A release record binds a product identifier, version or revision, artifacts,
source revision, build inputs, signatures or attestations where used, release
channel, publication time, and owners. A mutable page saying “latest” is not an
identity. An incident responder needs to answer which exact artifacts exist,
who received them, which components they contain, which claims accompanied
them, and which newer artifacts replace them.

A support policy is a public contract that answers at least:

1. which channels and versions receive correctness and security fixes;
2. the support start and end conditions;
3. the response and remedy targets, with exceptions and escalation paths;
4. supported platforms, architectures, configurations, and dependencies;
5. compatibility and migration promises;
6. how users learn about updates, end of support, withdrawal, and revocation;
7. whether old versions remain downloadable or installable; and
8. which emergency actions owners may take.

“Supported” must not be inferred from a download still existing. A release can
be available but unsupported, compatible but unsafe, or within ordinary
support while temporarily contained. Planned end of support should have a
notice period, migration path, archive policy, and owner. A vulnerability may
create obligations even after ordinary support ends when contracts, law,
coordinated disclosure, or continuing risk require them; the applicable policy
must say who decides.

### Compatibility and security floors are different

Compatibility has several directions. A new reader may accept old data; an old
reader may not accept new data. An API may preserve source compatibility while
changing binary layout or operational behavior. State the object being
compared, direction, version pair, environment, and evidence.

A migration record says how state moves forward, what is backed up, which
preconditions are checked, whether migration is reversible, and how partial
failure is recovered. It does not by itself authorize an old vulnerable binary
to run. A **compatibility floor** can remain at revision 7 because revision 8
can migrate revision-7 data, while a **rollback floor** becomes revision 8 so
the vulnerable executable cannot be reinstalled.

Rollback prevention must survive restart and attacker-controlled mirrors. A
client needs trusted, persistent version state and authenticated metadata;
merely hiding an old download link is not enforcement. The Update Framework
specification illustrates checks that reject older trusted metadata and expired
metadata associated with rollback and freeze attacks. This course model keeps
only an integer floor. It does not implement TUF, signatures, key rotation,
expiration, mirrors, or compromise recovery.

### Intake treats reports as hostile claims, not established facts

A vulnerability intake channel should publish scope, contact, encryption,
expected response, disclosure policy, and safe-handling instructions. RFC 9116
defines <code>security.txt</code> as a machine-readable aid for vulnerability
disclosure, while warning that reports and referenced resources may be stale,
malformed, or malicious. A contact file is not permission to test, proof a
report was received, or a complete incident-response program.

Bound intake before parsing or opening attachments. Retain the original bytes
immutably, calculate an identity, separate untrusted content from operator
commands, and record receipt without promising validity. A useful initial
record includes:

- stable report identity and receipt channel;
- reporter contact restrictions and disclosure expectations;
- claimed product, version, configuration, impact, and reproduction steps;
- attachments and their exact content identities;
- possible duplicates, related incidents, and upstream/downstream ownership;
- handling classification and authorized viewers; and
- acknowledgment, triage, escalation, and disclosure deadlines.

Timeout, malformed input, duplicate reports, spam, and disagreement are states
to handle explicitly. They must not silently become “not vulnerable.”

### Triage scopes the problem and its uncertainty

Triage attempts to reproduce the report in an isolated environment, identify
affected and unaffected versions, test preconditions, estimate impact and
exploitability, and identify component owners. Severity is a decision aid,
not a proof of truth and not a substitute for affected-version analysis.

Record what is known, inferred, disputed, and untested. Preserve alternative
hypotheses and the evidence that rejected them. A public score may be useful,
but the team must also account for deployment-specific exposure, active
exploitation, safety implications, data sensitivity, workaround quality, and
the time required by downstream integrators.

Triage also maps claims. If evidence undermines a statement such as “all
supported inputs are rejected safely,” mark that claim **suspended** while the
scope is investigated. Do not continue publishing the statement because a
final root cause or severity is pending. Claim invalidation can trigger a
documentation correction, release containment, test quarantine, or broader
incident declaration.

### Containment reduces exposure without pretending to repair it

Containment actions may stop publication, pause an update channel, disable a
feature, rotate credentials, revoke signing authority, isolate infrastructure,
or provide a narrowly tested workaround. Each action needs an owner, time,
scope, rollback condition, expected risk reduction, side effects, verification,
and communication plan.

Containment is not remediation. Removing an artifact from one index does not
remove cached copies. Revoking a credential does not update clients that never
check revocation. Disabling a service can create availability or safety risk.
Preserve the decision and test both the intended effect and foreseeable escape
paths.

The supplied model forces claim suspension before release containment. That is
a teaching policy, not a universal organizational rule. Its purpose is to make
one dangerous ordering error observable: a workflow must not keep a disputed
claim labeled valid while marking the affected release safely contained.

### Advisories are versioned technical artifacts

A useful advisory identifies the affected product and versions, unaffected or
fixed versions, impact, preconditions, severity convention, discovery and
credit details where authorized, mitigations, update and migration steps,
rollback warnings, timeline, references, and revision history. Unknown facts
are labeled unknown. Corrections append or supersede records rather than
silently rewriting history.

The Common Security Advisory Framework 2.0 defines a structured JSON language
for product, vulnerability, impact, and remediation information. A valid CSAF
document can improve machine exchange; it does not establish that the stated
affected products, remedies, or external notifications are correct.

Embargo decisions require a defined constituency, participants, information-
handling rules, target disclosure time, early-disclosure triggers, and a plan
for downstreams that need lead time. An embargo is coordination, not secrecy
for its own sake. Active exploitation, reporter publication, failed
coordination, or inability to contain may change the balance.

### Update, migration, withdrawal, and revocation are distinct remedies

An **update** replaces an affected artifact with a tested revision. It needs
source and dependency identities, review, regression and adversarial tests,
affected-version tests, reproducible evidence, publication checks, migration
instructions, and an update-path test from every supported origin.

A **withdrawal** says an artifact must no longer be selected or installed. A
**revocation** invalidates authority or trust, such as a key, signature,
certificate, token, or delegated role. A **retirement** is planned end of
support. These actions can coincide, but they are not interchangeable. A
withdrawn artifact may remain cryptographically authentic; a revoked key may
have signed unaffected artifacts; a retired version may remain safe within a
documented unsupported archive.

When no safe update exists, withdrawal plus an advisory and migration to an
alternative can be the honest remedy. Preserve what remains unresolved and the
conditions for reinstatement. Never relabel withdrawal as a successful patch.

### Downstream notification is part of remediation

A maintainer cannot assume users monitor one website. Build a constituency map
before an incident: package distributors, image builders, embedded vendors,
cloud operators, direct customers, dependency consumers, mirrors, and internal
teams. Record contact method, product/version relationship, disclosure
constraints, acknowledgment, requested action, deadline, and follow-up.

Notification evidence should distinguish:

- message prepared;
- delivery attempted;
- transport accepted;
- recipient acknowledged;
- recipient assessed impact; and
- recipient completed remediation.

The example model retains downstream identifiers but performs no transport.
Its “notified” event means only that a local state transition referenced a
notification artifact. It cannot support the stronger statement that any
person received, understood, or acted on a message.

### Closure requires recovery evidence, not calendar exhaustion

Define closure criteria before the incident. For an update path they commonly
include a fixed artifact, migration evidence, rollback prevention, updated
claims, advisory publication, downstream notification, channel verification,
monitoring, and an owner accepting residual risk. A withdrawal path instead
shows selection and install denial, advisory publication, migration or
alternative guidance, and downstream notification.

A recovery drill should start from retained artifacts in a fresh environment
and test at least:

1. reconstructing the incident timeline and exact release identities;
2. installing the current allowed revision;
3. rejecting the withdrawn or below-floor revision;
4. replaying migration and restoring from an interrupted migration;
5. rebuilding advisory and notification records;
6. rotating or recovering update authority where relevant; and
7. detecting a deliberately corrupted or missing artifact.

Record command, working directory, runtime, inputs, stdout, stderr, immediate
status, duration or logical work count, and artifact identities. A successful
drill shows that those paths worked under the drill conditions. It does not
prove the next incident will match them.

### A timeline needs clocks, owners, and evidence strength

Use UTC timestamps with a named clock source for real operations. Distinguish
event time, observation time, record time, and publication time. Preserve
uncertainty when the exact event time is unknown. Deadlines should identify
their policy or legal source and escalation behavior.

The course model uses integer **logical ticks** so evidence is deterministic.
It requires strictly increasing ticks and at most 16 retained events. Those
ticks are not dates, service-level compliance evidence, or wall-clock
measurements. The model also caps revisions at 8, evidence references and
downstreams at 4, identifier length at 32, and ticks at 10,000. It checks each
bound before retaining the next event.

Every transition request and lifecycle snapshot uses exact Python types. The
model rejects unsupported actions, payload fields on the wrong action,
duplicate downstreams, out-of-order time, skipped lifecycle states, update
revision jumps, closure without migration and rollback evidence, and work past
the event cap. Immutable records reduce accidental mutation but do not prove
the recorded history occurred.

### Canonical records improve replay but do not authenticate truth

The model serializes a fully validated snapshot as sorted compact JSON and
computes SHA-256 over its UTF-8 bytes. Canonicalization makes the same in-memory
record produce the same bytes. A digest detects changes relative to a trusted
digest; it does not identify the author, prove the event evidence exists, or
show an advisory was published.

The local trust boundary includes the written transition contract, Python
semantics, validator, serializer, hash implementation, exact source selected,
runtime, operating system, hardware, command capture, and the human mapping
from evidence identifiers to external artifacts and actions. Tests and
deliberate failures exercise named paths. They do not prove completeness,
absence of other defects, authenticity, delivery, legal compliance, incident
closure, update security, or any property of Orange.

## Worked example

The supplied **Atlas** scenario starts tracking revision 7, promotes and
publishes it, receives and triages a critical report, suspends its claims,
contains it, records an advisory, releases revision 8, records migration,
raises the rollback floor, records four downstream references, closes the
incident, and performs a recovery drill.

~~~sh
cd curriculum/modules/ass-104
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/lifecycle_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

The scenario reaches 16 events, revision 8, four evidence references on one
event, four downstreams, identifier length 32, and logical tick 10,000 without
crossing another cap. Revision 7 remains compatible input to migration but is
below the post-remediation install floor. The last tick is outside the recorded
ordinary support window, demonstrating that a recovery record is not itself a
renewed support promise.

The smoke suite preserves illegal-transition failures followed by legal
restoration, exact-type rejection, the update and withdrawal paths, rollback
denial, support-window endpoints, event and revision bounds, canonical replay,
and execution in a fresh temporary directory.

## Check your understanding

1. Why are compatibility, support, availability, and security different axes?
2. Which evidence can justify suspending a claim before root cause is known?
3. Why is containment not remediation?
4. What must an advisory say about affected and fixed versions?
5. How do withdrawal, revocation, and retirement differ?
6. Why can a successful migration coexist with a rollback prohibition?
7. What is the difference between a prepared notice and recipient remediation?
8. Which facts does a canonical JSON digest establish, and which does it not?
9. Why may incident work continue after the ordinary support window ends?
10. Which trusted step connects a local evidence identifier to a real external
    action?

## Next step

Complete the **Harbor** lab in a fresh temporary directory, using a distinct
record grammar and transition implementation. Preserve each deliberate
failure before restoring the legal path. Then complete the independent
**Beacon** assessment without importing or translating the supplied model.
Keep all claims bounded to the artifacts and actions actually checked.

## Sources

- [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final) —
  current incident-response recommendations integrated with cybersecurity risk
  management; final published April 2025.
- [FIRST PSIRT Services Framework 1.1](https://www.first.org/standards/frameworks/psirts/psirt_services_framework_v1-1)
  — product vulnerability intake, stakeholder coordination, remediation,
  advisory, lifecycle, and continuous-improvement service areas.
- [RFC 9116](https://www.rfc-editor.org/rfc/rfc9116.html) — the
  <code>security.txt</code> vulnerability-disclosure contact format and its
  trust, staleness, malformed-input, and permission boundaries.
- [OASIS Common Security Advisory Framework 2.0](https://docs.oasis-open.org/csaf/csaf/v2.0/os/csaf-v2.0-os.html)
  with [Errata 01](https://docs.oasis-open.org/csaf/csaf/v2.0/errata01/os/csaf-v2.0-errata01-os.html)
  — structured product security advisory exchange.
- [The Update Framework Specification 1.0.28](https://theupdateframework.github.io/specification/v1.0.28/)
  — authenticated update metadata, rollback and freeze checks, persistent
  trusted state, and bounded retrieval concepts.
- [Bounded lifecycle model](examples/lifecycle_model.py) — normative semantics
  for this course example only.
- [Portable smoke suite](checks/lab_smoke.py) — endpoint, adversarial,
  illegal-transition, restoration, and replay evidence.
