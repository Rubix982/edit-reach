# C-012 — the strict/variant split on RippleEdits is not robust to the recovery rule, and their union is

**Closed 2026-11-24 on branch 2 of three, which was the branch nobody expected.** Predictions in `C-012-predictions.md`, committed at `6786538` before the runner was written. Three of the five failed, and two of them failed in the direction opposite to the one §5.8 of the paper asserted.

Run: `python3 agents/engineer/workspace/run_c012_candidate_pool.py`. No model, no gradients, no network. Output: `results/C-012-candidate-pool.json`.

## What was run

The adapter gathers subject-shaped strings from all six test types, takes the **longest as the canonical subject**, and passes **the rest on as aliases**. Three scorings of all three released subsets:

- **released** — as shipped.
- **R1** — canonical pick restricted to the five non-aliasing types; every candidate still passed on as an alias. Removes the circularity and nothing else.
- **R2** — whole pool restricted. Also discards genuine variants, so its alias rate falling is the restriction working as designed.

## The result

| subset | | entries covered | prompts | names it outright | including variants |
| --- | --- | ---: | ---: | ---: | ---: |
| recent | released | 75.0% | 16,315 | 0.796 | 0.898 |
| | **R1** | 74.9% | 16,311 | **0.820** | **0.898** |
| random | released | 85.0% | 11,731 | 0.519 | 0.902 |
| | **R1** | 80.1% | 11,353 | **0.707** | **0.905** |
| popular | released | 81.8% | 10,046 | 0.564 | 0.851 |
| | **R1** | 79.5% | 9,843 | **0.662** | **0.849** |

**The strict rate rose, by 2.4, 18.8 and 9.8 points.** The paper said the longest-candidate rule inflates a rate. On every subset it was suppressing one.

**The union did not move: 0.0, +0.3 and −0.2 points.** Every prompt that changed verdict moved between STRICT and ALIAS inside the same flagged set. That is the finding. The screen's "names it outright" / "names a variant" boundary on this corpus is set by which string the recovery happens to pick; whether the prompt is flagged at all is not.

**The mechanism.** The longest candidate an entry offers is often a long formal variant lifted out of an aliasing prompt — `Theodore Vonkurnatowski` where the entry's other prompts all say `Theo Vonkurnatowski`. Made canonical, it matches none of them, so prompts that do carry a name of the subject read ALIAS instead of STRICT. R1 picks the name the non-aliasing prompts actually use. Entries relabelled by R1: 62 of 1,948 on `recent` (3.2%), **383 of 1,922 on `random` (19.9%)**, 113 of 885 on `popular` (12.8%) — which is why `random` moved four times as far as `recent`.

## Per test type, strict rate

| Test type | recent | | random | | popular | |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| | released | R1 | released | R1 | released | R1 |
| Compositionality I | 0.989 | 1.000 | 0.656 | 0.999 | 0.868 | 0.994 |
| Relation Specificity | 0.891 | 0.938 | 0.660 | 0.804 | 0.729 | 0.878 |
| Forgetfulness | 0.965 | 1.000 | 0.997 | 1.000 | 0.973 | 0.997 |
| Logical Generalization | 0.621 | 0.643 | 0.451 | 0.930 | 0.402 | 0.622 |
| Subject Aliasing | 0.163 | 0.129 | 0.265 | 0.173 | 0.114 | 0.072 |
| Compositionality II | 0.011 | 0.013 | 0.000 | 0.001 | 0.018 | 0.020 |

[C-011]'s ordering survives in both columns: the three types about the edited subject on top, the mixed one between, the one about a different entity at the bottom. **The ordering is robust to the recovery rule; the levels are not.** `random`'s Logical Generalization moves 0.451 → 0.930.

## Which rule is right, as far as 33 cases can say

Where the two rules pick different canonical strings and the entry's Wikidata item is one of the 170 already resolved for [C-010], the label adjudicates:

| | n |
| --- | ---: |
| R1 matches Wikidata, released does not | 6 |
| released matches Wikidata, R1 does not | 1 |
| both match (the disagreement is between two acceptable names) | 24 |
| neither matches | 2 |

**Six to one for R1, over 33 adjudicable cases, with 24 of them ties.** That is directional and it is not a precision measurement. The 180-item labelled set was drawn stratified by the *released* rule's verdicts, so it cannot be reweighted to score R1, and no held-out draw exists under R1. **R1's precision is unmeasured.** What this card establishes is that the two rules disagree materially and that the released one is not the better of the two where they can be checked — not that R1's numbers are the right ones to publish.

## Scorecard against the predictions

| # | Predicted | Outcome |
| --- | --- | --- |
| 1 | Coverage falls ≤3 points per subset | **Failed on `random`** — 85.0% → 80.1%, a 4.9-point fall. Held on `recent` (0.1) and `popular` (2.3). |
| 2 | Subject Aliasing strict falls sharply, to ~0.05–0.12 | **Held in direction, missed the range.** 0.163→0.129, 0.265→0.173, 0.114→0.072. |
| 3 | Per-subset strict falls by ≤2 points | **Failed, and in the opposite direction.** It rose by 2.4, 18.8, 9.8. |
| 4 | Per-subset alias rate moves <0.5 points | **Held.** 0.0, +0.3, −0.2. |
| 5 | The five non-aliasing per-type rates each move <1 point | **Failed badly.** `random`'s Logical Generalization moved 47.9 points. |

Prediction 4 was the one §5.8 had already asserted in prose, and it is the one that held. Predictions 3 and 5 came from treating the circularity as the whole of what the recovery rule does to the counts. It is the smaller half.

## What changes

- **§5.8's per-subset table.** Its RippleEdits "names it outright" column is rule-dependent. The "including variants" column is not, and is now the column to quote for that corpus.
- **Limitation 14 is wrong as written.** It says one per-type rate is inflated by the screen. The inflation is real for `Subject_Aliasing` and is the smaller effect; the larger one is suppression of four other types' rates, and of the subset rate itself.
- **Nothing on MQuAKE moves.** MQuAKE hands the screen a subject string and has no recovery step, so the 177-fold finding and both MQuAKE rows are untouched.
- **[F-17] survives.** Under R1 the three subsets read 82.0 / 70.7 / 66.2%, still inside MQuAKE-CF's range, so *all three RippleEdits subsets sit beside the contaminated file* holds under both rules.
- **`editscreen` is not changed by this card.** Switching the released rule to R1 would move a documented 80.3% coverage figure and publish a canonical-pick rule whose precision has never been measured. The fix is a measurement, not an edit: draw a held-out set under R1 and score it. [T-019].
