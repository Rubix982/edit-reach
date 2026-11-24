# C-011 · Five of the six test types screen the way their definitions say they should, and the sixth agrees for the wrong reason

_2026-11-24 · 38,092 test prompts across RippleEdits' three released subsets · no model, no gradients, laptop, seconds · `editscreen` 0.2.0a4 at commit 6d05d49, `matcher_version` 0.2.0_

## The question

[C-010] measured the screen's precision stratified by **subset**. Stratified instead by RippleEdits' own six declared test types, the same run produced two numbers nobody had explained: `Compositionality_II` screening at essentially zero, and `Subject_Aliasing` low on the strict rule but high once name variants count.

Either the benchmark is doing what it says it does, or the adapter is recovering the wrong string. The adapter takes the **longest candidate across all six types**, and two of those types name a different entity on purpose — so a label that is right for the entry can still be the wrong string to look for in one type's prompts.

## What was done

The six definitions were read out of the benchmark's own paper (Cohen et al., TACL 2024, arXiv 2307.12976) and each one's prediction written down and committed **before any count was read** — `results/C-011-predictions.md`, commit `8e7d69a`. Then the screen was run over every test prompt of every recoverable entry in all three subsets, and the counts compared to the predictions.

No labels were added. This card compares a stated prediction to a count; it does not measure precision, and it makes no fourth model-labelled draw while two blind human subsets sit unfilled.

## The result

| test type | the query is about | predicted | `recent` | `random` | `popular` |
| --- | --- | --- | ---: | ---: | ---: |
| `Compositionality_I` | the edited subject | high | 0.989 | 0.656 | 0.868 |
| `Relation_Specificity` | the edited subject | high | 0.891 | 0.660 | 0.729 |
| `Forgetfulness` | the edited subject | high | 0.965 | 0.997 | 0.973 |
| `Logical_Generalization` | the subject, the old object or the new one | between the two | 0.621 | 0.451 | 0.402 |
| `Subject_Aliasing` | an alias of the subject | low on strict | 0.163 | 0.265 | 0.114 |
| `Compositionality_II` | a different entity that has the subject as its object | near zero | 0.011 | 0.000 | 0.018 |

Strict rule, over test prompts. **Every prediction holds.** The three types whose queries are about the edited subject sit at the top, the one whose queries are about a different entity sits at the bottom, and the mixed type sits between them in all three subsets. `Subject_Aliasing` rises from 0.114–0.265 on the strict rule to 0.622–0.904 once name variants count, which is the test type doing exactly what it is built to do.

**So the two numbers that opened [T-016] are the benchmark working as written, not the adapter failing.** That question needed the definitions read, not a new draw.

**One name had to be matched up, and it was checked rather than assumed.** The paper's sixth criterion is **Preservation**; the released files carry **`Forgetfulness`** and no `Preservation`. All 1,227 `Forgetfulness` prompts in `recent` carry the *"which is not"* clause that the paper gives as Preservation's example phrasing, so the two are the same criterion under two names. That clause is also where [C-010]'s 28 malformed recoveries came from.

## Two things the counts turned up that the predictions did not

**`Compositionality_II` is not clean, it is 99.1% clean.** 20 of its 2,285 prompts name the edited subject on the strict rule. Every one is a real string in the prompt, and they split two ways. **Nine name the subject outright**, because the chain runs through them — *"the name of the paternal grandfather of **Lucius Julius Caesar** is"*, *"the capital city of the country **Kingdom of England** is associated with"*. **Eleven carry the subject's name inside a different entity's name**: *"the father of **Jacques Genest** jr."*, *"the child of the founder of **Axel Springer** SE"*, *"the siblings of the screenwriter of **Michael Jackson**'s Thriller"*. A son, a company and a film, each named after the person whose fact was edited.

Both kinds put the edited name in front of the model, which is what the screen claims to detect, so neither is a precision failure. What the second kind is not is an item *about* the edited subject — and no draw stratified by subset would ever have sampled 20 items out of 38,092, which is the sense in which [C-010]'s "the strict rule has not been seen to be wrong" is narrowed by this page rather than contradicted by it.

**Most of `Subject_Aliasing`'s strict hits are circular, and the proportion is not stable.** The adapter recovers the subject as the longest candidate across all six types, so when the longest string an entry offers is an alias lifted out of an aliasing prompt, the screen then reports that same prompt as naming the subject. It read the name out of the prompt and then found it there.

| subset | `Subject_Aliasing` strict hits | recovered from an aliasing prompt | independent |
| --- | ---: | ---: | ---: |
| `recent` | 190 | 64 (34%) | 126 |
| `random` | 621 | **483 (78%)** | 138 |
| `popular` | 256 | 135 (53%) | 121 |

So this type's count matches its prediction for the wrong reason, and it is the one place in the six where the number is a property of the adapter rather than of the corpus. It is 682 prompts out of 38,092 — 1.8% — and it inflates `Subject_Aliasing`'s strict rate, not the alias rate, because those prompts would have read ALIAS anyway.

## What this changes under a number published earlier today

**The three headline rates are over test prompts, not entries**, and §5.8 of the paper page said entries. The denominators are **16,315 / 11,731 / 10,046** prompts, belonging to the 1,461 / 1,633 / 724 entries whose subject could be recovered out of 1,948 / 1,922 / 885. No rate moves — 79.6% / 51.9% / 56.4% are what they always were — but the column that said what they were computed over was wrong, and the page is corrected.

## What it does not license

**No per-type precision.** This card compares a count to a stated prediction. It cannot say how often the screen is right on a given type, and a figure for that would need a draw stratified by type and a second labeller — which is worth doing only after the agreement rate on the 441 items already drawn exists.

**Nothing about whether an edit worked.** As with every rate from this screen, it measures how an evaluation item was written.

**Nothing about `Compositionality_I` as a propagation test beyond the string.** [E-041] measured what those items receive of the update; this measures only whether the name is in them.

## Reproducing

```
python3 agents/engineer/workspace/run_c011_test_types.py
```

Reads the three released subsets, writes `C-011-ripple-by-test-type.json` and `C-011-denominators.json`. No model, no network.
