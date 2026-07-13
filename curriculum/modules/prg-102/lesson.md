# Data structures, algorithms, and bounds

A useful program chooses representations that make required operations clear,
implements those operations predictably, and refuses input beyond the work it
promises to perform. This module uses Python's built-in collections and small
algorithms whose behavior you can trace by hand.

## Learning objectives

- **PRG-102-01:** Choose and justify list, tuple, dictionary, and set
  representations from required operations and invariants.
- **PRG-102-02:** Implement and test search, count, deduplication, and ordering
  algorithms.
- **PRG-102-03:** State and enforce time, space, and input bounds.

## Prerequisites

Pass <code>prg-101</code>. You should be able to trace variables, functions,
branches, and loops; write a command-line Python program; handle invalid input;
and run normal, boundary, and invalid tests. This module uses only Python 3.11+
standard-library behavior.

## Lesson

**Choose a representation from the job, not habit.**

| Type | Order | Duplicates | Mutation | Best fit |
| --- | --- | --- | --- | --- |
| <code>list</code> | Preserves position | Allowed | Add, remove, or replace elements | A sequence whose order and contents may change |
| <code>tuple</code> | Preserves position | Allowed | Positions are fixed after construction | A fixed record or immutable snapshot |
| <code>dict</code> | Maps unique keys to values | Keys are unique | Add, remove, or replace mappings | Lookup by meaningful key, such as item ID to quantity |
| <code>set</code> | Do not use iteration order as a result contract | Members are unique | Add or remove members | Membership checks and uniqueness |

Python dictionaries preserve insertion order, but that fact does not turn every
mapping into a sequence. Select a dictionary when key-to-value lookup is the
main operation. Likewise, select a set when membership or uniqueness matters;
sort explicitly when output order is part of the contract.

A tuple cannot replace or add positions, but an object stored at one position
may itself be mutable. “Immutable snapshot” therefore requires immutable
elements or an explicit copy of mutable input.

Write the representation invariant in one sentence. Examples:

- “<code>readings</code> is a list because repeated values and input order are
  meaningful.”
- “Each parsed inventory entry is a two-field tuple
  <code>(name, quantity)</code>.”
- “<code>inventory</code> maps each unique item name to one bounded quantity.”
- “<code>seen</code> contains exactly the values already appended to the
  deduplicated result.”

The data structure does not enforce every invariant automatically. A dictionary
prevents duplicate keys in its final state, but assigning the same key twice
would silently replace a value. If duplicates are invalid input, check before
assignment.

**Linear search** checks values from the beginning and returns as soon as it
finds the target:

~~~python
def find_first(values, target):
    for index, value in enumerate(values):
        if value == target:
            return index
    return None
~~~

For <code>n</code> values, the algorithm performs at most
<code>n</code> equality checks. Its time is O(n), and aside from loop state it
uses O(1) extra space. Returning <code>None</code> distinguishes “not found”
from index 0.

**Counting** needs one value per distinct key:

~~~python
def count_values(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
~~~

After each iteration, the invariant is: <code>counts</code> contains the exact
frequencies in the processed prefix. If there are <code>u</code> distinct
values, extra space is O(u). Python dictionaries are hash tables; lookup and
update are normally treated as expected O(1), so the loop is expected O(n).
That is not a language-level worst-case guarantee. An enforced maximum input
size still bounds total work.

**Stable deduplication** preserves the first occurrence:

~~~python
def unique_in_order(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
~~~

The list records output order, while the set supports expected constant-time
membership. Extra space is O(u), and expected time is O(n). Using
<code>list(set(values))</code> would discard the first-occurrence order
contract. Using only <code>if value not in result</code> preserves order but
can require O(n²) comparisons.

**Ordering** should say whether the input may change:

~~~python
ordered = sorted(values)
~~~

<code>sorted</code> returns a new list and leaves <code>values</code> alone.
<code>values.sort()</code> changes that list in place and returns
<code>None</code>. Python's sort is stable: equal-key items retain their
relative order. State whether duplicates remain and which key determines order.
Comparison sorting uses O(n log n) time as a useful upper bound for this task;
the new list requires O(n) result space.

**Bounds are executable contracts.** Big-O describes growth, not an acceptable
resource budget. “O(n)” is still unbounded when <code>n</code> is unbounded.
Validate before expensive processing:

~~~python
MAX_ITEMS = 100


def validate_items(items):
    if not 1 <= len(items) <= MAX_ITEMS:
        raise ValueError("supply from 1 through 100 items")
~~~

Also bound individual item length or numeric range when those affect memory,
parsing, output, or later arithmetic. Record:

- the input limits and when validation occurs;
- worst-case loop iterations or comparisons under that limit;
- expected versus guaranteed complexity assumptions;
- extra space in terms of <code>n</code> or distinct count <code>u</code>; and
- failure behavior when a bound is exceeded.

With at most 100 items, linear search performs at most 100 equality checks.
Stable deduplication holds at most 100 entries in both result and membership
structures. Sorting accepts at most 100 items. These statements are falsifiable
and operationally more useful than “the input should be small.”

## Worked example

Trace the sequence <code>[7, 10, 7, 5]</code> with target 7.

Linear search compares index 0, finds 7, and returns 0. Counting evolves as:

| Processed value | <code>counts</code> |
| ---: | --- |
| 7 | <code>{7: 1}</code> |
| 10 | <code>{7: 1, 10: 1}</code> |
| 7 | <code>{7: 2, 10: 1}</code> |
| 5 | <code>{7: 2, 10: 1, 5: 1}</code> |

Stable deduplication evolves as:

| Value | Already in <code>seen</code>? | <code>result</code> afterward |
| ---: | --- | --- |
| 7 | no | <code>[7]</code> |
| 10 | no | <code>[7, 10]</code> |
| 7 | yes | <code>[7, 10]</code> |
| 5 | no | <code>[7, 10, 5]</code> |

An ordered copy is <code>[5, 7, 7, 10]</code>; duplicates remain and the input
list is unchanged. The [bounded-scores example](examples/bounded_scores.py)
implements all four operations and rejects more than 100 scores before
processing. The [inventory example](examples/inventory_lookup.py) shows a list
of input records becoming tuples, a dictionary, a set, and an explicitly
ordered tuple for distinct purposes.

## Check your understanding

1. Which structure fits an ordered, editable series where duplicates matter?
2. Which structure fits a fixed latitude/longitude pair?
3. Why use both a list and a set for stable deduplication?
4. What do <code>n</code> and <code>u</code> mean in O(n) time and O(u) space?
5. Why is “dictionary lookup is O(1)” an incomplete assurance claim?
6. If input is capped at 64 items, what is the maximum number of comparisons
   for a complete linear search?

**Answers:** (1) list; (2) tuple; (3) the list preserves first-occurrence order
and the set supports membership checks; (4) total input items and distinct
items; (5) it is an expected hash-table behavior, not an unconditional
language-level worst-case guarantee, and it omits the input bound; (6) 64.

## Next step

Complete the [lab](lab.md), including representation justifications and bounded
tests. Then take the [independent assessment](assessment.md). Passing requires
at least 80/100 and every critical criterion in the [rubric](rubric.md).

## Sources

- Python Software Foundation, [The Python Tutorial, Python 3.11: Data
  Structures](https://docs.python.org/3.11/tutorial/datastructures.html), lists,
  tuples, sets, dictionaries, looping, and sorting.
- Python Software Foundation, [Python 3.11 standard type
  hierarchy](https://docs.python.org/3.11/library/stdtypes.html), sequence,
  mapping, and set behavior.
- Python Software Foundation, [Sorting Techniques, Python
  3.11](https://docs.python.org/3.11/howto/sorting.html), stable sorting, keys,
  and in-place versus copied order.
- [Assessment system](../../../docs/assessment-system.md), independent evidence
  and pass policy.
