# Lab: build and falsify the Kite compiler pipeline

## Goal

Build an independent, bounded compiler pipeline for the pure typed expression
language **Kite**. Specify the source and IR, lower with explicit invariants,
validate and execute both representations, encode and decode a fixed-layout
artifact, and collect evidence for a narrowly stated preservation relation.

This lab practices **PLT-103-01**, **PLT-103-02**, and **PLT-103-03**. Kite is
not Cairn or Orange. A result is complete only when its normal, exact endpoint,
one-beyond, malformed, equivalence, and deliberate-failure evidence agrees with
the written contracts.

## Setup

Read [the lesson](lesson.md), inspect the supplied example, and confirm its
baseline without changing it:

~~~sh
cd curriculum/modules/plt-103
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/ir_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

The final command must print <code>plt-103 lab smoke: PASS</code> and exit zero.
Use Python 3.11 or newer and only its standard library.

Create a fresh temporary workspace and keep every learner-created source,
artifact, and evidence file below it:

~~~sh
workdir="$(mktemp -d)"
cd -- "$workdir"
pwd
python3 --version
~~~

Use <code>PYTHONDONTWRITEBYTECODE=1</code> and <code>python3 -B</code> on every
run. Do not copy, import, rename, or mechanically translate Cairn. Do not use a
network, external package, administrator permission, global configuration, or
repository write.

## Tasks

1. **Specify Kite — PLT-103-01.** Write <code>kite_pipeline.py</code>. Define
   immutable source nodes for <code>Word</code>, <code>Truth</code>,
   <code>Ref</code>, <code>Xor</code>, <code>Equal</code>,
   <code>Pick</code>, and <code>Bind</code>. Words are exact unsigned 16-bit
   values. <code>Xor</code> accepts two words and returns a word;
   <code>Equal</code> accepts two same-typed values and returns truth;
   <code>Pick</code> has a truth condition and same-typed alternatives. Kite is
   pure and eagerly evaluates both alternatives. Bindings use lexical scope
   and nearest-binding shadowing. Accept ASCII identifiers beginning with a
   lowercase letter and continuing with lowercase letters, digits, or
   underscore.
2. **Fix the source envelope before lowering — PLT-103-01.** Limit source
   nodes to 47, root depth to 18, active bindings to 12, and identifier spelling
   to 20 ASCII bytes. Reject an unsupported exact node type, invalid word,
   invalid name, undefined reference, ill-typed operation, and excess source
   bound with immutable diagnostics carrying stable codes and messages. Check
   depth before recursion, nodes before retaining or lowering a node, and
   active bindings before extending the environment. A failure yields no IR or
   artifact.
3. **Define and lower to typed IR — PLT-103-01.** Use instructions
   <code>word_const</code>, <code>truth_const</code>,
   <code>xor_word</code>, <code>equal</code>, and <code>pick</code>. Each
   instruction defines one contiguous register starting at zero and may use
   only smaller registers. Names and bindings emit no instructions. Cap the IR
   at 47 instructions. Write the lowering invariants for environment validity,
   register dominance, type preservation, returned register/type, and every
   resource counter. Explain why eager source <code>Pick</code> permits a
   straight-line IR instruction.
4. **Write independent source and IR evaluators — PLT-103-03.** The source
   reference evaluator must not call the lowerer, IR evaluator, encoder, or
   decoder. The IR evaluator must validate before running and must not call the
   source evaluator. Both return an immutable type/value pair. Implement every
   source form independently; do not define equivalence by having both paths
   call one shared evaluation function.
5. **Validate the IR as untrusted input — PLT-103-02.** Reject a non-program,
   non-tuple instruction collection, non-instruction entry, zero or 48
   instructions, missing/duplicate/non-contiguous destination, forward/self or
   absent register use, unknown opcode/type, operand type mismatch, noncanonical
   unused field, and invalid result register/type. Use a single forward table
   of prior register types and state its loop invariant.
6. **Specify and implement the artifact — PLT-103-02.** Use big-endian bytes.
   The header is exactly 12 bytes: <code>KIR1</code>, one-byte version 1,
   one zero flags byte, two-byte instruction count, two-byte result register,
   one-byte result type, and one reserved zero byte. Every instruction is
   exactly 16 bytes: opcode, result type, destination, three operands, signed
   four-byte immediate field, and a two-byte reserved zero field. Use
   <code>0xffff</code> for unused operands and zero for unused immediates.
   The only valid length is <code>12 + count * 16</code>; the maximum is 764
   bytes. Reject non-bytes, short header, wrong magic/version, unknown codes,
   nonzero flags/reserved/unused fields, count outside 1–47, length mismatch,
   and decoded invalid IR. Decode/re-encode valid artifacts byte-for-byte.
7. **Test exact normal behavior — PLT-103-01, PLT-103-02.** Lower a closed
   expression with nested bindings, shadowing, <code>Xor</code>,
   <code>Equal</code>, and both <code>Pick</code> outcomes. Assert the complete
   instruction sequence, every destination/operand/type/immediate, result
   register/type, source value, IR value, artifact bytes or digest, decoded
   value, and canonical re-encoding. Show that capture-avoiding consistent
   renaming changes source names but not a closed artifact.
8. **Test endpoints and one beyond — PLT-103-03.** Cover word 0/65,535 and
   -1/65,536; identifier 1/20/21 bytes; source depth 18/19; active bindings
   12/13; exactly 47 nodes and instructions; the first structurally possible
   source tree beyond 47; IR count 47/48; artifact length 764 and its truncated
   and trailing variants. Calculate each tree and byte count in comments.
   Ensure a different cap does not accidentally reject an alleged endpoint
   first.
9. **Test invalid and adversarial states — PLT-103-02, PLT-103-03.** Cover
   every source/type/IR/artifact rejection from tasks 2, 5, and 6. Mutate each
   multibyte header field separately to catch wrong byte order. Mutate a prior
   operand into a self-reference, a valid type code into the wrong valid type,
   a sentinel into an out-of-range register, and an unused field into nonzero.
   Assert stable code and message, absent output, and bounded retained data.
10. **Build the equivalence table — PLT-103-03.** Create at least 40 fixed,
    visible, bounded source trees that vary values, Boolean outcomes, nested
    scope, shadowing, both branch types, and all source operators. For every
    well-typed case assert
    <code>source(e) == execute(decode(encode(lower(e))))</code>. Add
    metamorphic cases for alpha-renaming and inserting a dead pure binding.
    Record the exact domain. State that finite agreement is evidence, not a
    proof of preservation.
11. **Prove failure sensitivity — PLT-103-03.** Make three isolated temporary
    mutations: expect the wrong final value, change one expected SSA operand,
    and change one expected big-endian count byte. For each mutation, run only
    its targeted test, preserve stdout, stderr, and the immediate nonzero
    status, restore it, and preserve the zero-status rerun. Do not merely
    describe the failures.
12. **Record the claim envelope.** In <code>evidence.md</code>, record the
    absolute temporary path, Python version, source SHA-256 hashes, exact
    commands, stdout, stderr, and immediate statuses. Justify O(n) lowering,
    O(i) validation/execution/encoding, O(n+i) retained model data, and the
    exact 764-byte artifact cap; label Python interpreter and allocator memory
    outside the exact model. State that evidence covers only the recorded pure
    Kite cases. It proves no universal semantic preservation, optimization,
    machine code, constant-time, safety, security, termination, or Orange
    property.

## Verification

From the temporary workspace, run the complete learner suite:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v \
  >passing.stdout 2>passing.stderr
status=$?
printf 'test status: %s\n' "$status"
sha256sum kite_pipeline.py test_kite_pipeline.py >source.sha256
~~~

Status zero is necessary but not sufficient. Inspect the implementation and
evidence and verify that:

- source, IR, and artifact contracts are separate and complete;
- lowerer counters and IR operands satisfy their stated invariants;
- source and IR evaluation are independent implementations;
- validation occurs again at encode and execute boundaries;
- every exact endpoint and feasible one-beyond case is calculated and reached;
- malformed artifacts fail before unchecked indexing or allocation;
- the 40-case table and both metamorphic relations execute;
- all three mutations visibly fail before their restored passes;
- evidence distinguishes observations, assumptions, and unsupported claims;
  and
- every generated file remains beneath the temporary workspace.

Finally, from the repository module directory, rerun the supplied model as a
separate integrity check:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

## Reflection

Write six to eight sentences answering:

- Which source facts disappear during lowering, and which IR facts replace
  them?
- How does the environment implement scope without load instructions?
- Which condition makes straight-line eager <code>Pick</code> sound for Kite?
- Why must the encoder validate IR it did not create?
- Which invalid byte mutation could otherwise be misread as a valid artifact?
- What does the 40-case table add beyond one worked example?
- What would a universal preservation proof require that this lab lacks?
- Which professional compiler and Orange claims remain unsupported?
