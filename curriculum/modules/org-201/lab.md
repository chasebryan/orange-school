# Lab: establish the S3a typed-value boundary

## Goal

Build the exact Orange S3a revision from an immutable Git archive, exercise
accepted and rejected typed closed specifications, predict exact reference
values, and produce an evidence statement that stays inside the implemented
boundary.

## Setup

Work from the Orange School repository root. The source Orange repository must
contain the pinned commit object, but its checkout may remain on any branch.
Archive the commit into a disposable directory so the build does not write to
the source repository:

```bash
export ORANGE_REPO="${ORANGE_REPO:-../orange}"
ORANGE_REV="ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6"

test "$(git -C "$ORANGE_REPO" rev-parse "$ORANGE_REV^{commit}")" = "$ORANGE_REV"
S3A_ROOT="$(mktemp -d)"
git -C "$ORANGE_REPO" archive "$ORANGE_REV" | tar -x -C "$S3A_ROOT"

cargo +1.96.1 build --quiet --locked --offline \
  --manifest-path "$S3A_ROOT/compiler/Cargo.toml" \
  -p orangec
ORANGEC="$S3A_ROOT/compiler/target/debug/orangec"
test -x "$ORANGEC"
```

Record `ORANGE_REV`, the resolved commit, `"$ORANGEC" --version`, and the
archive/build commands. Keep all generated source, stream, and status evidence
under `"$S3A_ROOT/lab"`, not in either repository:

```bash
mkdir -p "$S3A_ROOT/lab"
```

## Tasks

1. Before running the compiler, make a prediction table for the catalog cases:
   command, status, complete standard output or an emptiness assertion, and
   first stable standard-error code or an emptiness assertion.

2. Check and evaluate the accepted source, preserving both streams separately:

   ```bash
   accepted="$(pwd -P)/curriculum/modules/org-201/examples/typed-values.or"
   expected="$(pwd -P)/curriculum/modules/org-201/examples/typed-values.stdout"

   "$ORANGEC" check "$accepted" \
     >"$S3A_ROOT/lab/check.stdout" \
     2>"$S3A_ROOT/lab/check.stderr"
   check_status="$?"
   test "$check_status" -eq 0
   test ! -s "$S3A_ROOT/lab/check.stdout"
   test ! -s "$S3A_ROOT/lab/check.stderr"

   "$ORANGEC" eval "$accepted" \
     >"$S3A_ROOT/lab/eval.stdout" \
     2>"$S3A_ROOT/lab/eval.stderr"
   eval_status="$?"
   test "$eval_status" -eq 0
   cmp "$expected" "$S3A_ROOT/lab/eval.stdout"
   test ! -s "$S3A_ROOT/lab/eval.stderr"
   ```

   Annotate each value line with its source declaration. Explain why
   `shared` and `placeholder` produce no lines and why the two declarations
   named `shared` do not collide.

3. Test same-kind uniqueness. Predict the first code, then run:

   ```bash
   duplicate="$(pwd -P)/curriculum/modules/org-201/examples/duplicate-spec.or"
   "$ORANGEC" check "$duplicate" \
     >"$S3A_ROOT/lab/duplicate.stdout" \
     2>"$S3A_ROOT/lab/duplicate.stderr"
   duplicate_status="$?"
   test "$duplicate_status" -eq 1
   test ! -s "$S3A_ROOT/lab/duplicate.stdout"
   grep -F 'error[ORC0201]' "$S3A_ROOT/lab/duplicate.stderr"
   ```

   Create a fresh source that instead repeats an `impl` name and confirm the
   same code. Then change one declaration to `spec`, predict again, and confirm
   that `check` becomes silent with status `0`. Do not claim that the
   cross-kind declarations link.

4. Test the signedness boundary, including the deliberately surprising
   negative-zero case:

   ```bash
   negative="$(pwd -P)/curriculum/modules/org-201/examples/negative-word.or"
   "$ORANGEC" check "$negative" \
     >"$S3A_ROOT/lab/negative.stdout" \
     2>"$S3A_ROOT/lab/negative.stderr"
   negative_status="$?"
   test "$negative_status" -eq 1
   test ! -s "$S3A_ROOT/lab/negative.stdout"
   grep -F 'error[ORC0206]' "$S3A_ROOT/lab/negative.stderr"
   ```

   In a separate fresh source, change only the type to `Int`. Confirm silent
   `check` success and an `eval` line ending in `Int = 0`.

5. Demonstrate all-or-nothing evaluation:

   ```bash
   bounded="$(pwd -P)/curriculum/modules/org-201/examples/eval-no-partial.or"
   "$ORANGEC" eval "$bounded" \
     >"$S3A_ROOT/lab/bounded.stdout" \
     2>"$S3A_ROOT/lab/bounded.stderr"
   bounded_status="$?"
   test "$bounded_status" -eq 1
   test ! -s "$S3A_ROOT/lab/bounded.stdout"
   grep -F 'error[ORC0207]' "$S3A_ROOT/lab/bounded.stderr"
   ```

   Explain why neither the valid `before` nor the valid `after` declaration
   appears on standard output.

6. Under `"$S3A_ROOT/lab"`, author small independent sources for each row and
   fill in the result before running it:

   | Boundary | Required case |
   | --- | --- |
   | exact type | unsupported identifier such as `Byte` |
   | exact width | `Word[08]` or `Word[16]` |
   | lower endpoint | `Word[8] { 0 }` |
   | upper endpoint | `Word[8] { 255 }` |
   | first rejected value | `Word[8] { 256 }` |
   | normalized integer | negative hexadecimal or binary `Int` |
   | empty Core | only empty `spec` and `impl` declarations |

   Preserve the command, streams, status, and first stable code. Exact accepted
   `Word[8]` value lines must use two lowercase hexadecimal digits. Empty-Core
   `eval` must return `0` and write zero bytes on both streams.

7. Create a source with at least four accepted typed specifications, mixed
   radices, and empty declarations between them. Predict every value line in
   order, run `eval`, and compare expected and actual output byte for byte.
   Reordering a typed declaration must reorder only its corresponding output
   line; do not make a cross-revision ID claim.

8. Write a claim matrix with these rows:

   - exact source and compiler revision;
   - lexical, syntactic, and S3a semantic acceptance;
   - normalized reference value and source order;
   - callable function behavior and implementation value;
   - spec-to-impl relationship;
   - refinement or proof result;
   - canonical Core or stable artifact identity;
   - generated code or target behavior; and
   - security, compatibility, release, and production support.

   Mark each as supported, contradicted, or not tested by the evidence and give
   one sentence of justification.

## Verification

The lab passes when the evidence shows:

- an immutable archive resolved to
  `ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`, with all build output outside
  the Orange source repository;
- silent status `0` for accepted `check` and exact source-ordered `eval` output;
- separate same-kind rejection and cross-kind acceptance evidence;
- `ORC0203`, `ORC0204`, `ORC0206`, and `ORC0207` at their exact boundaries;
- normalized `Int`, two-digit lowercase hexadecimal `Word[8]`, and empty-Core
  output behavior;
- empty standard output on rejected `eval`, including a valid declaration
  before the error; and
- an explicit claim boundary excluding every unsupported item in task 8.

## Reflection

Why is exact output prediction stronger evidence than merely observing status
`0`? Give one defect the endpoint and normalization cases could expose. Then
name one semantic-correctness or proof claim that the complete lab still cannot
establish and explain what additional independent evidence it would need.
