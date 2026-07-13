# Lab: build the bounded Rill frontend

## Goal

Implement and test a deterministic lexer and recursive-descent parser for a
new teaching language, with explicit UTF-8 positions, grammar and precedence,
complete-or-none AST behavior, structured diagnostics, limited recovery, and
auditable resource bounds.

## Setup

From the repository root, inspect and run the supplied Pebble model:

~~~sh
cd curriculum/modules/plt-101
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/frontend_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

The final command must print <code>plt-101 lab smoke: PASS</code> and exit 0.
Use Python 3.11 or newer and only the standard library.

Create a fresh temporary workspace and keep all learner artifacts there:

~~~sh
workdir="$(mktemp -d)"
cd -- "$workdir"
pwd
~~~

Use <code>PYTHONDONTWRITEBYTECODE=1</code> and <code>python3 -B</code> for every
run. Do not import, copy, rename, or mechanically translate the Pebble example.
Rill has a different contract below. No external package, network operation,
administrator access, permission change, or repository write is needed.

## Tasks

1. **Write the text and position policy — PLT-101-01.** Create
   <code>rill_frontend.py</code>. Its public function accepts exact
   <code>str</code>, requires strict UTF-8 encodability, and caps source at
   2,048 UTF-8 bytes. Rill spellings are ASCII only. Use half-open UTF-8 byte
   spans and one-based LF-delimited line/code-point-column positions. State
   explicitly that columns are not byte offsets, display cells, or grapheme
   clusters. Reject unsupported code points; do not normalize or substitute
   them.
2. **Implement the lexer — PLT-101-01.** Recognize keywords
   <code>put</code> and <code>show</code>; ASCII identifiers of 1–24 bytes;
   integers of 1–8 ASCII digits; <code>:=</code>; operators <code>+</code>,
   <code>-</code>, <code>*</code>; and delimiters <code>[</code>,
   <code>]</code>, and <code>.</code>. A lone colon is invalid. Retain at most
   384 source tokens plus one EOF token and at most six diagnostics. Define
   frozen token, span, and diagnostic records. Diagnostic codes, messages, and
   spans must be deterministic.
3. **Specify and implement the parser — PLT-101-02.** Use this grammar exactly:

   ~~~text
   program    := statement* EOF
   statement  := "put" IDENTIFIER ":=" expression "."
               | "show" expression "."
   expression := product (("+" | "-") product)*
   product    := primary ("*" primary)*
   primary    := INTEGER | IDENTIFIER | "[" expression "]"
   ~~~

   Build a frozen AST with binding, display, integer, name, and binary nodes.
   Preserve integer spelling but omit punctuation and grouping nodes. Addition
   and subtraction are left-associative; multiplication binds tighter. Cap
   bracket nesting at 24 and total AST nodes at 256, with checks before further
   recursion or retention.
4. **Bound recovery — PLT-101-02.** On a statement parse error, synchronize
   through the next period, then attempt the next statement until EOF or six
   diagnostics. Prove every recovery loop consumes a token or stops. Return a
   program only when there are no lexical or parse diagnostics. Never return a
   valid-looking prefix AST, and do not invent missing tokens.
5. **Test positive and endpoint behavior — PLT-101-03.** In
   <code>test_rill_frontend.py</code>, use <code>unittest</code> to check exact
   tokens, spans, and AST shape for
   <code>put total := 2 + 3 * 4. show total.</code>. Cover an empty program,
   LF line transitions, one multibyte rejected code point, identifiers of 1
   and 24 bytes, integers of 1 and 8 digits, exactly 2,048 source bytes where a
   valid padded program fits, 384 source tokens, 24 bracket levels, and an
   exact 256-node program whose size you calculate. Count statement and
   expression nodes but not the enclosing program record. Because a binary
   operand adds both an operand and a binary node, use the smallest
   constructible overflow, 258 nodes, for the node rejection case. Cover one
   beyond every other feasible endpoint.
6. **Test invalid and recovery behavior — PLT-101-03.** Prove a bytes object
   raises exactly <code>TypeError("source must be str")</code> at the API
   boundary. Cover an unencodable surrogate, non-ASCII identifier, lone colon, overlong
   identifier/integer, invalid statement start, missing expression, unmatched
   bracket, missing period, over-budget source/tokens/nesting/nodes, and more
   than six malformed statements. For malformed source, assert diagnostic code, stable message,
   exact byte and line/column span, order, cap, and <code>program is None</code>.
   Include two malformed statements followed by a valid one and prove recovery
   reports errors without returning the valid suffix as a program.
7. **Add metamorphic and differential tests — PLT-101-03.** Define a span-free
   AST shape. Show that adding whitespace and redundant square-bracket grouping
   preserves the shape. For at least 20 bounded expressions generated from a
   fixed local table, compare Rill's grouping with an independently written
   shunting-yard or precedence-climbing reference parser. Do not import the
   implementation under test into the reference algorithm. Record the exact
   shared grammar subset and state that agreement is test evidence, not a
   semantic or correctness proof.
8. **Prove failure sensitivity — PLT-101-03.** Temporarily change the expected
   root for <code>2 + 3 * 4</code> from addition to multiplication. Run only
   that test, preserve stdout, stderr, and the immediate nonzero status. Restore
   addition, rerun the same test, and preserve status zero. Also mutate one
   expected byte endpoint for the rejected multibyte input, observe failure,
   and restore it.
9. **Record bounds and non-claims.** Write <code>evidence.md</code> with Python
   version, absolute workspace path, source hashes, commands, stdout, stderr,
   and immediate statuses. State <code>s &lt;= 2048</code> source bytes,
   <code>t &lt;= 384</code> source tokens, depth at most 24,
   <code>n &lt;= 256</code> AST nodes, and at most six diagnostics. Justify O(s)
   lex time, O(t) parse time, and O(t+n) retained model data; do not claim exact
   Python process memory. State that Rill is independent teaching courseware
   and establishes no Orange syntax, semantics, compatibility, conformance,
   safety, or security property.

## Verification

From the temporary workspace, run:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v \
  >passing.stdout 2>passing.stderr
status=$?
printf 'test status: %s\n' "$status"
~~~

Status zero is necessary but not sufficient. Inspect the source and evidence
and verify that:

- byte offsets and code-point columns follow the written UTF-8 policy;
- tokenization makes progress and refuses truncation at each cap;
- grammar code and documented precedence agree;
- bracket depth and AST nodes are checked before unbounded work or retention;
- recovery stops at a declared synchronization point, remains capped, and
  cannot return a partial program;
- positive, exact endpoints, one-beyond, and malformed inputs are present;
- metamorphic and independent differential relations are actually checked;
- both deliberate mutations produced observable nonzero statuses before their
  restored passes; and
- all learner-created files and outputs remain beneath the temporary path.

Finally, rerun the repository smoke check from the module directory as separate
evidence that the supplied model remains unchanged:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

## Reflection

Write five to seven sentences answering:

- Which Rill location demonstrates that a byte offset and column can differ?
- How do the grammar functions establish precedence and associativity?
- Which concrete syntax disappears from the AST, and why?
- Why does recovery collect diagnostics but suppress the whole program?
- Which endpoint was hardest to construct without accidentally crossing a
  different bound first?
- What did the differential test add beyond hand-written examples?
- Which useful frontend or Orange claim remains unsupported by this lab?
