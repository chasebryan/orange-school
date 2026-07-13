# Lab: test the complete Orange 2026 grammar and phase boundary

## Goal

Exercise every implemented grammar alternative at the canonical revision,
distinguish parser rejection from semantic rejection, and produce correctly
scoped evidence for current `orangec check` behavior.

## Setup

Work from the Orange School repository root. Use a local Orange Git object
provider, but archive the exact commit into a disposable directory so neither
the checkout nor its build tree is changed:

```bash
export ORANGE_REPO="${ORANGE_REPO:-../orange}"
ORANGE_REV="ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6"

test "$(git -C "$ORANGE_REPO" rev-parse "$ORANGE_REV^{commit}")" = "$ORANGE_REV"
LAB_ROOT="$(mktemp -d)"
git -C "$ORANGE_REPO" archive "$ORANGE_REV" | tar -x -C "$LAB_ROOT"

cargo +1.96.1 build --quiet --locked --offline \
  --manifest-path "$LAB_ROOT/compiler/Cargo.toml" \
  -p orangec --target-dir "$LAB_ROOT/target"
ORANGEC="$LAB_ROOT/target/debug/orangec"
test -x "$ORANGEC"
mkdir -p "$LAB_ROOT/cases" "$LAB_ROOT/results"
```

Record the resolved commit, compiler version, archive command, and build
command. Generated sources and evidence belong under `"$LAB_ROOT"`.

## Tasks

1. From memory, write the eight grammar productions. Mark the declaration-list
   repetition, both `spec` tails, the one optional width, and the one optional
   sign. Compare with the normative grammar only after completing the attempt.

2. Predict the phase, status, standard-output condition, and first diagnostic
   code for each catalog example. Run the cross-kind accepted case:

   ```bash
   functions="$(pwd -P)/curriculum/modules/org-103/examples/functions.or"
   "$ORANGEC" check "$functions" \
     >"$LAB_ROOT/results/functions.stdout" \
     2>"$LAB_ROOT/results/functions.stderr"
   functions_status="$?"
   test "$functions_status" -eq 0
   test ! -s "$LAB_ROOT/results/functions.stdout"
   test ! -s "$LAB_ROOT/results/functions.stderr"
   ```

   Explain why the same-spelled `spec` and `impl` pass semantic uniqueness but
   neither link nor gain a value.

3. Show that each existing negative case lexes, then demonstrate its distinct
   parser boundary:

   ```bash
   reserved="$(pwd -P)/curriculum/modules/org-103/examples/reserved-declaration.or"
   trailing="$(pwd -P)/curriculum/modules/org-103/examples/trailing-syntax.or"
   "$ORANGEC" lex "$reserved" >"$LAB_ROOT/results/reserved.tokens"
   "$ORANGEC" lex "$trailing" >"$LAB_ROOT/results/trailing.tokens"

   "$ORANGEC" check "$reserved" \
     >"$LAB_ROOT/results/reserved.stdout" \
     2>"$LAB_ROOT/results/reserved.stderr"
   reserved_status="$?"
   test "$reserved_status" -eq 1
   test ! -s "$LAB_ROOT/results/reserved.stdout"
   grep -F 'error[ORC0103]' "$LAB_ROOT/results/reserved.stderr"

   "$ORANGEC" check "$trailing" \
     >"$LAB_ROOT/results/trailing.stdout" \
     2>"$LAB_ROOT/results/trailing.stderr"
   trailing_status="$?"
   test "$trailing_status" -eq 1
   test ! -s "$LAB_ROOT/results/trailing.stdout"
   grep -F 'error[ORC0104]' "$LAB_ROOT/results/trailing.stderr"
   ```

   State why neither parser failure reaches semantic analysis.

4. Author one accepted source containing an empty module, one containing both
   empty declaration kinds, and one containing all of these typed tails:
   widthless type, bracketed-width type, positive integer, negative integer,
   and mixed binary, decimal, and hexadecimal magnitudes. Use only exact
   semantically supported types so `check` is silent. Predict before running.

5. Isolate syntax containers from semantic support. Create each source below
   under `"$LAB_ROOT/cases"`, predict its phase, then capture both streams and
   status separately:

   - `spec value() -> Byte { 1 }`;
   - `spec value() -> Word[08] { 1 }`;
   - `spec value() -> Word[8] { -0 }`; and
   - `spec value() -> Word[8] { 256 }`.

   The declarations all match the grammar. Their expected semantic codes are,
   in order, `ORC0203`, `ORC0204`, `ORC0206`, and `ORC0207`. Explain why these
   results support a phase observation but not acceptance of the source or a
   proof that the parser is correct.

6. Create and check a typed implementation:

   ```orange
   edition 2026;
   module rejected {
     impl value() -> Int { 1 }
   }
   ```

   Confirm status `1`, empty standard output, and `ORC0101`. Explain why this is
   a parser rejection rather than the internal semantic `ORC0202` defense.

7. Demonstrate the duplicate-name phase distinction with three fresh cases:

   - two `spec` declarations with the same name, one empty and one typed;
   - two empty `impl` declarations with the same name; and
   - a `spec` and `impl` with the same name in the opposite order from the
     catalog example.

   Predict all results. The first two are syntactically valid but fail semantic
   analysis with `ORC0201`; the third passes silently. Do not describe the
   cross-kind pair as matched or linked.

8. Make a boundary table for: missing edition semicolon, alternate edition
   spelling, reserved module name, function parameter, missing typed literal,
   two typed literals, semicolon inside the typed body, nonempty legacy body,
   declaration beginning with `claim`, typed `impl`, and second module. Predict
   lexical validity, parser result, and first stable code. Run at least five
   cases spanning different productions.

9. Repeat one accepted, one parser-rejected, and one semantic-rejected command.
   Compare status and both complete streams byte for byte. Finish with a claim
   matrix distinguishing tokenization, parsing, semantic acceptance, Core
   construction, reference evaluation, implementation execution, proof or
   refinement, code generation, and cryptographic correctness.

## Verification

The lab passes when the evidence shows:

- the complete eight-production additive grammar at exact revision
  `ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`;
- silent `check` status `0` for legacy and typed accepted sources;
- `ORC0103`, `ORC0104`, and typed-`impl` `ORC0101` parser boundaries;
- parsed-but-unsupported type, width, signedness, and range cases reaching the
  expected `ORC02xx` semantic boundaries;
- same-kind duplicate semantic rejection and cross-kind acceptance;
- identical repeated statuses and streams for identical inputs; and
- no claim that parsing is semantic validation or that full `check` success is
  evaluation, implementation execution, proof, code generation, security, or
  cryptographic correctness.

## Reflection

Why does a phase-labelled negative suite reveal more than a list of rejected
files? Describe one parser defect and one semantic-routing defect this lab could
expose. Then identify one parser- or semantic-correctness theorem the same
evidence still cannot establish.
