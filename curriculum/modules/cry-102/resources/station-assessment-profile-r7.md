# Station assessment profile r7

This is a fictional, case-specific assessment input. It is complete for the
assigned design exercise but is not an organizational standard, deployment
approval, universal cryptographic recommendation, FIPS module claim, or
substitute for reviewing current algorithm and protocol limits.

## Fixed selections

- Profile ID: `station-assessment-profile-r7`
- Record construction identifier: `AES-256-GCM`
- Record key size: 256 bits
- Nonce size: 96 bits, unique for every record under one record key
- Full tag size: 128 bits
- Opening policy: authenticate before parsing or releasing any plaintext; all
  authentication failures return one public rejection class
- High-entropy key derivation identifier: `HKDF-SHA256`
- Audit authentication identifier: `HMAC-SHA256`, full 256-bit tag
- Password-verifier review identifier: `PBKDF2-HMAC-SHA256`
- Password salt: unique per verifier and at least 16 bytes
- Password parameter authority: `station-security-review-board-r7`
- Required benchmark record: `station-password-benchmark-2026-06-r7`

These names select the fictional case. A learner must still identify the
primary specification for each algorithm and the maintained production library,
module, platform, and operational evidence that an actual deployment would
need.

## Key purposes and domain labels

Three distinct key purposes are required:

1. `sensor-record-aead-key`
2. `audit-envelope-hmac-key`
3. `operator-password-verifier-output`

The first two may be separate labeled outputs from approved high-entropy input;
the password-derived output is never an input to that general derivation tree.

The exact ASCII domain labels are:

- AEAD AAD: `station-r7/sensor-record/aad/v1`
- record-key HKDF `info`: `station-r7/sensor-record/key/v1`
- audit-key HKDF `info`: `station-r7/audit-envelope/key/v1`
- audit HMAC input: `station-r7/audit-envelope/input/v1`

Labels are compared as exact bytes. They are not case-folded, Unicode-
normalized, trimmed, or inferred from prose.

## Canonical record AAD

The AAD is the following concatenation in this exact order:

~~~text
u16be(len(aad_domain)) || aad_domain ASCII bytes
u16be(len(station_id)) || station_id ASCII bytes
u32be(writer_id)
u16be(schema_version)
u16be(record_type)
u64be(batch_sequence)
u16be(len(key_id)) || key_id ASCII bytes
~~~

Constraints:

- `station_id` and `key_id` are 1 through 32 bytes and match
  `[A-Za-z0-9][A-Za-z0-9._-]*`;
- `writer_id` is an exact integer from 1 through `2^32-1` and is durably unique
  for the lifetime of one record key;
- `schema_version` and `record_type` are exact integers from 1 through 65,535;
- `batch_sequence` is an exact integer from 0 through `2^64-1`; and
- decoders reject truncation, trailing bytes, non-canonical lengths, unknown
  versions, unknown record types, and values outside these ranges.

The visible envelope uses the same field values. A parser must compare the
authenticated canonical fields with any routing copy and reject disagreement.

## Nonce, message, replay, and rotation limits

The 96-bit nonce is:

~~~text
u32be(writer_id) || u64be(writer_counter)
~~~

Each writer reserves non-overlapping counter intervals in authenticated durable
state before use. Counter state is scoped to the exact record key ID and cannot
be restored, cloned, or rolled back under that key. Writer counters begin at 0.

This fictional profile permits at most `2^10` (1,024) records per writer under
one key, so the maximum permitted counter is `2^10-1` (1,023). Exactly three
writer IDs are assigned, giving an assessment-profile aggregate cap of
`3 * 2^10` (3,072) records per record key. Each plaintext is at most 65,536
bytes, or 4,096 16-byte blocks. The plaintext contribution is therefore at most
`2^22` blocks per writer and `3 * 2^22` blocks across the three writers before
counting AAD and construction bookkeeping.

This deliberately low exercise cap forces early rotation and makes the budget
calculation reviewable. It is not an assertion that reaching the cap is safe.
The learner must include AAD and all construction-specific terms, compare the
result with the governing standard/profile and required forgery target, and
preserve a deployment blocker until the current authority and chosen
implementation approve an equal or lower bound.

Rotation is mandatory before a writer would exceed its counter cap, when an
interval cannot be durably reserved, after rollback or clone detection, on key
exposure, or when the profile/version changes. The old key and replay state
remain available only for the explicitly approved receive window; senders may
not fall back to it.

Replay state is owned by `station-record-ingress-r7`. It authenticates a record
first, then checks `(key_id, writer_id, batch_sequence)` against durable state.
Duplicate, stale, rolled-back, unknown-version, and out-of-window records are
rejected without legacy fallback.

## Audit envelope input

The audit HMAC input is the exact ASCII audit domain label framed with `u16be`
length, followed by the canonical record AAD, followed by a 32-byte SHA-256
digest of the visible audit payload. It uses only the distinct audit HMAC key.
The audit mechanism authenticates among holders of that key; it is not a
digital signature or non-repudiation evidence.

## Source and approval boundary

The record/rekey/message caps above have source
`station-assessment-profile-r7 fictional operational limits`. They are not
attributed to NIST or an RFC. The assessment requires learners to cite the
actual algorithm sources separately and to stop before production until a
current authority reviews algorithm status, quantitative use bounds, the
chosen library/module, platform behavior, key custody, nonce durability,
password benchmarking, side channels, recovery, and incident response.
