# Lab: audit a finite archive-challenge game

## Goal

Define and audit a finite probabilistic game, justify one real-to-ideal hop,
evaluate a conditional concrete bound, and preserve exact and sampled evidence
without calling either a general cryptographic proof.

## Setup

From the repository root, record the baseline in a fresh shell:

~~~sh
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 curriculum/modules/frm-104/examples/worked_game.py
worked_status=$?
PYTHONDONTWRITEBYTECODE=1 python3 curriculum/modules/frm-104/checks/lab_smoke.py
smoke_status=$?
printf 'worked=%s smoke=%s\n' "$worked_status" "$smoke_status"
~~~

The last command must report both statuses as zero, and the smoke command must
print <code>frm-104 lab smoke: PASS</code>. Create an isolated workspace and
copy the example files:

~~~sh
workdir="$(mktemp -d)"
cp -R curriculum/modules/frm-104/examples "$workdir/"
cd -- "$workdir"
pwd
~~~

Record the absolute directory. Use Python 3.11 or newer and only the standard
library. Do not fetch a package, implement cryptography, or use real secrets.

## Tasks

1. **Write <code>game-contract.md</code>.** Define the archive-challenge toy
   scenario independently. A challenger selects a uniform red/blue bit. At a
   bounded trigger probability the real world reveals that bit, while the
   ideal world supplies an independent bit. State parameter ranges, all random
   variables and distributions, state, view grammar, adversary call and
   output, win event, one-half baseline, absolute advantage convention, and
   exact quantifier order. State time, memory, query, and sample-space bounds.
   Explain why this game is not a confidentiality definition for an archive.
2. **Create <code>adversaries.csv</code>.** Enumerate all eight deterministic
   mappings from the three possible views to a guess. Assign each a stable ID.
   For trigger probabilities 0, 1/16, 8/16, and 16/16, record exact real and
   ideal wins, trials, win probabilities, and advantages for every strategy.
   Identify the worst advantage in each game without generalizing beyond this
   finite strategy class.
3. **Create <code>lab_games.py</code>.** Import <code>game_model</code> from the
   copied <code>examples</code> directory through an explicit local path. Render
   the table deterministically with <code>Fraction</code> values. Assert that
   real and ideal probabilities agree when the trigger is impossible, the
   copy strategy's real advantage equals half the trigger probability, every
   ideal advantage is zero, and the observed adjacent gap never exceeds the
   trigger bad-event bound. Exit nonzero if any relation fails.
4. **Write <code>hop-ledger.md</code>.** Show the exact single change between
   real and ideal. Define the coupled sample space, bad event, and inequality.
   State which game's bad probability is used. Distinguish the observed finite
   gap from its looser upper bound. Add a hypothetical second hop based on a
   named primitive assumption, but do not claim the supplied model proves that
   assumption. Give the reduction algorithm's input, adversary simulation,
   output translation, runtime/query overhead, success relation, aborts, and
   direction of the final inequality.
5. **Create <code>bound-worksheet.csv</code>.** Use columns
   <code>term,formula,parameters,exact_value,justification,evidence_type,scope</code>.
   Evaluate a supplied primitive term of <code>1/1,000,000</code>, a collision
   union bound for <code>q=32,N=65,536</code>, and a mathematical simulation
   term of zero. Sum exact fractions and state whether the total is useful
   under this module's maximum bit-guessing advantage. Also calculate the
   endpoints <code>q=0</code>, <code>q=4,096</code>, and one invalid
   <code>q=4,097</code> attempt. Never call the union bound the exact collision
   probability.
6. **Pre-register and run a sample.** Before execution, write
   <code>sample-plan.md</code> with game, strategy, seed 41, 10,000 trials,
   estimator, exact comparison target, and a statement that no seed will be
   retried. Run it once and preserve stdout, stderr, and status separately.
   Report the frequency and absolute estimation error. Do not convert the
   sample into a proof, confidence claim, or source of the exact probability.
7. **Create <code>test_lab_games.py</code>.** Use <code>unittest</code> to test
   the normal example, denominator 64, denominator 65 rejection, numerator
   endpoints and one beyond, all eight strategies, zero-bad equivalence,
   copy-strategy algebra, collision-bound query and space endpoints and one
   beyond, strict Boolean/integer behavior, deterministic seeded replay, and
   simulation-trial endpoint and one beyond. A test of a false
   <code>1/8</code> advantage for the <code>p=1/8</code> case must fail. Preserve
   that failure, repair the expectation to <code>1/16</code>, and preserve the
   passing rerun.
8. **Write <code>evidence-ledger.md</code>.** Record Python version, absolute
   workspace, source-file SHA-256 values, exact commands, stdout, stderr,
   immediate statuses, finite sample-space sizes, loop bounds, and output-file
   identities. Classify each claim as definition, exact model result,
   conditional reduction step, mathematical bound, unit test, empirical
   sample, or unsupported. Explicitly reject claims of general adversary
   security, primitive security, proof-assistant verification, implementation
   correctness, side-channel resistance, deployment approval, and Orange
   behavior.

## Verification

From the isolated workspace run:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 lab_games.py
model_status=$?
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_lab_games.py
test_status=$?
printf 'model=%s tests=%s\n' "$model_status" "$test_status"
~~~

Both statuses must be zero after the deliberate failure has been preserved and
repaired. Review the submission manually and confirm that:

- every probability is over a stated finite sample space;
- all eight deterministic strategies and every requested endpoint ran;
- the hop changes one declared distribution and uses the right inequality;
- the reduction direction upper-bounds target advantage and accounts for
  resources and aborts;
- every concrete term has a source and scope;
- exact enumeration and sampling have different labels;
- one-beyond inputs are rejected before excess work; and
- the final claims do not exceed the retained evidence.

Rerun the repository smoke check from the repository root. A passing learner
test does not replace independent smoke evidence.

## Reflection

Write five to eight sentences answering these prompts:

- Which quantifier in your finite result differs most from a cryptographic
  security definition?
- Why is the real-to-ideal gap smaller than the bad-event bound for the copy
  strategy?
- What would make a formally correct concrete bound vacuous?
- Which reduction resource was easiest to omit?
- What did the seed make reproducible, and what did it not make exact?
- Which deliberately false claim failed, and why was that failure important?
- What additional formalization and implementation evidence would be needed
  before relating the method to a real language or system?
