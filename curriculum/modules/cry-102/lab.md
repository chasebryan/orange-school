# Lab: audit a symmetric-protection profile without inventing cryptography

## Goal

Classify cryptographic services, exercise bounded one-way standard-library
mechanics with public data, build a fail-closed validator for non-secret
protocol metadata, and analyze nonce, tag, AAD, domain, key-separation, password
KDF, and composition failures. The deliverable is a review package, not an
encryption implementation.

## Setup

From the repository root, inspect and run the supplied evidence:

~~~sh
cd curriculum/modules/cry-102
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 examples/worked_review.py
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
~~~

The last command must print `cry-102 lab smoke: PASS` and exit 0. Read
[`crypto_mechanics.py`](examples/crypto_mechanics.py) and
[`protocol_manifest.py`](examples/protocol_manifest.py). Identify every input
bound, the exact metadata fields, and each explicit statement about what the
examples do not establish.

Create a separate learner workspace:

~~~sh
workdir="$(mktemp -d)"
cd -- "$workdir"
pwd
python3 --version
~~~

Keep all learner-created files beneath the printed directory. Use Python 3.11
or newer and only its standard library. Use public fixed test bytes, not a real
password, key, token, user record, or production configuration. Do not make a
network request, install a package, alter global configuration, or implement a
cipher, block mode, stream cipher, padding construction, or AEAD.

The case study is an offline warehouse application with three independent
purposes:

- protect inventory records with authenticated encryption;
- authenticate visible audit events with a separate MAC key; and
- store local operator password verifiers under a deployment-owned password
  profile.

For this lab only, a fictional organizational review sheet named
`warehouse-training-profile-v2` lists AES-256-GCM, a 256-bit key, 96-bit nonce,
128-bit tag, unique-per-key counter allocation, reject-before-plaintext
opening, HKDF-SHA-256 for high-entropy shared-secret input, full-length
HMAC-SHA-256 for audit records, and PBKDF2-HMAC-SHA-256 with cost selected and
versioned by deployment security policy. Treat that sheet as scenario input,
not universal or production approval.

## Tasks

1. **Build a service and value map — CRY-102-01.** Create
   `service-map.md`. For record confidentiality, record integrity, visible
   header binding, audit-event authentication, password-guess cost, key
   derivation, and replay rejection, record:

   - the exact claim and attacker capability;
   - the responsible primitive or protocol state;
   - its inputs and output;
   - one assumption and one exclusion; and
   - one superficially similar mechanism that does not satisfy the claim.

   Add a second table distinguishing secret key, password, salt, nonce, AAD,
   digest, MAC tag, AEAD tag, key identifier, domain label, ciphertext, and
   replay counter. State whether each is normally secret, unique, unpredictable,
   authenticated, encrypted, or deployment-profile dependent. Do not mark a
   nonce or password salt as a secret.
2. **Exercise standardized one-way APIs — CRY-102-03.** Create
   `mechanics.py` using only `hashlib` and `hmac`. Implement bounded functions
   that:

   - compute a SHA-256 digest for an exact `bytes` input of at most 262,144
     bytes;
   - compute and verify a full HMAC-SHA-256 tag for a 16-through-64-byte public
     test key and bounded message, using `hmac.compare_digest` for verification;
   - derive 16 through 48 bytes with `hashlib.pbkdf2_hmac("sha256", ...)` from
     exact byte inputs, a 16-through-32-byte salt, and a lab-only iteration
     count from 1 through 20,000; and
   - reject Boolean counts, text where bytes are required, empty lab passwords,
     out-of-range values, and malformed HMAC tags.

   Name the PBKDF2 constants `LAB_ONLY_MIN_ITERATIONS` and
   `LAB_ONLY_MAX_ITERATIONS`. Put a module docstring above them stating that the
   interval is for fast offline checks and is not a production parameter
   recommendation. Never print an input or derived byte string.
3. **Test normal, endpoint, and invalid mechanics.** Create
   `test_mechanics.py` with `unittest`. Pin the SHA-256 `abc` vector and RFC
   4231 HMAC-SHA-256 test case 1. Cover empty and maximum hash messages; minimum
   and maximum HMAC key sizes; both salt, iteration, and output-length
   endpoints; changed message; changed, short, and long tags; wrong input
   types; Boolean and out-of-range counts; and an empty password. Include one
   fixed PBKDF2 regression value generated from labels explicitly named public
   test data. State that the regression checks parameters and API behavior, not
   password security.
4. **Specify a metadata-only manifest — CRY-102-02 and CRY-102-04.** Create
   `warehouse-manifest.json` and `manifest_contract.md`. The JSON must contain
   no key, password, verifier, plaintext, ciphertext, nonce value, or tag. It
   must record:

   - schema and fictional profile versions;
   - exact AEAD algorithm, key size, nonce size, tag size, allocation rule,
     AAD-domain reference, record-key reference, and failure policy;
   - exact HKDF algorithm, high-entropy source kind, salt rule, `info`-domain
     reference, and output-key reference;
   - exact audit MAC algorithm, full tag size, input-domain reference,
     audit-key reference, and rejection policy;
   - password KDF algorithm, salt minimum, parameter authority, cost-version
     field, and verifier-key label; and
   - three distinct key labels and three distinct domain labels.

   In `manifest_contract.md`, classify every field as algorithm identifier,
   parameter, protocol binding, lifecycle rule, or failure rule. For each
   algorithm name, identify the scenario authority that allowed it and the
   primary standard that defines it. Explain why neither the JSON nor its
   validator proves algorithm correctness, compliance, side-channel safety, or
   deployability.
5. **Implement a fail-closed manifest validator — CRY-102-04.** Create
   `validate_manifest.py` and `test_manifest.py`. The validator must accept a
   parsed mapping, return all deterministic errors, require exact field sets
   and types, and enforce the fictional profile. It must reject:

   - an unknown or homemade algorithm name;
   - nonce size other than 12 bytes or a rule weaker than unique per key;
   - tag size other than 16 bytes for AEAD or 32 bytes for HMAC;
   - plaintext release before authentication;
   - an HKDF source labeled as a password;
   - duplicate or malformed domain labels;
   - one key label assigned to two purposes;
   - missing parameter authority or cost-profile version; and
   - any extra field, including one named `key_material`, `password`, or
     `nonce_value`.

   Start from one valid fixture. Deep-copy and mutate one invariant per negative
   test so the failure cause is observable. Include wrong container and Boolean
   numeric cases. Do not read environment variables or external files in the
   validator.
6. **Design nonce, AAD, and replay state — CRY-102-02.** Create
   `record-state.md` for two concurrent warehouse writers. Define a disjoint
   nonce allocation that remains unique per record key across restart, crash,
   clone, backup restore, and counter exhaustion. Define the exact canonical
   fields and encoding placed in AAD, including schema version, writer identity,
   sequence, and record type. State the rejection rule for unknown versions.

   Separately define replay state. Explain why a replayed record can have a
   valid AEAD tag, how the receiver detects it, which authenticated field binds
   the replay decision, and what happens if durable replay state rolls back.
   Quantify the counter capacity and state when rotation must occur. You are
   specifying the state machine, not writing encryption code.
7. **Run a failure and composition review — CRY-102-02.** Create
   `failure-review.md` with one row for each of these mutations:

   - repeated AEAD nonce under one key;
   - same nonce under a distinct newly generated key;
   - ciphertext bit change;
   - visible header change without an AAD update;
   - correct ciphertext with wrong AAD, key, nonce, or tag;
   - valid old record replay;
   - same key label used for record AEAD and audit HMAC;
   - same domain label used for HKDF `info` and HMAC input;
   - two password records sharing a salt;
   - HKDF applied directly to a human password; and
   - plaintext returned before tag verification.

   For each, state the violated invariant, expected safe behavior, externally
   visible error class, allowed non-sensitive evidence, and remediation. Mark
   the replay row as protocol-state failure rather than AEAD tag failure. Mark
   same nonce under a genuinely different key as outside the same-key reuse
   event while still requiring the profile's allocation and lifecycle review.
8. **Write the production handoff — CRY-102-04.** Create `handoff.md` listing
   the decisions this lab cannot make: current organizational approval,
   maintained library and version, validated-module requirements, platform and
   side-channel review, random source, key store, erasure limits, nonce-state
   durability, real password profile and benchmark, message/rekey limits,
   canonical serialization, replay persistence, monitoring, incident response,
   dependency updates, and interoperability tests. For every item, name an
   owner, required evidence, and stop condition. Explicitly say that no lab
   code may be copied as an encryption or password-storage subsystem.

## Verification

From the temporary learner workspace, run:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v
test_status=$?
PYTHONDONTWRITEBYTECODE=1 python3 validate_manifest.py warehouse-manifest.json
manifest_status=$?
printf 'test status: %s\nmanifest status: %s\n' "$test_status" "$manifest_status"
~~~

The validator CLI may load only the named local JSON file, print a deterministic
accept/reject result, and return nonzero on rejection. Preserve Python version,
absolute workspace, exact commands, stdout, stderr, and immediate statuses in
`evidence.md`.

Then make one copy of the valid manifest in the temporary workspace, change its
AEAD failure policy to return plaintext before authentication, and show that the
validator exits nonzero. Restore the valid input and show it exits zero. Do the
same with one deliberate wrong expected HMAC vector: preserve the failing test,
restore the vector, and preserve the passing run.

Status zero is necessary but not sufficient. Inspect the artifacts and confirm:

- every claim maps to the correct service and its limits;
- no executable file implements encryption, AEAD, HKDF, or a home-grown mode;
- every executable input is bounded and every negative test is failure-sensitive;
- nonce allocation handles concurrency and durable rollback explicitly;
- AAD and domain labels have exact encodings and versions;
- AEAD failure releases no plaintext and replay is handled separately;
- key labels and domains remain distinct by purpose;
- lab PBKDF2 bounds are never called a production profile; and
- the handoff assigns every unresolved production decision.

Finally, rerun the unchanged repository smoke check from the module directory.
That separates repository example evidence from learner-workspace evidence.

## Reflection

Write six to eight sentences addressing all of these questions:

- Which two values were easiest to confuse, and what invariant distinguishes
  them?
- What state, rather than primitive math, makes nonce uniqueness difficult?
- Why can authenticated decryption fail safely while replay still succeeds
  cryptographically?
- Why does a distinct domain label not automatically authorize reuse of one
  key across algorithms?
- What does the PBKDF2 regression prove, and what does it leave unproved about
  password defense?
- Which production handoff stop condition would you verify first, and why?
