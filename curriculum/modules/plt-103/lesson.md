# IRs, lowering, code generation, and preservation

A compiler pipeline changes representation. Each change can make later work
simpler, but it can also lose meaning, invent behavior, or produce ambiguous
bytes. Professional compiler work therefore needs explicit contracts at every
boundary: source meaning, IR invariants, lowering obligations, artifact layout,
and evidence relating executions.

This module uses **Cairn**, a deliberately small pure expression language, and
Python 3.11's standard library. Cairn is independent courseware. Its source
AST, IR, artifact, and tests do not define, implement, emulate, or predict
Orange behavior.

## Learning objectives

- **PLT-103-01:** Specify a typed IR and lower a bounded source AST while
  preserving explicit scope, type, single-assignment, and resource invariants.
- **PLT-103-02:** Validate, serialize, decode, and execute a deterministic
  bounded artifact with use-before-definition and exact-layout checks.
- **PLT-103-03:** Establish scoped source-versus-IR equivalence evidence across
  normal, endpoint, one-beyond, invalid, metamorphic, and deliberate-failure
  cases without overstating proof or Orange capability.

## Prerequisites

Pass <code>plt-102</code> and <code>sys-101</code>. You should be able to trace
lexical scope, state a typing judgment, distinguish pure evaluation from an
effect, reason about fixed-width integers and byte order, and test exact
representation boundaries. The supplied evidence uses Python 3.11 or newer,
only the standard library, no network, and only temporary output.

## Lesson

### Give each representation a contract

Cairn's source representation is already an AST. That intentionally removes
lexing and parsing from this module so that its claim can be narrow: given one
well-formed closed tree, lower it to one validated IR program.

The source forms and types are:

| Source node | Static rule | Pure evaluation |
| --- | --- | --- |
| <code>IntLiteral(n)</code> | <code>n</code> is an exact signed 32-bit integer | <code>n : i32</code> |
| <code>BoolLiteral(b)</code> | <code>b</code> is an exact Boolean | <code>b : bool</code> |
| <code>Name(x)</code> | nearest active <code>x</code> exists | bound value and type |
| <code>Add(a,b)</code> | both operands are <code>i32</code> | checked mathematical sum |
| <code>Less(a,b)</code> | both operands are <code>i32</code> | Boolean comparison |
| <code>Choose(c,t,f)</code> | <code>c:bool</code>; branches have one type | eagerly evaluate all three, then select |
| <code>Let(x,v,b)</code> | type <code>v</code>, then type <code>b</code> with a shadowing binding | evaluate <code>v</code>, extend scope for <code>b</code> |

The eager rule for <code>Choose</code> matters. Lowering both branches to a
straight-line <code>select</code> would not preserve a lazy or effectful source
conditional. Cairn is pure and evaluates both branches, so the simple lowering
has a stated semantic basis. An optimizing compiler must not silently borrow
this argument for a language with exceptions, I/O, divergence, or lazy
conditionals.

### Make the IR smaller than the source language

Cairn IR has five instructions:

| Opcode | Inputs | Result |
| --- | --- | --- |
| <code>const_i32 n</code> | one signed 32-bit immediate | <code>i32</code> |
| <code>const_bool b</code> | immediate 0 or 1 | <code>bool</code> |
| <code>add_i32 a,b</code> | two prior <code>i32</code> registers | <code>i32</code> |
| <code>less_i32 a,b</code> | two prior <code>i32</code> registers | <code>bool</code> |
| <code>select c,t,f</code> | prior <code>bool</code> plus same-typed branches | branch type |

Each instruction defines exactly one destination. Destinations are contiguous
<code>%0</code>, <code>%1</code>, and so on. Every operand must name a smaller
destination. These rules simultaneously establish single assignment, exclude
use before definition, and make a single forward validation pass sufficient.
The final result register must exist and its recorded type must match the
instruction that defined it.

Names and <code>Let</code> do not survive as instructions. During lowering, the
environment maps each active source name to the register and type of its value.
A nested binding uses a copied environment so shadowing is lexical. A
<code>Name</code> lowers to an existing register and emits nothing. This is a
specific concrete-to-IR mapping, not a general claim that debug names,
locations, or source identities are disposable.

### State lowering invariants before coding

At the entry and return of every recursive lowering call, Cairn maintains:

1. the environment contains only validated identifiers mapped to prior typed
   registers;
2. every retained instruction has one contiguous destination and only prior
   operands;
3. the returned pair is <code>(type, prior register)</code> for the source
   subtree;
4. source nodes, recursive depth, active bindings, instructions, and names are
   still within their checked caps; and
5. a failure returns no program or artifact.

Checks happen before excess recursion or retention. The model admits at most
63 source nodes, depth 24 with the root at depth one, 16 active bindings,
24 ASCII name bytes, and 63 instructions. Signed addition is checked during
execution; overflow produces <code>R001</code> in both the source reference and
IR evaluator rather than wrapping differently.

For an AST with <code>n</code> retained nodes and <code>i</code> emitted
instructions, lowering takes O(n) time and retains O(i+b) model data for at
most <code>b=16</code> active bindings. Those are algorithmic model bounds, not
exact Python heap measurements.

### Treat validation as a trust boundary

The lowering function creates IR, but the executor and encoder validate it
again. They do not rely on a caller's claim that a frozen dataclass is valid.
Validation rejects:

- an unknown exact object or instruction type;
- zero or more than 63 instructions;
- a missing, duplicate, skipped, or reordered destination;
- a forward, self, negative, or out-of-range operand;
- an opcode/type/field mismatch;
- an unknown opcode or type; and
- a result register/type mismatch.

Immutability prevents later field assignment; it does not prove that the
original fields obey cross-record invariants. Validation supplies that second
part.

### Generate bytes only from validated IR

Cairn's artifact is portable because its byte layout is explicit, not because
Python happens to serialize an object. All integers are big-endian.

The 12-byte header is:

| Offset | Bytes | Meaning |
| ---: | ---: | --- |
| 0 | 4 | ASCII magic <code>CIR1</code> |
| 4 | 1 | version 1 |
| 5 | 1 | flags, required zero |
| 6 | 2 | instruction count |
| 8 | 2 | result register |
| 10 | 1 | result type code |
| 11 | 1 | reserved, required zero |

Every instruction is exactly 16 bytes: one-byte opcode, one-byte type,
two-byte destination, three two-byte operand fields, one signed four-byte
immediate, and two reserved zero bytes. Unused operands contain
<code>0xffff</code>; unused immediates contain zero. Therefore the only valid
length is

<code>12 + instruction_count * 16</code>,

and the maximum valid artifact is 1,020 bytes. The decoder rejects truncation,
trailing data, nonzero reserved or unused fields, unknown codes, and a declared
count of 64 before constructing and validating the IR. Re-encoding a decoded
artifact must reproduce the same bytes; that is a useful canonicality test.

### Define what preservation evidence says

For a closed, well-typed, in-budget Cairn expression <code>e</code>, the tested
relation is:

<code>evaluate_source(e) == execute_ir(decode(encode(lower(e))))</code>.

That equality covers a result type and value or a matched declared runtime
failure. A worked case and a fixed table of cases support the relation for
those inputs. Boundary cases support enforcement of the documented envelope.
Malformed IR and byte cases support validator rejection. Exact byte
round-trips support deterministic encoding.

None is a proof for every possible tree. A proof would require a formal source
semantics, IR semantics, lowering relation, and induction over every source
form, plus a verified connection to the executable implementations. Even such
a proof would be scoped to its assumptions. Testing also does not establish
termination, constant-time behavior, secure parsing, optimizer correctness,
machine-code correctness, or any Orange property.

### Use endpoint and failure evidence together

The smoke check builds a full binary addition tree with 32 leaves: 32 constants
plus 31 additions equals exactly 63 source nodes and 63 instructions. Its
artifact is exactly <code>12 + 63 * 16 = 1,020</code> bytes. The same tree with
64 leaves has 127 nodes; 65 is the first representable full-expression node
count above 63, and lowering stops on node 64. Calling that case “64 nodes”
would be inaccurate.

Other tests exercise depth 24/25, 16/17 active bindings, 24/25 name bytes,
signed 32-bit endpoints and one beyond, count 63/64, malformed layouts, and a
36-case source/IR table. A deliberate assertion expects 41 for
<code>20 + 22</code>, observes a nonzero status, restores 42, and observes zero.
That failure shows the test can detect at least that wrong expectation. It does
not measure all possible implementation defects.

## Worked example

Read [<code>examples/ir_pipeline.py</code>](examples/ir_pipeline.py), then run:

~~~sh
cd curriculum/modules/plt-103
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/ir_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

The expression binds <code>base = 20 + 1</code>, tests
<code>base &lt; 22</code>, and selects <code>base + base</code> or zero. The first
command must report <code>i32 42</code>, eight instructions, 140 artifact bytes,
a deterministic SHA-256 digest, and decoded <code>i32 42</code>. The second must
print <code>plt-103 lab smoke: PASS</code> and exit zero.

Trace the environment and register table by hand. The two uses of
<code>base</code> reuse register <code>%2</code>; they do not create load
instructions. Then change the condition to compare against 20 and predict
which value remains represented in the eagerly lowered instruction list and
which value becomes the final result.

## Check your understanding

1. Why would lowering both branches before <code>select</code> be wrong for a
   lazy conditional with an effectful branch?
2. Which invariants make one forward validation pass sufficient?
3. Why does a frozen <code>Instruction</code> still require IR validation?
4. Why is the first full-tree case beyond 63 nodes a 127-node tree rather than
   a 64-node tree?
5. What exact artifact sizes are valid for one and 63 instructions?
6. What does canonical decode/re-encode evidence exclude, and what does it not
   prove?
7. State the preservation relation and three assumptions under which it is
   tested.
8. Why does this module establish no Orange compiler capability?

## Next step

Complete [the lab](lab.md) without importing or translating Cairn. Then submit
[the independent assessment](assessment.md). Passing requires at least 80/100
and every critical criterion in [the rubric](rubric.md). Preserve evidence in a
fresh temporary workspace; do not add generated artifacts or caches to the
course repository.

## Sources

- Python Software Foundation, [<code>struct</code> — Interpret bytes as packed
  binary data](https://docs.python.org/3.11/library/struct.html), Python 3.11.
  This module uses explicit big-endian format strings and standard sizes.
- Python Software Foundation, [<code>dataclasses</code> — Data
  Classes](https://docs.python.org/3.11/library/dataclasses.html), Python 3.11.
  Frozen and slotted records support the model's immutable representation.
- LLVM Project, [LLVM 18.1.0 Language Reference Manual: Well-Formedness and SSA
  values](https://github.com/llvm/llvm-project/blob/llvmorg-18.1.0/llvm/docs/LangRef.rst). Cairn borrows the general lesson
  that IR validity and definition/use discipline must be explicit; Cairn is
  not LLVM IR.
- Xavier Leroy, [Formal verification of a realistic
  compiler](https://doi.org/10.1145/1538788.1538814), Communications of the
  ACM 52(7), 2009. The preservation discussion uses this as motivation for
  distinguishing testing from a semantic preservation proof; Cairn is not
  CompCert.
