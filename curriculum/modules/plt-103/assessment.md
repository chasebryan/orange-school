# Assessment: independent Mica compiler pipeline

## Instructions

Complete this assessment independently in a fresh temporary directory using
Python 3.11 or newer and only the standard library. Do not copy, import, rename,
or lightly translate Cairn or a Kite solution. **Mica** has a distinct source
model, operation set, bounds, IR names, and artifact format.

Submit the source/IR/artifact specifications, implementation, tests, mutation
outputs, hashes, exact commands, stdout, stderr, immediate statuses, resource
argument, and claim matrix. Generated files must remain under the temporary
directory. Work offline without external packages, privileged operations,
global changes, or writes to the course repository.

## Knowledge check

Answer before writing code:

1. Distinguish a source AST, typed IR, serialized artifact, and machine code.
   Which three does this assessment implement?
2. State one scope invariant, one typing invariant, one SSA definition/use
   invariant, and one resource invariant for lowering.
3. Explain why a frozen instruction can still contain an invalid forward use or
   operand type.
4. Give an example where eagerly lowering both alternatives would not preserve
   the source language's behavior. Why does Mica avoid it?
5. Explain the difference among validation, source interpretation, IR
   execution, encoding, and decoding. Why should the public boundaries not
   trust one another?
6. Derive the byte length for 1, 33, and 55 fixed-width instructions from the
   format below.
7. Contrast a worked example, endpoint, one-beyond, malformed-state,
   metamorphic, equivalence-table, and deliberate-failure test. Name one blind
   spot in each.
8. State what a semantic preservation theorem would need beyond a passing
   finite test table.
9. Explain why this assessment proves no native artifact, optimizer, machine
   instruction, runtime, security, or Orange property.

## Independent task

Create <code>mica_pipeline.py</code>, <code>test_mica_pipeline.py</code>, and
<code>evidence.md</code>.

1. **Source contract — PLT-103-01.** Define immutable exact nodes
   <code>Small(n)</code>, <code>Bit(b)</code>, <code>Use(x)</code>,
   <code>Subtract(a,b)</code>, <code>AtMost(a,b)</code>,
   <code>Decide(c,t,f)</code>, and <code>With(x,v,body)</code>. A small value is
   an exact signed 16-bit integer. Subtraction is checked and fails on overflow.
   <code>AtMost</code> takes two small values and returns bit.
   <code>Decide</code> requires a bit condition and same-typed alternatives.
   Mica is pure and eagerly evaluates the condition and both alternatives.
   <code>With</code> uses lexical nearest-binding scope. Names start with one
   ASCII lowercase letter, continue with lowercase letters or digits, and
   contain no underscore.
2. **Source bounds and diagnostics — PLT-103-01.** Cap source nodes at 55,
   root depth at 21, active bindings at 14, and names at 18 ASCII bytes. Use
   immutable diagnostics with stable codes/messages. Reject wrong exact node,
   literal, Boolean, or name types; invalid name spelling; undefined use;
   ill-typed operations; and excess nodes/depth/bindings. Static and bound
   checks must occur before excess recursion, environment growth, instruction
   retention, or execution. A static or bound failure exposes no partial IR or
   artifact. Signed subtraction overflow is instead the declared runtime
   failure described under independent semantics.
3. **Typed IR and lowering — PLT-103-01.** Define instructions
   <code>small</code>, <code>bit</code>, <code>sub_small</code>,
   <code>at_most</code>, and <code>decide</code>. Each instruction defines one
   contiguous register from zero; operands name only smaller registers. Uses
   and bindings emit nothing. Cap instructions at 55. Specify the exact fields
   used and unused by every opcode. Implement lexical shadowing without a
   mutable global environment. Document entry/exit invariants and show why the
   returned type/register represents the source subtree.
4. **Independent semantics — PLT-103-03.** Implement a source reference
   evaluator and an IR evaluator without sharing evaluation dispatch or
   arithmetic helpers. The source evaluator must not lower; the IR evaluator
   must validate and must not call the source evaluator. Both return immutable
   typed values or matching declared failures. Explain the exact eager rule
   that lets <code>Decide</code> become straight-line IR. A well-typed
   subtraction that overflows may lower and encode, but source and IR execution
   must both fail with the same runtime code and produce no value; its artifact
   is not evidence of successful execution.
5. **IR validation — PLT-103-02.** In one forward pass, reject a wrong program,
   instruction collection, or entry type; count 0 or 56; missing, duplicate,
   or noncontiguous destination; negative, missing, forward, self, or
   out-of-range operand; unknown opcode/type; opcode/result/operand mismatch;
   noncanonical unused field; and invalid result register/type. Validate again
   before both execution and encoding.
6. **Mica artifact — PLT-103-02.** Use a 14-byte big-endian header: magic
   <code>MICA</code> (4), version 2 (1), flags zero (1), instruction count (2),
   result register (2), result type (1), record size 18 (1), and reserved zero
   (2). Each 18-byte record is opcode (1), result type (1), destination (2),
   operand one (2), operand two (2), operand three (2), signed immediate (2),
   source ordinal (2), and reserved zero padding (4). Use <code>0xffff</code> for unused
   operands and zero for other unused fields. Source ordinals are contiguous
   from zero in emitted-instruction order and are artifact evidence, not source
   byte positions. Valid length is <code>14 + count * 18</code>; maximum valid
   length is 1,004 bytes. Reject non-bytes, short header, wrong magic/version,
   flags/reserved/record size, count, unknown codes, invalid unused fields,
   noncontiguous ordinals, length mismatch, or decoded invalid IR. Require
   byte-identical decode/re-encode.
7. **Worked and scope cases — PLT-103-01, PLT-103-02.** Test a hand-traced
   expression containing nested and shadowed <code>With</code>, subtraction,
   comparison, and both typed variants of <code>Decide</code>. Assert every
   source value, instruction field, result, artifact field, byte length, digest,
   decoded value, and re-encoded byte. Show that capture-avoiding alpha-renaming
   preserves the closed artifact and that a deliberately capturing rename does
   not qualify for that relation.
8. **Endpoints and one beyond — PLT-103-03.** Exercise -32,768/32,767 and both
   arithmetic overflows; name 1/18/19 bytes; depth 21/22; active bindings
   14/15; exactly 55 nodes/instructions and the first representable tree beyond;
   IR count 55/56; artifact length 1,004, 1,003, and 1,005; exact maximum legal
   register and a self/forward reference. Show calculations and isolate each
   bound so the intended check fires first.
9. **Invalid and corruption cases — PLT-103-02, PLT-103-03.** Cover every
   source, type, IR, and artifact rejection above. Independently mutate the
   high and low byte of each multibyte count, result-register, operand,
   immediate, and source-ordinal field, and separately mutate the one-byte
   record-size field. Cover unknown and wrong-but-known opcode and
   type codes, sentinel misuse, nonzero unused values, truncation, trailing
   bytes, and reserved fields. Assert exact diagnostic code/message and absent
   executable output.
10. **Equivalence and metamorphic evidence — PLT-103-03.** Use a visible fixed
    table of at least 50 well-typed, closed, in-budget expressions varying
    signed endpoints, comparison outcomes, result types, nesting, shadowing,
    and every operator. Assert
    <code>source(e) == execute(decode(encode(lower(e))))</code>. Separately test
    capture-avoiding alpha-renaming and insertion of a dead pure binding.
    Include matched overflow cases without treating two generic exceptions as
    equal. State the exact tested domain and why it is not universal proof.
11. **Failure sensitivity — PLT-103-03.** Preserve four observed mutation and
    restoration pairs: wrong expected result, wrong expected operand register,
    wrong expected artifact byte order, and a lowerer mutation that swaps
    subtraction operands. Each targeted mutation must produce an immediate
    nonzero status; each restoration must produce zero. Record both channels
    and do not weaken or skip a test to recover.
12. **Reproducibility, resources, and non-claims.** Record the absolute
    temporary path, Python version, source hashes, exact commands, channels,
    immediate statuses, and a matrix separating specification, observation,
    inference, and unsupported claim. Justify O(n) source work, O(i) IR/artifact
    work, O(n+i) retained model data, and the exact 1,004-byte cap. Python
    runtime/allocator overhead is outside the exact model. State that Mica is
    independent courseware and supports no universal preservation, optimizer,
    native code, ABI, performance, constant-time, safety, security, termination,
    or Orange conclusion.

## Completion criteria

Use [the rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. A complete submission must:

- specify, type, bound, and lower Mica with explicit invariants for
  **PLT-103-01**;
- validate, encode, decode, canonicalize, and execute the fixed artifact for
  **PLT-103-02**;
- provide exact endpoint, one-beyond, malformed, 50-case equivalence,
  metamorphic, and four observed deliberate-failure/restoration pairs for
  **PLT-103-03**;
- preserve enough commands, hashes, channels, statuses, and calculations for
  an assessor to reproduce every claim; and
- limit conclusions to the exact pure Mica model and recorded evidence.
