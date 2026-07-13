# Assessment: finite beacon games and conditional reduction audit

## Instructions

Complete this assessment independently with Python 3.11 or newer and only the
standard library. Work in a fresh temporary directory. Submit the written game
definitions, executable exact model, tests, hop/reduction ledger, concrete
bound worksheet, sample plan and result, and reproducible evidence record.

Do not copy or rename the archive-challenge lab or the expose-or-hide worked
model. The assessed beacon game must include the query choice and abort rule
specified below. It must use your own data structures and enumerator. You may
consult the supplied examples, but the assessor must be able to distinguish
your implementation and evidence. Do not implement a cryptographic primitive
or claim anything about Orange.

The assessment covers:

- **FRM-104-01:** Specify a bounded probabilistic security game with challenger,
  adversary, randomness, interfaces, transcript, win event, baseline,
  advantage, resource bounds, and quantifier order.
- **FRM-104-02:** Construct reviewable game hops and reductions whose assumptions,
  bad events, loss terms, and concrete bounds are explicit and directionally
  valid.
- **FRM-104-03:** Distinguish proof from exact finite enumeration and seeded
  simulation, then produce boundary, relational, deliberate-failure, and
  reproducibility evidence with calibrated claims.

Use this independent toy scenario:

> A challenger samples a uniform hidden beacon bit and a uniform marked slot
> from <code>0..m-1</code>. Before seeing a reply, a deterministic adversary
> selects one slot to probe. In Game 0, a correct probe returns the hidden bit;
> every other probe returns an independent fair decoy. In Game 1, every probe
> returns an independent fair decoy. In Game 2, Game 1's decoy is supplied by
> a hypothetical primitive interface. The adversary sees its selected slot and
> reply and guesses the hidden bit. An invalid or second probe aborts and loses.
> The course model admits <code>1 <= m <= 32</code> and exactly one probe.

Game 2 is hypothetical. The assessment may state a conditional primitive
assumption and reduction term but must not implement or validate the primitive.

## Knowledge check

1. Define challenger, adversary, transcript, win event, baseline, advantage,
   resource class, and assumption game without using them interchangeably.
2. Write the quantifier order for a bit-guessing game and explain how fixing
   one program and one parameter weakens the claim.
3. Compare the conventions <code>|Pr[win]-1/2|</code> and
   <code>2|Pr[win]-1/2|</code>. Why must a report name one?
4. State the obligations of an adaptive oracle interface, including invalid,
   repeated, challenge-related, and over-budget queries.
5. Explain coupling and identical-until-bad. Which game's probability appears
   in the transition bound?
6. Give the useful direction of a reduction from a target adversary to an
   assumption adversary. Name three possible loss terms and two resource
   overheads.
7. Distinguish an exact probability, union upper bound, asymptotic assumption,
   concrete assumption bound, seeded sample frequency, and confidence
   statement.
8. Explain why exhaustive enumeration of a bounded model can be exact while
   remaining neither a general cryptographic proof nor implementation evidence.

## Independent task

1. **Formal game contract — FRM-104-01.** Create
   <code>beacon-games.md</code>. Give pseudocode for Games 0, 1, and 2. Specify
   every random variable and distribution, input domain, state transition,
   adversary call, probe validation and abort, transcript, output, win event,
   one-half baseline, absolute advantage, and exact quantifier order. State
   time, memory, probe, slot, and enumeration bounds. Define how adversary
   coins would enter even though your executable strategies are deterministic.
2. **Adversary class — FRM-104-01.** Define a deterministic strategy by a probe
   slot and a Boolean guess for each possible reply. Validate exact types and
   ranges before execution. Explain why enumerating <code>4m</code> such
   strategies covers randomized mixtures within this finite model but not all
   efficient adversary programs in a general game. Reject invalid and repeated
   probes rather than skipping them.
3. **Exact executable model — FRM-104-01 and FRM-104-03.** Create
   <code>beacon_model.py</code>. Enumerate hidden bit, marked slot, probe, decoy
   bit, and every deterministic strategy for each <code>m</code> from 1 through
   32. Use <code>fractions.Fraction</code> for every exact probability and
   advantage. Produce a deterministic result table and identify the worst
   strategy. Assert internally that Game 1 gives zero advantage, that Game 0
   and Game 1 coincide for strategies whose probe can never equal the marked
   slot in an assessor-supplied restricted variant, and that the maximum Game
   0 advantage is nonincreasing as <code>m</code> grows.
4. **Hop proof obligations — FRM-104-02.** Create
   <code>hop-ledger.md</code>. For Game 0 to Game 1, define the coupled coins,
   the single changed reply, event <code>Bad = selected slot equals marked
   slot</code>, and the exact adjacent gap. Prove the gap is no larger than
   <code>Pr[Bad]=1/m</code> using an identical-until-bad argument and state the
   game in which that probability is measured. For Game 1 to Game 2, name the
   exact distributional replacement and make the gap conditional on a
   separately stated primitive assumption. Do not treat code similarity as a
   hop proof.
5. **Reduction construction — FRM-104-02.** Write pseudocode for assumption
   adversary <code>B</code> using target adversary <code>A</code>. Document
   challenge embedding, complete query simulation, output translation, aborts,
   guessed positions, probability relation, direction of the inequality,
   runtime, memory, query, and data overhead. State whether the reduction is
   tight. Include a deliberate reversed inequality, mark it invalid, repair
   it, and explain why the repaired direction supports the target theorem.
6. **Concrete accounting — FRM-104-02.** Create
   <code>concrete-bounds.csv</code> with one row per primitive, bad-event,
   guessing, collision, and mathematical-simulation term. Include formula,
   exact parameters, exact rational value, assumption/source, resource
   transformation, and scope. Evaluate two assessor cases: (a)
   <code>m=32</code>, primitive term <code>2^-40</code>, no other loss; and (b)
   the same values plus collision union bound
   <code>q(q-1)/(2N)</code> for <code>q=4,096,N=65,536</code>. Preserve the
   uncapped expression and probability cap, sum terms without rounding down,
   and label whether each result is informative under maximum advantage
   <code>1/2</code>.
7. **Boundary and relational tests — FRM-104-03.** Create
   <code>test_beacon_model.py</code> with <code>unittest</code>. Exercise
   <code>m=1</code>, <code>m=32</code>, and rejection of 0 and 33; all
   <code>4m</code> strategies; exact trial counts; invalid game and strategy
   types; probe endpoint and one beyond; ideal zero advantage; bad-event hop
   bound; complement-strategy symmetry; monotonic worst advantage; exact
   Fraction results; and deterministic rendering. Mutate the Game 1 decoy into
   the hidden bit, preserve a relational-test failure, restore it, and preserve
   a passing run.
8. **Pre-registered simulation — FRM-104-03.** In a separate
   <code>beacon_sample.py</code>, implement a seeded sample path with at most
   100,000 trials. Before running, record the exact game, strategy,
   <code>m=17</code>, trial count 20,000, seed 104, estimator, expected exact
   value, and reporting precision. Run once. Preserve frequency, exact target,
   absolute error, command, channels, and status. Explain why replayability is
   not independence, an exact calculation, a confidence interval, or proof of
   a zero-probability event.
9. **Evidence and claim audit — FRM-104-03.** Create
   <code>evidence-map.md</code>. Record Python version, absolute workspace,
   SHA-256 identities, exact commands, stdout, stderr, immediate statuses,
   loop/sample-space calculations, endpoint results, failure/restoration
   evidence, and output identities. Classify each item as definition,
   assumption, proof step, exact executable-model result, test, empirical
   sample, external implementation evidence, or deployment evidence. Explicitly
   reject general primitive security, proof-assistant verification,
   constant-time behavior, implementation conformance, protocol security,
   deployment approval, and Orange semantic or professional-readiness claims.

## Completion criteria

Use the [rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. A passing submission must:

- satisfy **FRM-104-01** with complete game syntax, finite adversary class,
  interfaces, win event, advantage convention, bounds, and quantifiers;
- satisfy **FRM-104-02** with reviewable adjacent hops, a correctly directed
  reduction, explicit assumptions/resources/losses, and exact concrete
  accounting;
- satisfy **FRM-104-03** with an independent bounded enumerator, endpoints,
  relational and deliberate-failure evidence, pre-registered sampling, and
  reproducible claim classification; and
- keep every conclusion within the finite model or clearly conditional theorem
  actually established.

An incomplete probability space, ambiguous win event, skipped invalid query,
reversed reduction, omitted resource loss, empirical frequency used as an
exact probability, green tests called a general proof, or any Orange or real
cryptographic construction claim cannot pass.
