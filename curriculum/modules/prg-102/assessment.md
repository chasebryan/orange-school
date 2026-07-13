# Assessment: bounded event summary

## Instructions

Complete this assessment independently with Python 3.11+ and only the standard
library. Work in a fresh temporary directory. Submit source, tests,
representation-and-bounds notes, and a reproducible command/result record. Do
not copy or rename the module examples or lab solution.

This assessment covers:

- **PRG-102-01:** Choose and justify list, tuple, dictionary, and set
  representations from required operations and invariants.
- **PRG-102-02:** Implement and test search, count, deduplication, and ordering
  algorithms.
- **PRG-102-03:** State and enforce time, space, and input bounds.

## Knowledge check

1. For each case, choose a list, tuple, dictionary, or set and justify it:
   ordered duplicate-preserving input; fixed two-field record; lookup from
   unique code to count; membership among codes already observed.
2. Explain why <code>list(set(values))</code> does not implement stable
   deduplication.
3. State the time and extra-space growth of linear search, dictionary counting,
   stable deduplication with a set, and copied comparison ordering. Identify
   which claims rely on expected hash-table behavior.
4. Explain why an asymptotic statement does not replace a concrete input bound.
5. Given a maximum of 64 events, state maximum linear-search comparisons and
   maximum distinct keys retained.

## Independent task

Create <code>event_summary.py</code> with this interface:

~~~text
python3 event_summary.py TARGET EVENT [EVENT ...]
~~~

1. **Representations — PRG-102-01.**
   - Preserve input events in order with duplicates.
   - Represent each parsed event as a fixed record containing its code and
     original position.
   - Map each unique code to its count.
   - Track codes already emitted during stable deduplication.
   Write a justification for the list, tuple, dictionary, and set used,
   including the invariant each one maintains.
2. **Algorithms — PRG-102-02.** Implement your own loop-based functions for:
   - the first position of <code>TARGET</code>, or <code>None</code>;
   - a count for every event code;
   - first-occurrence-order deduplication; and
   - an ordered copy of the unique codes, without mutating the input.

   On success, print labeled lines for first target position, target count,
   unique codes in input order, and unique codes in sorted order. Tests must
   check search at first/last/absent positions, repeated/all-unique data,
   stable deduplication, correct counts, ordering, and lack of input mutation.
3. **Bounds — PRG-102-03.** Accept from 1 through 64 events. Each event and
   target code must contain 1 through 12 uppercase ASCII letters, digits, or
   underscores. Reject the complete input before running the reporting
   algorithms if any bound fails. Invalid input writes a precise diagnostic to
   stderr, no report to stdout, and exits nonzero.

   State time and extra-space bounds using <code>n</code> and distinct count
   <code>u</code>, identify expected hashing assumptions, and translate the
   64-event limit into concrete maximum search comparisons and retained keys.
4. Create <code>test_event_summary.py</code> using <code>unittest</code> or
   simple assertions. Include normal cases, exactly 1 and 64 events, 65 events,
   empty and overlong codes, lowercase and punctuation, plus command-level
   checks of stdout, stderr, and exit status.
5. Record Python version, absolute directory, exact commands, observations,
   statuses, and limits of the test evidence.

## Completion criteria

Use [the rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. The submission must:

- justify all four representations from operations and invariants for
  **PRG-102-01**;
- correctly implement and independently test all four algorithms for
  **PRG-102-02**;
- state and enforce time, space, item-count, and per-item bounds for
  **PRG-102-03**;
- reject invalid or oversized input before reporting success; and
- run offline using only Python's standard library.
