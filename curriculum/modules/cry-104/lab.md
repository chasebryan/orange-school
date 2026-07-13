# Lab: build a replayable standards evidence chain

## Goal

Turn exact standards-source identities into atomic requirements, verify a
bounded local vector artifact before executing it, demonstrate failure
sensitivity, and write only the claim supported by the resulting evidence.

## Setup

From the repository root, run the supplied baseline:

~~~sh
cd curriculum/modules/cry-104
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 examples/vector_worked.py
baseline_status=$?
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
smoke_status=$?
printf 'baseline=%s smoke=%s\n' "$baseline_status" "$smoke_status"
~~~

The smoke command must print <code>cry-104 lab smoke: PASS</code> and both
statuses must be 0.

Create an isolated workspace and copy only the supplied example directory:

~~~sh
workdir="$(mktemp -d)"
cp -R examples "$workdir/"
cd -- "$workdir"
pwd
~~~

Keep all learner-created evidence under the printed directory. The lesson and
local files contain the required facts. Do not fetch or install anything.

## Tasks

1. **Create <code>source-record.md</code>.** Record FIPS 180-4's publisher,
   title, publication state and date, stable publication-page URL, the revision
   planning note as a separate fact, and the SHA-256 scope used here. Add the
   NIST CAVP Secure Hashing page, retrieval date, vector format description,
   and its limitation on informal vector use. Add RFC 8174's series/status,
   date, and capitalization rule. Add the RFC Editor errata status vocabulary
   and an “observed as of” date. Distinguish algorithm definition, selection
   profile, vectors, algorithm validation, and module validation.
2. **Create <code>requirements.csv</code>.** Use columns
   <code>id,source,location,subject,precondition,requirement,failure,evidence,open_question</code>.
   Extract at least eight atomic requirements for the course vector workflow:
   exact algorithm, byte-oriented input, hex decoding, digest width, source
   identity, artifact digest, no skipped cases, and nonzero failure. Map each
   to a stable source or an explicitly labeled course-harness requirement. Do
   not label a course policy as a NIST requirement.
3. **Audit provenance.** Explain every field in
   <code>examples/provenance.json</code>. Independently calculate the vector
   file's SHA-256 with Python or <code>sha256sum</code>, record the exact command
   and compare it byte-for-byte with the manifest. Identify the trust root and
   explain why the adjacent manifest is not independent authentication.
4. **Preserve a provenance failure.** Copy the pristine files to
   <code>case-provenance-fail/</code>, change exactly one vector-file byte, and
   run the harness without changing the manifest. Preserve command, stdout,
   stderr, and immediate nonzero status. State which link failed before vector
   execution.
5. **Preserve a vector failure after provenance succeeds.** In a separate copy,
   replace exactly one expected digest with 64 zeroes and update the manifest
   to the new vector-file digest. Run provenance and vectors. Preserve the one
   failed case and nonzero overall result. Explain why matching provenance did
   not make the changed expectation correct.
6. **Add strict negative tests.** In <code>test_evidence.py</code>, import the
   supplied harness and test duplicate JSON keys, duplicate vector IDs, an
   absolute path, parent traversal, uppercase hex, odd hex, a 31-byte expected
   digest, empty vectors, 1,001 vectors, an unknown field, a wrong artifact
   digest, and one valid single-vector boundary. Every invalid case must raise
   <code>ValueError</code>. Deliberately weaken one assertion, preserve a
   failing run, restore it, and preserve the passing run.
7. **Write <code>claim-ledger.md</code>.** Record exact environment, source and
   local artifact identities, commands, directories, channels, statuses,
   vector counts, failures, and skipped count. Write one supported observed
   claim and one supported regression claim. Reject at least six unsupported
   claims involving proof, complete conformance, side channels, CAVP/CMVP,
   source authentication, or deployment safety. Explain what evidence would
   be needed to strengthen each rejected claim.

## Verification

From the isolated workspace run:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v
test_status=$?
printf 'test status: %s\n' "$test_status"
~~~

Status 0 is necessary but not sufficient. Inspect the submission and confirm:

- source identities, statuses, updates, retrieval dates, and roles are not
  conflated;
- every requirement is atomic and has a stable source/location or explicit
  course-policy label;
- the pristine artifact digest matches and both deliberate changes are
  retained as distinct failures;
- the loader rejects ambiguity before execution and never reports zero cases
  as success;
- all vector results identify their case and actual digest;
- stdout, stderr, and immediate statuses are retained separately; and
- the final claim remains at observed/regression level.

Rerun the repository smoke check independently. Do not replace the retained
failure artifacts with the restored passing copy.

## Reflection

Write five to seven sentences:

- Which source defined the algorithm and which source characterized vector
  use?
- What did the content digest prove, and what did it leave unauthenticated?
- Why did the second mutation pass provenance but fail vector execution?
- How did an erratum's status affect whether you treated it as a correction?
- Which unsupported claim was most tempting after a green run?
- What new evidence would be needed before making that claim?
