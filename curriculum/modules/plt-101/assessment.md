# Assessment: independent Chalk language frontend

## Instructions

Complete this assessment independently in a fresh temporary directory using
Python 3.11 or newer and only the standard library. Do not copy, import, rename,
or lightly translate Pebble or a Rill solution. Chalk has a distinct source
contract, grammar, syntax, limits, and recovery boundary.

Submit the specification, implementation, tests, deliberate-failure outputs,
resource argument, source hashes, exact commands, stdout, stderr, and immediate
statuses. All generated artifacts must remain under the temporary directory.
The work must run offline without external packages or privileged operations.

## Knowledge check

Answer before writing code:

1. Distinguish UTF-8 byte offset, Unicode code-point index, one-based source
   column, display cell, and grapheme cluster. Which two units does Chalk store?
2. For <code>print 8 - 3 - 1 !</code>, state the tree implied by left
   associativity. For <code>print 2 + 3 * 4 !</code>, state the tree implied by
   precedence.
3. Explain why a token sequence is concrete syntax and why a punctuation-free
   AST cannot reproduce every original source spelling.
4. Give a progress invariant for scanning and one for parser recovery.
5. Explain why returning the first valid statement alongside a later parse
   error can be dangerous to a consumer expecting a complete program.
6. Contrast example, endpoint, metamorphic, differential, and
   deliberate-failure tests. Name one limitation of each.
7. State why frontend acceptance alone says nothing about name resolution,
   types, execution, code generation, security, or Orange conformance.

## Independent task

Create <code>chalk_frontend.py</code>, <code>test_chalk_frontend.py</code>, and
<code>evidence.md</code>.

1. **Text and positions — PLT-101-01.** Accept only exact <code>str</code>
   values that strictly encode as UTF-8. Cap source at 3,072 UTF-8 bytes before
   scanning. Chalk uses ASCII spellings only; no normalization, case folding,
   escape decoding, or Unicode identifiers are supported. Store half-open
   UTF-8 byte spans plus one-based LF-delimited line and Unicode-code-point
   columns. Specify treatment of space, tab, CR, and LF. Reject unsupported or
   unencodable source with immutable structured diagnostics. Reject non-str
   API values with the exact <code>TypeError("source must be str")</code>.
2. **Lexer — PLT-101-01.** Recognize keywords <code>bind</code> and
   <code>print</code>; an ASCII identifier beginning with a lowercase letter
   and continuing with lowercase letters, digits, or underscore; unsigned
   ASCII decimal integers; the two-character binding token <code>&lt;-</code>;
   operators <code>+</code>, <code>-</code>, <code>*</code>, and
   <code>/</code>; grouping braces <code>{</code> and <code>}</code>; and
   statement terminator <code>!</code>. A lone <code>&lt;</code> is invalid.
   Bound identifiers at 20 bytes, integers at nine digits, retained source
   tokens at 512 plus EOF, and diagnostics at five. Preserve exact token text
   and spans; reject rather than truncate.
3. **Grammar and AST — PLT-101-02.** Implement this grammar without adding
   unary operators, optional terminators, or implicit recovery productions:

   ~~~text
   program    := statement* EOF
   statement  := "bind" IDENTIFIER "<-" expression "!"
               | "print" expression "!"
   expression := product (("+" | "-") product)*
   product    := primary (("*" | "/") primary)*
   primary    := INTEGER | IDENTIFIER | "{" expression "}"
   ~~~

   Use immutable program, binding, print, integer, name, and binary nodes.
   Retain integer spelling and source spans but omit keywords, terminators,
   braces, and operator tokens as standalone tree nodes. Binary nodes retain
   their operator spelling. Enforce left associativity and the declared two
   precedence levels.
4. **Bounds and recovery — PLT-101-02.** Cap grouping depth at 20 and statement
   plus expression AST nodes at 384; the enclosing program record is not part
   of that count. Check the cap before recursion or retention. After a statement error,
   discard through at most the next <code>!</code>, then continue only while
   EOF and the five-diagnostic cap have not been reached. Prove the recovery
   loop makes progress. Any lexical or parse diagnostic must make the public
   program result absent; no valid prefix or recovered suffix may escape as an
   executable AST.
5. **Deterministic diagnostics — PLT-101-01, PLT-101-02.** Define stable codes
   for invalid source encoding, source/token/spelling limits, unsupported
   code point, unexpected token, missing expression, missing closing brace,
   missing terminator, nesting, and node limits. Assert code, message, UTF-8
   byte span, line/column span, ordering, and cap. Diagnostic content must not
   depend on a temporary path, object address, locale, hash order, or clock.
6. **Positive and endpoint tests — PLT-101-03.** Test exact tokens and AST for
   <code>bind area &lt;- 2 + 3 * 4 ! print area !</code>. Include empty input,
   multiple lines, identifiers at 1 and 20 bytes, integers at 1 and 9 digits,
   exactly 3,072 valid padded UTF-8 bytes, exactly 512 source tokens, grouping
   at depth 20, and a calculated exact 384-node program. Because every added
   binary operand contributes an operand and a binary node, the smallest
   constructible overflow is 386 nodes rather than 385; test that case while
   remaining below the token cap. Check source positions at ASCII and
   multibyte-invalid boundaries. For each other feasible cap, also test one
   beyond without accidentally crossing another cap first.
7. **Invalid and recovery tests — PLT-101-03.** Prove bytes and mutable-byte
   inputs raise the exact API <code>TypeError</code>. Cover an unencodable
   surrogate, uppercase/non-ASCII identifiers, lone
   <code>&lt;</code>, overlong identifier/integer, invalid program start,
   missing binding name/arrow/expression/brace/terminator, extra brace,
   repeated operators, trailing tokens, over-budget source/tokens/depth/nodes,
   two malformed statements followed by valid syntax, and at least six
   malformed statements. Every rejected case must have no program result.
8. **Metamorphic and differential evidence — PLT-101-03.** Show with executable
   tests that inserting legal whitespace and redundant braces preserves a
   span-free AST shape, while consistent identifier renaming changes only name
   spellings. Independently implement either a shunting-yard parser or a Pratt
   parser for expressions. Compare at least 30 fixed-seed, bounded expression
   cases across all four operators. The reference must not call production
   lexer or parser functions. Document the precise shared subset and preserve
   the inputs used. Agreement is evidence for those cases, not proof.
9. **Failure sensitivity — PLT-101-03.** Mutate three expectations one at a
   time: the precedence root of <code>2 + 3 * 4</code>, the UTF-8 byte end of a
   rejected multibyte code point, and the diagnostic code for a missing brace.
   Run only the targeted tests, preserve stdout/stderr and immediate nonzero
   status, restore the expectation, and preserve the passing rerun.
10. **Resource and claim record.** State and justify
    <code>s &lt;= 3072</code> UTF-8 source bytes, <code>t &lt;= 512</code> source
    tokens, depth at most 20, <code>n &lt;= 384</code> AST nodes, and at most five
    diagnostics. Give O(s) lexer time, O(t) parser time, and O(t+n) retained
    model data, while labeling Python runtime/allocator overhead as outside the
    exact model. State that Chalk is independent teaching courseware. Parsing
    proves no name, type, evaluation, termination, compilation, safety,
    authenticity, confidentiality, or Orange property.

## Completion criteria

Use [the rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. A complete submission must:

- define and implement the UTF-8 byte/Unicode position contract for
  **PLT-101-01**;
- tokenize deterministically within all spelling, source, token, and diagnostic
  bounds for **PLT-101-01**;
- implement the independent Chalk grammar, precedence, complete-or-none AST,
  nesting/node caps, and limited recovery for **PLT-101-02**;
- provide positive, endpoint, one-beyond, invalid, recovery, metamorphic,
  independent differential, and observed deliberate-failure evidence for
  **PLT-101-03**;
- preserve reproducible commands, channels, hashes, and immediate statuses;
  and
- make only the narrow frontend claims supported by the evidence.
