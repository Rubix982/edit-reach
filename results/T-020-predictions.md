# T-020 — predicted, before any count was read

Committed before the runner was written. The question is whether batching, which [C-009] needs to be affordable at all, moves the quantity the card reports or only the individual verdicts underneath it.

## What is already measured

A source vector read alone and inside a batch of six differs by up to **0.0078**, which is bfloat16 granularity. The clean next-token prediction is identical batched or alone and the entity position check passes, so this is reduction order rather than misalignment. It flipped one example: `Portsmouth <- Abau`, asked for a language, answers `English` at batch 1 and `Tok Pisin` at batch 6 — the base city's answer against the patched city's, contested and decided by noise.

## The design

One fixed set of **240 pairs**, taken in release order from `val`, target `Continent`, counterfactual `prompt_template_counterfactual`, layer 5, 6 generated tokens. Scored three times at batch sizes **16, 48 and 120**. Same pairs, same order, same everything else; only the batch size moves.

## Predictions

| # | Quantity | Predicted |
| --- | --- | --- |
| 1 | Spread in aggregate IIA across the three batch sizes | **Within ±5.7 points**, the binomial 95% half-width at n=240 near p=0.5. The flips should be symmetric, so the mean should barely move. |
| 2 | Spread in the unintervened accuracy across batch sizes | **Smaller than 1's.** No vector is transplanted on that arm, so only the clean forward pass varies, and that was measured identical batched or alone at the last token. |
| 3 | Per-example disagreement between any two batch sizes | **Non-zero, and in the single-digit percents.** One flip was already found by hand in six examples, but near-boundary examples should be a small minority. |
| 4 | Direction | **No systematic direction.** A larger batch should not raise or lower IIA; if it does, something other than arithmetic noise is going on. |

## Branches, fixed in advance

- **If 1 holds** — the spread is inside the sampling interval — the aggregate is the quantity, batch size is recorded as configuration like the serving device, and C-009 may use whatever batch size is affordable. Per-example verdicts stay unquotable.
- **If 1 fails** — the aggregate moves more than sampling noise — then batch size is an experimental variable rather than a configuration detail, every published number must name it, and the reproduction against Table 3g has to be run at a single fixed batch size with that stated.
- **If 4 fails** — the movement has a direction — the cause is not bfloat16 reduction order and the runner is wrong somewhere. That closes this thread on a defect rather than a measurement, and C-009 stops until it is found.

## What is affected

[C-009]'s every future number, and nothing already published: no result from this runner has been quoted anywhere.
