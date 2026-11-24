# T-020 — batching moves individual verdicts and does not move the aggregate

**Answered 2026-11-24.** Predictions in `T-020-predictions.md`, committed at `afb3a4a` before the runner was written. Three of four held; the one that failed, failed because its reasoning was wrong rather than its threshold.

Run: `python3 agents/engineer/workspace/run_t020_batch_stability.py`. 240 fixed pairs from `val`, target `Continent`, counterfactual `prompt_template_counterfactual`, layer 5, 6 generated tokens, Llama-3.1-8B over NDIF. Output: `results/T-020-batch-stability.json`.

## The result

| batch | IIA | unintervened | wall |
| ---: | ---: | ---: | ---: |
| 16 | 0.2667 | 0.6917 | 774s |
| 48 | 0.2667 | 0.6833 | 375s |
| 120 | **0.2625** | 0.6875 | 219s |

**Aggregate spread 0.42 points, against a sampling 95% half-width of 6.33 at n=240.** The aggregate does not move.

Per-example disagreement is smaller than it was worth predicting:

| comparison | disagree | became correct | became wrong |
| --- | ---: | ---: | ---: |
| 16 vs 48 | **0** of 240 | 0 | 0 |
| 16 vs 120 | 1 of 240 (0.4%) | 0 | 1 |
| 48 vs 120 | 1 of 240 (0.4%) | 0 | 1 |

Batch 16 and batch 48 agree on **every one of 240 examples**. Only batch 120 differs, on one.

## Scorecard

| # | Predicted | Outcome |
| --- | --- | --- |
| 1 | Aggregate spread within ±5.7 points | **Held, with room.** 0.42 against a 6.33 half-width. |
| 2 | Unintervened spread smaller than IIA's | **Failed.** 0.84 against 0.42 — the wrong way round. |
| 3 | Disagreement non-zero, single-digit percent | **Held in direction, over-pessimistic.** 0.0% and 0.4%, below the predicted range. |
| 4 | No systematic direction | **Held, and untested.** The one flip went the same way in both comparisons, but one example is not a direction. |

**Why 2 failed, and it is a fault in the prediction rather than a finding about the model.** The prediction said *"no vector is transplanted on that arm, so only the clean forward pass varies."* That is false about this runner. The unintervened column is generated through **the same patched path**, written with the vector already at that site, precisely so a difference between the columns is the intervention and not the decoding. So both arms carry an identical write and are equally exposed to batching noise, and there was never a reason to expect one to be quieter. Writing the prediction down is what made that visible.

## What it licenses, and what it does not

- **The aggregate is the quantity, and batch size is configuration.** [C-009] may use whatever batch size is affordable, recording it alongside the serving device as [C-006] requires.
- **Per-example verdicts remain unquotable**, which was already the rule and is now a measured one rather than a precaution.
- **It does not license a batch size above 120.** Everything here is measured at 16, 48 and 120; batch 16 and 48 are identical and only 120 shows a flip, which is a hint that disagreement grows with batch size rather than evidence about 256 or 512. MIB's own Llama eval batch is 256. If a run wants that, this check is cheap to repeat there.
- **It says nothing about other layers or other counterfactual types.** Layer 5 is the one this project edits at, which is why it was chosen, but a near-boundary example is a property of the layer as much as of the batch.

## One number worth not over-reading

IIA at layer 5 for Continent is **0.2625–0.2667**, against MIB's Full Vector row of 53 averaged across layers and 62 at its best. These are not comparable yet and nothing should be concluded from the gap: this is a single early layer, a single counterfactual type, and — the big one — **no filtering**. MIB keeps every example of the target attribute and half of each other, and filters to what the model answers correctly unintervened. Here the unintervened accuracy is **0.69**, so roughly a third of the denominator is examples the model gets wrong before anything is patched. That is the next thing to build and the reproduction cannot be attempted before it exists.
