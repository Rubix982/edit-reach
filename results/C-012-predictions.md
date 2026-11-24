# C-012 — predicted, before any count was read

Committed before the runner was written. [T-017] asks whether the adapter's longest-candidate rule manufactures any published rate. The counts that answer it are not yet known to anyone here.

## The two restrictions, which are not the same experiment

The adapter gathers subject-shaped strings from all six test types, takes the **longest as the canonical subject**, and passes **the rest on as aliases**. So restricting the candidate pool does two separable things, and lumping them would answer a question nobody asked.

- **R1 — restrict the canonical pick only.** The canonical subject is chosen from the five non-aliasing types; every candidate, aliasing ones included, is still passed on as an alias. This removes the circularity exactly: the screen can no longer report a prompt as naming the subject because it read the name out of that prompt. **R1 is the counterfactual the published rates should be judged against.**
- **R2 — restrict the whole pool.** Aliasing prompts contribute nothing, canonical or alias. This also throws away genuine name variants that `Subject_Aliasing` exists to supply, so a fall in the alias rate under R2 is the restriction working as designed rather than evidence about the published numbers.

## Predictions, R1

| # | Quantity | Predicted |
| --- | --- | --- |
| 1 | Coverage (entries with a recoverable subject) | **Falls, by ≤3 points per subset.** Some entries offer a candidate only through an aliasing prompt, and those entries are now skipped. |
| 2 | `Subject_Aliasing` strict rate | **Falls sharply**, to roughly 0.05–0.12 from 0.163 / 0.265 / 0.114. This is the 682 circular hits going away and is the one number expected to move a lot. |
| 3 | Per-subset strict rate | **Falls by ≤2 points** on each of `recent` / `random` / `popular`. The circular hits are 1.8% of all prompts screened. |
| 4 | Per-subset alias rate | **Moves by <0.5 points.** This is §5.8's stated expectation and the reason this card exists: those prompts should read as a variant match whichever string is canonical. |
| 5 | The five non-aliasing per-type strict rates | **Each moves by <1 point.** Their canonical label rarely comes from an aliasing prompt in the first place. |

## Branches, fixed in advance

- **If 3 and 4 hold** — no published rate outside `Subject_Aliasing` moves by more than its stated precision — the circularity is confined to the one test type, §5.8's expectation is confirmed with a number, and limitation 14 stands as written with its scope now measured rather than argued.
- **If 3 or 4 fails** — a subset rate moves materially — the published table is partly manufactured, and §5.8 reports the restricted-pool number beside the released-pool one, with this card as the reason.
- **If 1 fails badly** — coverage falls more than 3 points — the restriction is not free, the trade is coverage against circularity, and the right report names both rather than picking one. The 80.3% coverage figure in `editscreen`'s own documentation would then need a second number beside it.

## What is affected either way

`web/notebook/edit-reach/paper.md` §5.8's per-subset table, its per-test-type table, limitation 14, and finding F-17's falsifier thresholds. `editscreen`'s `validation/README.md`, which currently records the circularity and says it is left unfixed. Nothing measured on MQuAKE is touched: MQuAKE hands the screen a subject string and has no recovery step.
