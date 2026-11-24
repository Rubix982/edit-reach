# E-048 · Two MQuAKE variants differ by more than a hundredfold in how often a question names the edited entity

_Revised 2026-11-24 · 42,258 questions across three released MQuAKE files · no model, no gradients, laptop, seconds · `editscreen` 0.2.0a2 at commit 3bb1c9e, `matcher_version` 0.2.0_

**This revises the 2026-11-23 version, which reported a 40-fold gap.** The matchers were unvalidated then. They have since been measured against 261 hand-labelled items, the derived-alias rule was found to be right 57% of the time, and it was fixed. The gap is larger than first reported, not smaller, and the correction is set out under "What changed" below.

## Why this was run

[E-038] found, on RippleEdits, that the items naming the edited subject are the items where the edit sits on the first hop. That was one benchmark, and the hop position had to be inferred. MQuAKE is a second benchmark, built by different authors for a different purpose, and it carries the hop chain explicitly in `orig.triples_labeled` — so the same question can be asked without inferring anything.

The screen needs no model, no gradient and no edit, so it runs on a laptop and is unaffected by the `v*` gradient failure that blocks [E-043] and [E-047].

## The result

Two rates per file. The first counts only questions containing the edited subject's own surface form; the second adds matches on a name variant. Quote the first.

| file | questions | names it outright | including name variants |
| --- | ---: | ---: | ---: |
| MQuAKE-T | 5,604 | **0.37%** | 0.82% |
| MQuAKE-CF-3k | 9,000 | **65.4%** | 67.0% |
| MQuAKE-CF | 27,654 | **65.0%** | 66.4% |

Two files published under one benchmark's name, differing by a factor of **177** on whether the question hands the model the entity whose fact was changed.

*Added 2026-11-24, from C-010:* all three RippleEdits subsets screen at 51.9–79.6% on the same rule, which is MQuAKE-CF's range. **The gap is a property of these two MQuAKE files, not a spread across propagation benchmarks.** No rate on this page changes.

## What explains it, and why it is not a discovery

The chain head — `triples_labeled[0][0]` — is the entity a multi-hop question starts from. Split the questions by whether the case edits that entity:

| file | cases editing the head | head edited → names it | only later hops edited → names it |
| --- | ---: | ---: | ---: |
| MQuAKE-T | 0.4% | 21/21 = **100%** | 25/5,583 = 0.4% |
| MQuAKE-CF-3k | 65.1% | 5,852/5,859 = **99.9%** | 174/3,141 = 5.5% |
| MQuAKE-CF | 64.8% | 17,917/17,922 = **100%** | 448/9,732 = 4.6% |

**The right-hand column is near-tautological and should be read as such.** A multi-hop question has to name the entity it starts from, or it cannot be traversed; the chain head is that entity. So "the head was edited" and "the question names an edited entity" are close to the same statement, and the ~100% is suspiciously clean for exactly that reason. Reporting it as an empirical regularity would be dressing a structural property as a finding.

**What is not tautological is the left-hand column.** `MQuAKE-CF` places the edit at the chain head in about 65% of cases; `MQuAKE-T` does so in 0.4%. That is a choice made during construction, it differs enormously between two files shipped under one name, and it accounts for the whole of the gap without any further assumption. The claim this run supports is a claim about how the two corpora were built.

The later-hop column is **not** zero — 4.6% and 5.5% on the counterfactual files. Those are questions that happen to name a mid-chain entity that was also edited. Small, real, and the reason the explanation above is "accounts for" rather than "equals".

## What changed, and why the first version was wrong

The 2026-11-23 run used `matcher_version` 0.1.0 and quoted a single combined rate: 1.6% on MQuAKE-T against 67.8% on MQuAKE-CF-3k, a 43-fold gap.

261 items were then labelled by hand against a stratified draw. The strict rule — the subject's own surface form, on word boundaries — was right in every case. The derived-alias rule, which guesses variants from the subject string, was right **57.1% [45.1, 69.0]** of the time. It fired on names reduced to a generic word, matching "country music" against "a genre of music", and on the tail of a different person's name, matching "Nicolae Ceaușescu" when the edited subject was Elena. Both are fixed in `editscreen` 0.2.0; on a held-out draw the rule is now right **90.2% [80.5, 97.6]**.

What this did to the numbers is the part worth keeping:

| | MQuAKE-T | MQuAKE-CF-3k | gap |
| --- | ---: | ---: | ---: |
| strict only, before and after | 0.37% | 65.4% | 177× |
| strict + alias, before | 1.57% | 67.8% | 43× |
| strict + alias, after | 0.82% | 67.0% | 82× |

**The strict row did not move.** The rate built on the rule that cannot be argued with was identical before and after a correction that shifted everything quoted beside it, because MQuAKE-T's flagged items were mostly alias matches and four in ten of those were wrong. That is the argument for the headline being the strict rate, and it is the first evidence for it that did not come from reasoning about the rule in the abstract.

## What would have made this come out differently

Exposure roughly equal in both columns would have said that naming the subject is a property of MQuAKE's phrasing in general rather than of where the edit landed, and the [E-038] reading would not transfer. It is not what happened, but the comparison was the point of running it.

## Limits

**This was not pre-registered.** The cross-tabulation was written after four verdicts had been read by hand while building the adapter, so the direction was known before the number was. It is a measurement that can now be repeated, not a prediction that was risked.

**The labels behind the matcher precision were produced by a model, not a person.** A random 25-item subset has been drawn for a human to label blind, and is not yet filled in. Until it is, the precision figures above carry one unmeasured error rate of their own, and the honest reading of "100% precision for strict" is "100% agreement with one labeller".

**Neither rate bounds identification.** Hand-labelling found the edited subject identifiable from the probe in essentially every item of both files — MQuAKE renders its questions from the chain the edit sits on, so the subject is picked out whether it is named or not. What these rates measure is whether the question hands the model the **name**. That is a surface property, it is the one a model can exploit without reasoning, and it is a different question from identifiability.

**Equality of subject strings is how "the head was edited" is decided.** A case that rewrites the head entity under a different surface form than `triples_labeled` uses would be counted as later-hop. No attempt was made to resolve entities, so the head-edited share is itself a lower bound.

**It says nothing about accuracy.** Whether a model answers these questions correctly, and whether naming the subject inflates that, is not measured here and cannot be — this never sees a model's output.

## Reproducing

```bash
.venv/bin/python agents/engineer/workspace/run_e048_mquake_exposure.py
```

Input hashes, the `editscreen` commit, the matcher version, the measured matcher precision and the interpreter are recorded in `results/E-048-mquake-exposure.json`. The MQuAKE files live in `edit-slice`, not here; pass `--data` to point elsewhere.
