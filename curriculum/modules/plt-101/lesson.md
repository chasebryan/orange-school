# Lexers, parsers, syntax trees, and diagnostics

A language frontend turns source bytes into a structured representation or a
bounded, reproducible explanation of why it cannot. Correctness includes more
than accepting the happy path: the frontend must define text decoding, source
positions, token boundaries, precedence, resource limits, invalid-input
behavior, and what recovery does and does not promise.

This module uses **Pebble**, a deliberately small teaching language, and Python
3.11's standard library. Pebble is independent courseware. Its grammar,
diagnostics, and implementation do not define, emulate, or predict Orange.

## Learning objectives

- **PLT-101-01:** Define a byte, Unicode, and source-position policy and build
  a deterministic bounded lexer with structured diagnostics.
- **PLT-101-02:** Specify a grammar and precedence, construct a bounded parser,
  and distinguish concrete syntax from an abstract syntax tree.
- **PLT-101-03:** Test valid, endpoint, and invalid inputs, limited recovery,
  diagnostic stability, and resource claims with differential, metamorphic,
  and deliberate-failure evidence.

## Prerequisites

Pass <code>prg-102</code>. You should be able to write Python functions and
tests, use immutable records, state a loop invariant, reject malformed input,
and bound a collection before processing it. The supplied examples require
Python 3.11 or newer and only its standard library. They run offline and write
temporary evidence only.

## Lesson

### Begin with source units, not characters

“Character position” is ambiguous. A file is bytes. A successful UTF-8 decode
produces Unicode text. Python indexes a <code>str</code> by code point, while a
user interface might count grapheme clusters and a protocol might require byte
offsets. Those units differ: Greek lambda <code>λ</code> occupies two UTF-8
bytes, one Unicode code point, and usually one displayed grapheme cluster.

Pebble makes these choices explicit:

- its API accepts an exact Python <code>str</code> and requires that value to
  encode as strict UTF-8;
- source is capped at 4,096 UTF-8 bytes before token scanning;
- keywords, identifiers, decimal digits, operators, and delimiters use only
  specified ASCII spellings;
- source spans use half-open UTF-8 byte offsets
  <code>[byte_start, byte_end)</code> and one-based line/column positions;
- LF advances the line and resets the column; other accepted whitespace
  advances one code-point column; and
- columns count Unicode code points, not bytes, terminal cells, or grapheme
  clusters.

Passing anything other than an exact Python <code>str</code> is an API contract
error, not malformed source: Pebble raises <code>TypeError("source must be
str")</code> before lexing because a bytes or mutable-byte value has no declared
source-decoding policy. Structured source diagnostics begin only after that
host-language boundary has been satisfied.

The UTF-8 preflight stops as soon as it crosses 4,096 bytes instead of creating
an unbounded encoded copy. An encoding error encountered before that crossing
is <code>L000</code>; once the byte cap is crossed, the stable result is
<code>L001</code> even if later unexamined text would also be unencodable.

The policy deliberately rejects a non-ASCII identifier instead of silently
normalizing it or treating visually similar spellings as equal. A production
language may choose Unicode identifiers and normalization, but it must state
that policy and test confusable and normalization cases. Pebble's smaller
choice is not a universal recommendation.

A half-open span composes cleanly: its byte length is
<code>byte_end - byte_start</code>, and adjacent spans meet at an endpoint.
Keeping byte offsets alongside line/column positions lets a tool slice the
original UTF-8 representation while showing a useful location. Do not compare
a byte offset with a code-point column.

### Lexing is a deterministic bounded partition

A lexer maps source text to a sequence of tokens. A token has a kind, its exact
source spelling, and a span. Pebble recognizes:

| Category | Spellings |
| --- | --- |
| Keywords | <code>let</code>, <code>emit</code> |
| Identifier | ASCII letter or underscore, then ASCII letters, digits, or underscores |
| Integer | One or more ASCII decimal digits |
| Operators | <code>+</code>, <code>-</code>, <code>*</code>, <code>/</code>, <code>=</code> |
| Delimiters | <code>(</code>, <code>)</code>, <code>;</code> |

Whitespace separates tokens and is not retained in the token stream. The
lexer appends one EOF token at the final source position. It retains at most
512 non-EOF tokens, 32 bytes per identifier, ten digits per integer, and eight
diagnostics. A limit violation is an error; truncating an overlong identifier
into a valid one would change the program.

The scanner's progress invariant is: each loop iteration consumes at least one
code point, emits one token after consuming its complete spelling, or stops
with a bounded diagnostic. With <code>s &lt;= 4096</code> UTF-8 source bytes,
lexing is O(s) time and retains O(t) token data for
<code>t &lt;= 512</code>. Python object and allocator overhead is not fixed by
this model.

Structured diagnostics are data, not incidental prose on stderr. Pebble uses
an immutable record containing a stable code, message, and span. For example,
an unsupported lambda produces code <code>L005</code>, a message naming
<code>U+03BB</code>, byte span <code>[8,10)</code>, and line 2, column 1 in the
source <code>emit 1;\nλ</code>. Tests can assert each field separately. The
frontend never includes an address, hash iteration order, locale-formatted
value, or current path in that result.

### Grammar says which token sequences form programs

Pebble's grammar is:

~~~text
program    := statement* EOF
statement  := "let" IDENTIFIER "=" expression ";"
            | "emit" expression ";"
expression := product (("+" | "-") product)*
product    := primary (("*" | "/") primary)*
primary    := INTEGER | IDENTIFIER | "(" expression ")"
~~~

The layered rules encode precedence: multiplication and division bind more
tightly than addition and subtraction. The loops encode left associativity.
Thus <code>1 + 2 * 3</code> groups as <code>1 + (2 * 3)</code>, while
<code>8 - 3 - 1</code> groups as <code>(8 - 3) - 1</code>. Parentheses invoke
the expression rule recursively and can override those defaults.

A grammar must also expose exclusions. Pebble has no unary minus, string
literal, call, comment, assignment statement, implicit multiplication, or
optional semicolon. The lexer can produce a minus token, but the parser accepts
it only between expressions. Token availability alone does not make a token
valid at every grammar position.

### Recursive descent mirrors this grammar

A recursive-descent parser has a function for each grammar level.
<code>parse_sum</code> calls <code>parse_product</code>, which calls
<code>parse_primary</code>. Each function either returns one complete node or
raises a structured parse failure at the current token. An
<code>expect</code> helper consumes one required kind or reports what was
expected at that exact location.

This parser limits parenthesis nesting to 32 and total AST nodes to 256. The
nesting check happens before the recursive call. The node check happens when a
node is constructed. Token consumption is monotonic: the parser never moves
backward and every successful statement consumes its semicolon. Consequently,
parsing is O(t) time with <code>t &lt;= 512</code>; recursive call depth is at
most 32; retained AST data is O(n) for <code>n &lt;= 256</code>. These are model
bounds, not exact process-memory measurements.

A Pratt parser is another good technique when a language has many prefix,
infix, and postfix operators. It associates parsing functions and binding
powers with token kinds. Recursive descent is used here because the small
precedence table maps directly to three readable grammar rules. The important
property is not the parser family but the explicit precedence, associativity,
progress, and resource contract.

### Concrete and abstract syntax serve different consumers

The token stream is a small **concrete syntax** representation: it retains
keywords, punctuation, exact integer spelling, and positions, but discards
whitespace. A full concrete syntax tree used by a formatter might also retain
whitespace and comments.

The **abstract syntax tree** (AST) retains structure needed by later phases:
bindings, emitted expressions, names, integer spellings, and binary operators.
Parenthesis and semicolon nodes are absent because grouping is already encoded
by tree shape and statement boundaries. For example:

~~~text
emit 1 + 2 * 3;

emit
  +
    integer "1"
    *
      integer "2"
      integer "3"
~~~

Discarding concrete details is a policy. Pebble keeps integer text rather than
immediately converting it so a later phase can choose numeric semantics. Its
AST does not establish name resolution, integer range, division behavior,
types, effects, evaluation order, or runtime meaning. Those belong to later
language stages.

### Recovery can improve diagnostics without accepting a program

After a statement error, Pebble discards tokens through the next semicolon and
tries to diagnose the following statement. A semicolon is a **synchronization
point** because it is a statement boundary in this grammar. Recovery is capped
at eight diagnostics. It does not insert missing syntax, guess the author's
intent, recover inside an expression, or promise that every later diagnostic
is independent of the first error.

Most importantly, any lexical or parse diagnostic makes the public program
result <code>None</code>. Internally constructed prefix nodes are never
returned as an executable partial AST. Recovery is therefore a reporting
feature, not acceptance. If a parser chooses to expose error nodes for an IDE,
their non-executable status and downstream handling need a separate contract.

### Test relations, not only examples

Positive tests establish that named programs tokenize and parse. Endpoint tests
exercise exactly 4,096 bytes, 512 tokens, 32 nesting levels, and 256 nodes as
applicable, plus one beyond each feasible endpoint. Invalid tests cover wrong
types, unsupported Unicode spellings, overlong tokens, missing expressions,
missing delimiters, and malformed statement starts. Tests assert diagnostic
codes, messages, and locations as well as absence of an AST.

A **metamorphic test** checks a relation after a controlled transformation.
Adding whitespace or redundant parentheses should preserve Pebble's span-free
AST shape, although source spans change. Renaming an identifier consistently
should preserve the tree shape except for the spelling. Such tests explore
families of inputs without requiring one hand-written expected tree per input.

A **differential test** compares two independent implementations on an agreed
overlap. The smoke check compares Pebble's expression grouping with Python's
standard-library AST only for non-keyword ASCII names, decimal integers without
leading zeroes, and the four operators whose precedence and associativity
match in that restricted subset. Agreement is
evidence about those test cases, not proof that Pebble has Python semantics.
Shared code, shared bugs, or an incorrectly defined overlap can weaken the
comparison.

A deliberate-failure check temporarily asserts that multiplication is the root
of <code>1 + 2 * 3</code>. The observed nonzero run demonstrates that the test
can detect the targeted defect. Restoring the correct addition root and
observing status zero completes the evidence pair.

### Frontend success makes narrow claims

A successful Pebble parse claims only that bounded UTF-8 input conforms to the
documented Pebble lexical and grammar rules and produced the shown AST. It does
not show that the program is well typed, names exist, arithmetic is safe,
execution terminates, generated code is correct, input is trustworthy, or the
language is secure. It makes no compatibility or conformance claim about
Orange. A frontend is one trust boundary in a larger toolchain, not the whole
toolchain.

## Worked example

Run the local example from the repository root:

~~~sh
cd curriculum/modules/plt-101
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/frontend_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

The source is:

~~~text
let width = 2 + 3 * 4;
emit width;
~~~

The lexer produces 12 source tokens plus EOF. The AST shape places
<code>*</code> below <code>+</code>, proving the declared precedence for this
case. The final command prints exactly <code>plt-101 lab smoke: PASS</code> and
exits zero after valid, endpoint, invalid, recovery, metamorphic, differential,
and deliberate-failure checks. All subprocess evidence is created under a
temporary directory.

## Check your understanding

1. Why are byte offset 10 and column 10 not interchangeable?
2. What property makes <code>;</code> a useful recovery point in Pebble?
3. Draw both token sequence and AST for <code>emit (1 + 2) * 3;</code>. Which
   concrete tokens disappear from the AST?
4. Why must a diagnostic suppress the public AST even if the first statement
   parsed successfully?
5. State the exact source, token, nesting, node, and diagnostic caps.
6. What does the Python-AST differential check establish, and what does it not
   establish?

## Next step

Complete the lab by implementing the distinct **Rill** teaching grammar, then
complete the independent **Chalk** assessment. The next curriculum module uses
frontends as input to name resolution, types, and operational semantics; it
does not change this module's syntax-only claims.

## Sources

- [Python 3.11 lexical analysis](https://docs.python.org/3.11/reference/lexical_analysis.html)
  is the authoritative language-reference comparison for Python source
  encodings, tokens, identifiers, and indentation. Pebble adopts none of
  Python's grammar implicitly.
- [Python 3.11 <code>ast</code> documentation](https://docs.python.org/3.11/library/ast.html)
  specifies the standard-library parser interface used for the narrow
  differential check.
- [The Unicode Standard 17.0.0, Chapter 3](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/)
  defines Unicode conformance concepts and encoding forms; Pebble separately
  states its ASCII spelling subset and position units.
- [Unicode Standard Annex #29, revision 47](https://www.unicode.org/reports/tr29/tr29-47.html)
  explains grapheme-cluster boundaries, which are intentionally distinct from
  Pebble's code-point columns.
- [RFC 3629: UTF-8](https://www.rfc-editor.org/rfc/rfc3629)
  defines the UTF-8 encoding used for Pebble byte counts and byte spans.
