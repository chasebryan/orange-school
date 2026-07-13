# Assessment: Beacon release correction and response audit

## Instructions

Complete this assessment independently in a fresh temporary directory using
Python 3.11 or newer and only the standard library. Submit the release and
support policy, response contract, transition specification, executable model,
tests, update and withdrawal cases, advisory, downstream ledger, recovery
drill, trust inventory, and evidence map. Everything must run offline and all
generated artifacts must remain beneath the assessment workspace.

Do not import, copy, rename, or lightly translate the Atlas or Harbor models.
Beacon must use its own immutable records, state names, payload grammar,
diagnostics, scenarios, and canonical encoding. Use only fictional products,
contacts, vulnerabilities, downstreams, keys, and actions. No task authorizes
publication, notification, revocation, account access, or an Orange claim.

The assessment covers:

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

Beacon admits revisions 1 through 5, at most 14 retained events, four evidence
identifiers per event, four downstream identifiers, identifier length 28, and
logical ticks 0 through 900. A model may begin tracking an existing revision 4
if it states that earlier history is outside the record. Every collection is an
exact tuple, every integer excludes Boolean values, and every action and state
is an exact lowercase string from a declared vocabulary.

## Knowledge check

1. Distinguish artifact availability, compatibility, ordinary support,
   security support, safety, authenticity, and current selection.
2. What fields bind a release to exact source, build inputs, artifacts,
   channel, owners, claims, and downstream constituencies?
3. Why are acknowledgment, triage, severity, reproduction, affected-version
   analysis, and claim invalidation different decisions?
4. Give three containment actions and state why none automatically establish
   remediation.
5. Distinguish update, migration, rollback prevention, withdrawal, revocation,
   and planned retirement.
6. Which advisory fields let an automated or human consumer identify whether
   action is required, and how are corrections represented?
7. Give the useful evidence ladder from a prepared notice through confirmed
   downstream remediation.
8. What can canonical JSON plus SHA-256 establish? Which authenticity and
   external-action claims remain unproved?
9. Why can a recovery drill succeed without proving that a future incident or
   real update service will succeed?
10. Which clocks and times belong in a real incident timeline, and why are
    logical ticks insufficient for service-level or legal claims?

## Independent task

1. **Release and support contract — ASS-104-01.** Create
   <code>beacon-release-policy.md</code>. Specify exact product, source, build,
   artifact, channel, owner, platform, dependency, claim, support-window, and
   downstream identities. Define compatibility direction, migration origins,
   ordinary and security support, end-of-support notice, archival selection,
   update discovery, withdrawal, revocation, and rollback rules. Include a
   decision table for supported, expired, contained, fixed, withdrawn, and
   retired releases.
2. **Vulnerability handling contract — ASS-104-02.** Create
   <code>beacon-response.md</code>. Bound report and attachment input before
   retention. Define stable identity, hostile-input isolation, duplicate and
   spam handling, acknowledgment, triage, escalation, disclosure coordination,
   affected-version analysis, severity inputs, owners, deadlines, and claim
   suspension. Distinguish unknown, disputed, not reproduced, unaffected, and
   remediated.
3. **Executable lifecycle — ASS-104-01 and ASS-104-02.** Implement
   <code>beacon_model.py</code> with exact immutable release, incident, event,
   transition, policy-decision, and canonical-record structures. Validate an
   entire snapshot before each transition and serialization. Reject foreign
   objects, subclasses, payloads on the wrong action, malformed identifiers,
   non-contiguous event sequences, non-increasing ticks, duplicate references,
   inconsistent states, and every cap plus one using stable code/message pairs.
4. **Update path — ASS-104-02.** Require reviewed candidate, publication,
   report intake, triage, claim suspension, containment, advisory, next-revision
   update, migration evidence, rollback-floor advancement, all downstream
   references, closure, and recovery. Do not let an advisory, green test, or
   elapsed deadline substitute for an earlier transition.
5. **Withdrawal path — ASS-104-01 and ASS-104-02.** For a separate fictional
   report with no safe patch, require claim suspension, containment, advisory,
   withdrawal, fictional authority revocation, denial of current and older
   selection, migration or alternative guidance, four downstream references,
   closure, and a residual-risk record. Preserve that withdrawal did not erase
   cached artifacts or repair their bytes.
6. **Joint endpoint proof — ASS-104-03.** Begin tracking revision 4 and produce
   an update to revision 5. Reach exactly 14 events, four evidence identifiers
   on one event, four downstream identifiers across two notification events,
   identifier length 28, and tick 900 in one legal update and recovery history.
   Show the transition count and check each bound before retention. Isolate
   revision 6, event 15, evidence item 5, downstream 5, identifier length 29,
   and tick 901 so each yields its own expected diagnostic.
7. **Adversarial and deliberate-failure evidence — ASS-104-03.** Directly test
   status-like equality spoof objects, Booleans in every integer field, string
   and tuple subclasses, missing and extra payloads, invalid phases, forged
   events, repeated notification, time reversal, update revision jump,
   containment with valid claims, closure without remedy, and drill before
   closure. Preserve at least eight immediate nonzero failures and the
   independent zero-status restoration after each.
8. **Advisory and downstream communication — ASS-104-02.** Create a versioned
   fictional advisory with exact affected/unaffected/fixed/withdrawn ranges,
   impact, preconditions, severity convention, workaround limits, remedy,
   migration, rollback warning, timeline, credits, references, and revision
   history. Create a downstream ledger separating preparation, attempted
   delivery, transport acceptance, acknowledgment, assessment, and completed
   remediation. Never mark unperformed external steps complete.
9. **Canonical replay and recovery — ASS-104-03.** Serialize with a documented
   canonical rule and hash exact UTF-8 bytes. Reconstruct the state twice in
   fresh processes and require identical bytes and digest. In a recovery drill,
   allow revision 5, reject revision 4 after the floor rises, reject a corrupted
   record, rebuild the advisory and ledger, and preserve commands, runtime,
   directory, channels, immediate statuses, hashes, and logical work.
10. **Trust and claim audit — ASS-104-04.** Create <code>trust.md</code> and
    <code>evidence-map.md</code>. Inventory the policies, report encoding,
    validator, transition code, serializer, hash, artifact selection, Python,
    operating system, hardware, commands, and human mappings. Classify each
    item as definition, referenced evidence, local execution, attempted
    external action, verified external result, or unsupported. Explicitly
    exclude real vulnerability validity, actual publication or delivery,
    revocation effectiveness, update-protocol security, legal or service-level
    compliance, production readiness, and every Orange release, compatibility,
    support, or security claim.

## Completion criteria

Use the [rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. A passing submission must:

- satisfy **ASS-104-01** with exact release identity, compatibility and support
  semantics, migration, rollback, update, retirement, withdrawal, and
  revocation policy;
- satisfy **ASS-104-02** with bounded intake, evidence-driven triage, prompt
  claim invalidation, ordered containment/advisory/remedy, downstream mapping,
  and remedy-specific closure;
- satisfy **ASS-104-03** with a bounded exact-type implementation, jointly
  feasible endpoints, illegal-transition failures and restoration, canonical
  replay, and a falsifiable recovery drill;
- satisfy **ASS-104-04** with a complete trust inventory and conclusions no
  stronger than local checked evidence; and
- run offline under Python 3.11 or newer using only the standard library.

A skipped claim-suspension gate, containment called remediation, advisory
called delivery, withdrawal called deletion or repair, rollback allowed below
the floor, notification reference called acknowledgment, unreachable endpoint,
mutation without preserved failure status, or any external or Orange claim
cannot pass.
