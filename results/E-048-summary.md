# E-048 · Two MQuAKE variants differ 40-fold in how often a question names the edited entity

_2026-11-23 · 42,258 questions across three released MQuAKE files · no model, no gradients, laptop, seconds · `editscreen` 0.2.0a1 at commit 0893bfc, `matcher_version` 0.1.0_

## Why this was run

[E-038] found, on RippleEdits, that the items naming the edited subject are the items where the edit sits on the first hop. That was one benchmark, and the hop position had to be inferred. MQuAKE is a second benchmark, built by different authors for a different purpose, and it carries the hop chain explicitly in `orig.triples_labeled` — so the same question can be asked without inferring anything.

The screen needs no model, no gradient and no edit, so it runs on a laptop and is unaffected by the `v*` gradient failure that blocks [E-043] and [E-047].

## The result

| file | questions | names an edited entity |
| --- | ---: | ---: |
| MQuAKE-T | 5,604 | **1.6%** |
| MQuAKE-CF-3k | 9,000 | **67.8%** |
| MQuAKE-CF | 27,654 | **67.2%** |

Two files published under one benchmark's name, differing by a factor of forty on whether the question hands the model the entity whose fact was changed.

## What explains it, and why it is not a discovery

The chain head — `triples_labeled[0][0]` — is the entity a multi-hop question starts from. Split the questions by whether the case edits that entity:

| file | cases editing the head | head edited → names it | only later hops edited → names it |
| --- | ---: | ---: | ---: |
| MQuAKE-T | 0.4% | 21/21 = **100%** | 67/5,583 = 1.2% |
| MQuAKE-CF-3k | 65.1% | 5,852/5,859 = **99.9%** | 249/3,141 = 7.9% |
| MQuAKE-CF | 64.8% | 17,917/17,922 = **100%** | 678/9,732 = 7.0% |

**The right-hand column is near-tautological and should be read as such.** A multi-hop question has to name the entity it starts from, or it cannot be traversed; the chain head is that entity. So "the head was edited" and "the question names an edited entity" are close to the same statement, and the ~100% is suspiciously clean for exactly that reason. Reporting it as an empirical regularity would be dressing a structural property as a finding.

**What is not tautological is the left-hand column.** `MQuAKE-CF` places the edit at the chain head in about 65% of cases; `MQuAKE-T` does so in 0.4%. That is a choice made during construction, it differs enormously between two files shipped under one name, and it accounts for the whole of the 1.6%-vs-67.8% gap without any further assumption. The claim this run supports is a claim about how the two corpora were built.

The later-hop column is **not** zero — 7.0% and 7.9% on the counterfactual files. Those are questions that happen to name a mid-chain entity that was also edited. Small, real, and the reason the explanation above is "accounts for" rather than "equals".

## What would have made this come out differently

Exposure roughly equal in both columns would have said that naming the subject is a property of MQuAKE's phrasing in general rather than of where the edit landed, and the [E-038] reading would not transfer. It is not what happened, but the comparison was the point of running it.

## Limits

**This was not pre-registered.** The cross-tabulation was written after four verdicts had been read by hand while building the adapter, so the direction was known before the number was. It is a measurement that can now be repeated, not a prediction that was risked.

**The matchers are unvalidated.** No precision or recall exists for them, so every rate here inherits an unmeasured error. This is the gap that `editscreen` states in its own README and changelog, and nothing above should be quoted as a benchmark statistic until it closes.

**`STRICT` is a lower bound.** A question identifying the entity by description without naming it is counted clean, so the true exposure is higher than reported, never lower.

**Equality of subject strings is how "the head was edited" is decided.** A case that rewrites the head entity under a different surface form than `triples_labeled` uses would be counted as later-hop. No attempt was made to resolve entities, so the head-edited share is itself a lower bound.

**It says nothing about accuracy.** Whether a model answers these questions correctly, and whether exposure inflates that, is not measured here and cannot be — this never sees a model's output.

## Reproducing

```bash
.venv/bin/python agents/engineer/workspace/run_e048_mquake_exposure.py
```

Input hashes, the `editscreen` commit, the matcher version and the interpreter are recorded in `results/E-048-mquake-exposure.json`. The MQuAKE files live in `edit-slice`, not here; pass `--data` to point elsewhere.
