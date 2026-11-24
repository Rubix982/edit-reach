# C-010 · The strict rule survives a benchmark that does not hand it the subject

_2026-11-24 · 180 hand-labelled RippleEdits items · no model, no gradients, laptop, seconds · `editscreen` 0.2.0a4 at commit 3a2d4c8, `matcher_version` 0.2.0_

## The question, and why the earlier 100% did not answer it

`editscreen`'s strict rule had been measured on 261 MQuAKE items and was right every time. That number could not be carried over to RippleEdits, and the reason is not that RippleEdits is harder.

**MQuAKE hands the screen its subject as a string.** The record says the edited subject is "Henry Mackenzie" and the rule asks whether that string is in the probe. The only way a strict hit can be wrong there is a bad word boundary, which is why 100% is close to definitional.

**RippleEdits names its subject by Wikidata QID.** There is no string in the record to look for, so the adapter recovers one from the entry's own test prompts, taking the longest candidate the patterns offer. A strict hit then says a *recovered* string is in the probe — and the recovery can be wrong about which entity it names. The 100% does not transfer because it is a measurement of a different thing.

## What was done

180 items, twenty from each of the three released subsets crossed with the three verdicts, drawn by the same stratified sampler and scored by the same scorer as the MQuAKE set. Blinded the same way: the labelling file carries neither the stratum nor the subset.

One label was added for this draw. **`w` means the string the screen was handed is not this entry's subject at all** — a failure of the recovery rather than of the matcher. It beats the other four letters, and separating the two is the whole reason the card existed.

`w` cannot be adjudicated from the entry's own prompts, because that is where the recovered label came from: a wrong label consistent with them would be invisible. So each drawn entry's `subject_id` was resolved to its English Wikidata label, and the labelling file shows that beside the recovered string. Nothing in the package imports that lookup and nothing calls it at screening time.

**The threshold was written into the card before any item was labelled**: strict precision at or above 95% on all three subsets.

## The result

| subset | strict precision | alias precision |
| --- | ---: | ---: |
| recent | **100.0%** [100.0, 100.0] | 95.0% [84.2, 100.0] |
| random | **100.0%** [100.0, 100.0] | 100.0% [100.0, 100.0] |
| popular | **100.0%** [100.0, 100.0] | 95.0% [84.2, 100.0] |

Per subset and never pooled: the three recover their subjects at rates ten points apart, so one figure would describe no file anyone can download.

**`w` was never used.** Across the 166 distinct entries behind those 180 items, the longest-candidate recovery named the right entity every time — including where the two strings look nothing alike. The adapter recovered `Camp Rucker Theatre` where Wikidata says *Fort Rucker Theatre*, `Anyer Island` for *Anyar*, `Carolina Paz Santana de la Hoz` for *Leslie Santana*. Those are the same entity under another name, not a different one.

What the recovery gets wrong is the **shape** of the string. 28 of the 180 carried a trailing clause lifted from the benchmark's own phrasing — `Daniel G Gavin, which is not media consultant,` — and a malformed string is harder to find in a probe, not easier. It costs recall and cannot cost precision.

## What this licenses

The three rates that were parked as an open thread can now be quoted, on the strict rule, with coverage beside them:

| subset | entries | subject recovered | names the subject outright | including name variants |
| --- | ---: | ---: | ---: | ---: |
| recent | 1,948 | 75.0% | **79.6%** | 89.8% |
| random | 1,922 | 85.0% | **51.9%** | 90.2% |
| popular | 885 | 81.8% | **56.4%** | 85.1% |

Each rate is over the entries whose subject could be recovered, and the coverage column is what says how much of the file that is. Entries whose subject cannot be read are skipped rather than reported clean, because a false clean is the one error that would silently lower the rate being measured.

Set beside [E-048]: MQuAKE-CF-3k names its edited subject in 65.4% of questions and MQuAKE-T in 0.37%. All three RippleEdits subsets sit in the CF range, nowhere near MQuAKE-T. **The hundredfold gap is a property of the two MQuAKE files, not a general spread across propagation benchmarks.**

## What it does not license

**Nothing about whether an edit worked.** The screen measures how an evaluation item was written.

**Nothing about `Compositionality_II` or `Subject_Aliasing`**, the two per-test-type oddities that opened [T-016]. The precision measured here is over the three subsets, not over RippleEdits' declared test types, and a per-type precision would need a draw stratified by type.

**The labeller is a model.** A blind 25-item subset is drawn and waiting for a second labeller; until it is filled in, every figure above rests on one labeller and the agreement rate beside them is unmeasured. That is the largest caveat on this page and it is not a small one.

**The matchers are Western-name-shaped**, and both corpora are English questions over Wikidata entities — the friendliest case they will meet.

## Two failure modes found here, and left unfixed

Both false positives were alias matches on a word belonging to somebody else in the probe: a **title**, where "Princess Alice of Battenberg" matched on *Princess*; and a **house name**, where "Ursula von Baden" matched "the father of Agnes of Baden" on *Baden*.

The misses are more numerous and share one cause: **the neighbour guard suppresses a surname that follows a middle initial.** It reads the word before a match and drops matches belonging to another name, and in `William H. Gates III` that word is `H` — capitalised, not part of "Bill Gates", not at a sentence start. `A. Fauci` and `Steven Jonathan Carlip` go the same way.

Neither is fixed. Both were found by reading this sample's errors, and a fix read off a sample scores far better on it than anywhere else: the alias rule scored 100% on the set its own fixes came from and 90.2% on a held-out draw. A fix is committed before the draw that scores it exists.

## One thing that changed under the published numbers

The bootstrap now resamples **clusters** rather than rows — the case for MQuAKE, the entry for RippleEdits — because three questions off one case are not three independent draws. This widens two intervals published on 2026-11-24 and moves neither point estimate: the held-out alias figure is 90.2% **[75.8, 100.0]**, not [80.5, 97.6], and the pre-fix figure 57.1% **[42.4, 71.4]**, not [45.1, 69.0]. They still do not overlap, so the conclusion they supported stands.

## Reproducing

```
cd editscreen
.venv/bin/python validation/sample.py --adapter ripple
.venv/bin/python validation/score.py --labels validation/labels.ripple.claude.txt \
                                     --sample validation/sample.ripple.json
```

`validation/sample.ripple.json` records the seed, the stratum sizes, the matcher version, the `editscreen` commit, the per-subset coverage and the sha256 of each input file. Scoring reads it rather than the corpus, so it needs neither the benchmarks nor a network.
