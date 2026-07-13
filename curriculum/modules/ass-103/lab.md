# Lab: build and falsify an offline replay capsule

## Goal

Build **Ember**, an independent bounded replay-capsule model. Bind one selected
subject to canonical manifest bytes, complete dependency and provenance closure,
an environment/TCB profile, and deterministic output. Treat every capsule as
hostile, validate it before material retention, replay it without a network only
inside a temporary directory, and preserve evidence that detects substitution,
omission, addition, rollback, and nondeterminism.

This lab practices **ASS-103-01**, **ASS-103-02**, **ASS-103-03**, and
**ASS-103-04**. Ember is not Quartz or Orange. Do not copy or mechanically
rename the supplied model.

## Setup

Read [the lesson](lesson.md), inspect but do not edit the supplied examples, and
confirm the course baseline:

~~~sh
cd curriculum/modules/ass-103
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/replay_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

The final command must print <code>ass-103 lab smoke: PASS</code> and exit zero.
Create a fresh temporary workspace for your independent work:

~~~sh
workdir="$(mktemp -d)"
cd -- "$workdir"
pwd
python3 --version
~~~

Use Python 3.11 or newer, <code>PYTHONDONTWRITEBYTECODE=1</code>,
<code>python3 -B</code>, and only the standard library. Keep all generated
capsules, extracted material, results, mutations, and evidence below that
temporary path. Do not access a network, install a package, modify global
configuration, or write to the course repository.

## Tasks

1. **Write the assurance claim — ASS-103-04.** In <code>claim.md</code>, name
   Ember's exact subject, input envelope, environment, recipe, comparison
   relation, and trust-anchor assumption. List unsupported authenticity,
   freshness, correctness, safety, security, build, and Orange conclusions.
2. **Specify canonical manifest bytes — ASS-103-01.** Implement
   <code>ember_replay.py</code>. Accept one canonical ASCII JSON object with
   sorted keys, compact separators, duplicate-key rejection, sorted unique
   set-like arrays, and no unknown fields. Bind schema, subject, sequence,
   materials, dependency ids, provenance, environment, TCB, roots, recipe, and
   expected output. Re-encoding an accepted manifest must reproduce its bytes.
3. **Choose and enforce different bounds.** Ember permits 1–12 materials,
   3,072 bytes per material, 24,576 total material bytes, 12,288 manifest
   bytes, 72-byte ASCII paths, 12 references per array, six dependency edges,
   and 98,304 archive bytes. Ordinary text is at most 96 printable ASCII bytes;
   sequence is an exact integer from 0 through 4,294,967,295. Reject Boolean
   values where an integer is required. Document why each counter is checked
   before excess work or retention.
4. **Bind material and supply-chain identities — ASS-103-01.** Each material
   has a canonical id, path, exact size, SHA-256 content identity, dependency
   ids, and provenance id. Each provenance record has a producer, origin,
   revision, complete governed-material list, and canonical content identity.
   State why a digest is not a signature or proof that a provenance statement
   is true.
5. **Model separate trusted selection — ASS-103-03.** Define an immutable
   anchor with expected manifest identity, subject, minimum sequence, approved
   provenance identities, and approved TCB identities. Check raw manifest
   identity before using bundle policy. Explain how direct derivation from the
   untrusted capsule would defeat substitution and rollback detection.
6. **Close every dependency — ASS-103-01.** Traverse declared roots, reject an
   unknown id, self-edge, cycle, or path deeper than six edges, and require all
   declared materials to be in the selected closure. Require provenance's
   governed-material union and archive material paths to equal the same set.
   Sort the final closure independently of dictionary iteration.
7. **Scan the archive before material retention — ASS-103-02.** Accept only one
   uncompressed USTAR profile that you specify byte for byte. Validate every
   512-byte header, checksum encoding, regular-file type, empty link target,
   fixed uid/gid/mode/mtime/name fields, lexical member order, zero member
   padding, two-block terminator, and fixed final record padding. Reject
   symbolic/hard links, devices, directories, PAX/GNU extensions, absolute or
   backslash paths, <code>.</code>/<code>..</code>, uppercase or Windows
   device-name components, trailing-dot aliases, duplicate names, path
   aliases, and every count/size overflow in a first metadata pass.
8. **Verify before writing — ASS-103-02.** Retain the bounded manifest only
   after the header pass. Authenticate and structurally validate it before
   slicing material payloads. Verify each material's declared and observed
   size/digest before writing it to a freshly created temporary directory.
   Never follow or create a link. Require the workspace to be removed before a
   successful result returns.
9. **Define a distinct deterministic recipe — ASS-103-03.** Ember's built-in
   <code>length-prefixed-tree-v1</code> recipe emits <code>EMB1</code>, then
   every closure id and payload in sorted order using explicit unsigned
   big-endian widths you specify. It cannot execute bundle code or invoke a
   package manager. Compare the complete output bytes, size, and SHA-256 with
   the manifest and write the result only below the temporary root.
10. **Capture environment and TCB — ASS-103-01, ASS-103-04.** Bind and observe
    Python implementation/full version, recipe-engine version, and the SHA-256
    identity of <code>ember_replay.py</code>. Record the interpreter, model,
    JSON parser, digest implementation, filesystem, OS, and anchor-selection
    channel in the TCB/residual-assumption table. Reject observed declared TCB
    mismatches.
11. **Test exact normal and endpoints — ASS-103-02.** Build a fixed capsule in
    memory, replay it twice, and assert equal manifest, archive, closure, and
    output bytes. Separately test 0 and 4,294,967,295 sequences; 72/73 path
    bytes; 3,072/3,073 member bytes; 12/13 materials; exactly 24,576 total
    bytes and one byte above; depth 6/7; exactly 98,304 archive bytes or the
    largest constructible valid size, plus a direct 98,305-byte rejection.
    Record calculations so one bound cannot accidentally mask another.
12. **Test hostile structures — ASS-103-02.** Construct in-memory capsules with
    a symbolic link, hard link, directory, device, PAX header, GNU long name,
    absolute path, <code>../</code>, backslash, duplicate path, alternate path
    spelling, nonzero member padding, changed mode, wrong checksum, unsorted
    member order, truncated header/data, missing terminator, trailing nonzero
    bytes, missing declared material, and undeclared extra. Assert stable
    diagnostic code/message and no material workspace for every rejection.
13. **Test supply-chain attacks — ASS-103-03.** Isolate payload substitution;
    manifest substitution under the old anchor; expected digest plus payload
    substitution under the old anchor; provenance statement substitution;
    unapproved TCB change; unknown dependency; cycle; an unclosed extra
    material; sequence below the trusted floor; and environment mismatch. Show
    exactly which binding rejects each case.
14. **Test comparison and nondeterminism — ASS-103-03.** Corrupt expected size,
    expected digest, frame order, one length byte, and one output byte. Create a
    deliberately nondeterministic recipe variant using shuffled input order and
    show the exact deterministic comparison catches it. Restore the declared
    recipe after each case.
15. **Observe deliberate failure and restoration — ASS-103-04.** In isolated
    temporary copies, make four mutations: wrong expected replay value, accept
    one link type, omit the sequence-floor comparison, and reverse closure
    order. Run one targeted test for each mutation, preserve immediate nonzero
    status plus stdout/stderr, restore the source, and preserve the zero-status
    targeted rerun. Do not weaken or skip a test to recover.
16. **Write <code>evidence.md</code> — ASS-103-04.** Record absolute temporary
    path, Python and platform values, source/capsule/manifest/output hashes,
    exact commands, both channels, immediate statuses, endpoint arithmetic,
    mutation/restoration pairs, and a specification/observation/inference/
    unsupported-claim matrix. Justify O(B + M + D + P) work and O(P) retained
    payload/output within your caps. Label Python, input bundle, object,
    filesystem, allocator, kernel, and hardware memory outside exact byte
    claims.

## Verification

Run the complete independent suite from the temporary workspace:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v \
  >passing.stdout 2>passing.stderr
status=$?
printf 'test status: %s\n' "$status"
sha256sum ember_replay.py test_ember_replay.py claim.md evidence.md \
  >submission.sha256
~~~

Status zero is necessary but not sufficient. Inspect the evidence and confirm:

- the anchor is separate from the capsule and checked before bundle policy;
- every raw header is checked before any material payload is retained;
- manifest, closure, archive paths, and provenance coverage are equal sets;
- only verified bytes are written, only below a new temporary directory;
- output comparison is byte-exact and its order/widths are specified;
- all endpoint, hostile, supply-chain, nondeterminism, and four observed
  failure/restoration cases are present; and
- every conclusion is limited to Ember's exact recorded model and environment.

Then rerun the course smoke check unchanged:

~~~sh
cd /path/to/orange-school
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  curriculum/modules/ass-103/checks/lab_smoke.py
~~~

It must still print <code>ass-103 lab smoke: PASS</code>. The course smoke does
not grade the independent Ember submission.

## Reflection

1. Which bytes select the manifest, and how are those bytes obtained separately
   from the capsule?
2. At what exact point can Ember first retain material payload, and which
   structural checks already completed?
3. Which omission cases are structural, and which real-world undeclared
   dependencies remain unknowable to the manifest?
4. Which variation sources did you control, normalize, or merely record?
5. What can an approved provenance identity establish, and what can it not?
6. Which TCB component would be most valuable to replace with an independent
   implementation, and what comparison would you perform?
7. Which deliberate mutation most directly tested your claimed assurance
   boundary?
8. What additional signing, transparency, revocation, and state-protection
   design would a production replay verifier need?
