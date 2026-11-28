# The Card

One card open at a time. Six fields. Nothing starts until all six are filled, nothing else starts until this one is closed.

A card closes with a number, or with a sentence that could have come out the other way. Never with "explored" or "built". Field 6 is the one that kills cards; fill it honestly.

Promotion to the ten-lens Design Protocol happens only when field 4 names a load-bearing published claim, or field 5's two branches cost more than a week apart.

---

## C-012 · Does the rule that recovers a subject's name decide any rate the paper publishes?

**Status:** closed
**Opened:** 2026-11-24
**Closed:** 2026-11-24 — **branch 2.** It decides a large one. Restricting the canonical pick to the five non-aliasing test types moves the strict rate **up** by 2.4, 18.8 and 9.8 points on `recent` / `random` / `popular`, where the paper had asserted the rule inflates rather than suppresses. The combined "names it or a variant" rate moves by 0.0, +0.3 and −0.2, so every prompt that changed verdict moved between STRICT and ALIAS inside the same flagged set. **The split is rule-dependent and the union is not.** `results/C-012-summary.md`; predictions committed at `6786538` before the runner was written.

**Corroborated 2026-11-28, from a direction this card did not use.** C-012 reached *the split is rule-dependent and the union is not* by scoring the corpus under three recovery rules. `editscreen`'s second alias draw reached the same shape by scoring twelve items against a human instead: **"flag is right" 100%, "level is right" 20.3% [6.2, 36.2]** — the union right every time, the STRICT/ALIAS split wrong four times in five. Two independent methods, the same boundary. The closing finding stands and is now harder to attribute to how the rules were compared. See `editscreen/validation/README.md`, "the LEVEL is what fails", and [T-019] for the two recovery defects it names.

**C-009 was parked for this one sitting and is open again.** Recorded because the one-card rule is the rule most easily broken by a card that looked like cleanup.

**1. WHERE WE ARE.**
[C-011] found that 682 of 1,067 `Subject_Aliasing` strict hits are circular: the adapter takes the longest subject-shaped string across all six test types as the canonical subject, so an alias lifted out of an aliasing prompt can become the subject, and the screen then reports that same prompt as naming it. §5.8 of the paper says this inflates that one test type's strict rate and not the alias rate. That sentence was written without a count.

**2. WHAT WE ARE DOING.**
Score all three released RippleEdits subsets three times — as shipped; with the canonical pick restricted to the five non-aliasing types while every candidate is still passed on as an alias (R1); and with the whole candidate pool restricted (R2) — and report, for each, the entries covered, the strict rate, the strict-or-variant rate, and the strict rate per declared test type.

**3. WHY.**
We do not know whether any number in §5.8 is a property of RippleEdits or of the string the screen happened to pick. The circularity is the only part of the recovery rule anyone has looked at, and it is the part that raises one rate; nobody has asked what the same rule does to the other five.

**4. WHAT IS AFFECTED.** *(written before the work)*
§5.8's per-subset table and its per-test-type table, limitation 14, and [F-17]'s falsifier thresholds. `editscreen`'s `validation/README.md`, which records the circularity and says it is left unfixed. **Nothing measured on MQuAKE is touched** — MQuAKE hands the screen a subject string and has no recovery step.

**5. CONCLUSION IF WE DO IT.** *(three branches, fixed in advance)*
- **If no published rate outside `Subject_Aliasing` moves by more than its stated precision:** the circularity is confined to one test type, §5.8's expectation is confirmed with a number, and limitation 14 stands as written with its scope measured rather than argued.
- **If a subset rate moves materially:** the published table is partly manufactured, and §5.8 reports the restricted-pool number beside the released one.
- **If coverage falls by more than three points:** the restriction is not free, the trade is coverage against circularity, and both numbers are reported rather than one chosen.

**6. CONSEQUENCE OF NOT DOING IT.**
The paper publishes three rates over a corpus that does not give it a subject string, with a prose sentence asserting that the recovery rule does not affect them, and no count behind the sentence. A reader who runs the screen with any other reasonable recovery rule gets different numbers and no way to tell which of us is wrong.

**Controls, and what could make this wrong.**
- **The two restrictions are separated**, because R2 also discards genuine name variants that `Subject_Aliasing` exists to supply, so a fall in R2's alias rate is the restriction working as designed and says nothing about the published numbers. R1 is the counterfactual the published rates are judged against.
- **The adapter's own candidate reader is reused** over doctored copies of each entry, rather than a second copy of its patterns that could drift.
- **R1's precision is not measured, and the card does not claim it.** The 180-item labelled set was drawn stratified by the *released* rule's verdicts, so it cannot be reweighted to score R1. Where the two rules disagree and the entry's Wikidata label can adjudicate, R1 wins 6 to 1 over 33 cases with 24 ties — directional, small, and not a precision figure. [T-019] holds the draw that would make it one.
- **Cost.** No model, no gradients, no network. Three passes over three files already on disk.

---

## C-011 · Does a screen verdict mean the same thing on each of RippleEdits' six test types?

**Status:** closed
**Opened:** 2026-11-24
**Closed:** 2026-11-24 — on branch 1 for five of the six types, and on branch 1 **for the wrong reason** on the sixth. Every prediction written down before the counts holds: the three types whose queries are about the edited subject screen at the top, the type whose queries are about a different entity screens at the bottom, and the mixed type sits between them in all three subsets. So [T-016]'s two unexplained numbers are the benchmark working as its own definitions say, and no new draw was needed to find that out — the definitions had to be read, which nobody had done. Full result in `results/C-011-summary.md`, reproducible by `results/C-011-runner.py`.

**What it turned up that the predictions did not.** `Compositionality_II` is 99.1% clean rather than clean: 20 of its 2,285 prompts carry the edited name, nine outright and eleven inside a different entity's name — a son, a company and a film each named after the person whose fact was edited. And **most of `Subject_Aliasing`'s strict hits are circular**: the adapter recovers the longest candidate across all six types, so when that string is an alias lifted out of an aliasing prompt, the screen reports the same prompt as naming the subject. 78% of them on `random`, 34% on `recent`. That type's count matches its prediction for the wrong reason, and it is the one place in the six where the number is the adapter's property rather than the corpus's.

**What it corrected.** The three headline rates are over **test prompts** of recoverable entries — 16,315 / 11,731 / 10,046 — not over entries. §5.8 of the paper page said entries. No rate moved; the column saying what they were computed over was wrong and is fixed.

**1. WHERE WE ARE.**
[C-010] measured the screen's precision on RippleEdits **stratified by subset** and found the strict rule right 100% on all three, so the subset rates are quotable. Stratified instead by RippleEdits' own six declared test types, the same run produces two numbers nobody has explained. `Compositionality_II` screens at **0.011 / 0.000 / 0.018** across `recent` / `random` / `popular` — essentially never naming the edited subject. `Subject_Aliasing` is **0.163 / 0.265 / 0.114** on the strict rule and rises sharply once name variants count. `editscreen` prints a `by declared test type` breakdown in its own CLI output, so the package is already shipping per-type numbers that no card has checked.

**2. WHAT WE ARE DOING.**
For each of the six test types RippleEdits declares, write down from the benchmark's own definition whether that type's queries should contain the edited subject's surface name — before looking at any count — then count what the screen actually finds, per type and per subset, and name every type where the count and the definition disagree.

**3. WHY.**
We do not know whether the two odd numbers are the benchmark working as designed or the adapter recovering the wrong string. The adapter takes the **longest candidate across all six types**, and two of those types name a different entity by design: `Compositionality_II` asks about an entity that has the edited subject as its object, and `Subject_Aliasing` deliberately uses an alias. So a label that is correct for the entry can still be the wrong string to look for in one type's prompts. After this card, each per-type rate is either a property of the corpus or a property of the adapter, and we can say which.

**4. WHAT IS AFFECTED.** *(written before the work)*
- [T-016], which closes or stays open and says what would close it.
- `editscreen`'s `by_test_type()` output, which is printed today and justified by nothing.
- The paper's §5.8, which reports per-subset rates only, and §5.5 / F-03, which claims `Compositionality_I` items name the edited subject — measured there with the coefficient on one subset, and measurable here by string over all three.
- **[C-010]'s `w` result is narrowed either way.** `w` was adjudicated per entry, against the entry's Wikidata label. A label correct for the entry can still be the wrong string for a particular type's prompts, and this card is where that distinction either bites or does not.
- **Nothing in [E-048] changes.** MQuAKE declares no such types.

**5. CONCLUSION IF WE DO IT.** *(written before the counts are read)*
- **If every type's count matches what its definition predicts:** the two odd numbers are the benchmark working exactly as written, [T-016] closes with no new draw and no new labelling, and the paper gains a per-type table whose explanation is the benchmark's own definitions rather than ours.
- **If a type whose definition predicts the subject IS named comes out low** — `Compositionality_I`, `Relation_Specificity` or `Forgetfulness` — the adapter is recovering a string that is wrong for that type's prompts, the per-type numbers are not quotable, and the per-subset rates in §5.8 need re-reading, because they are the same items pooled.
- **If a type whose definition predicts the subject is NOT named comes out high**, the screen is firing on something other than the edited subject, which is a false-positive mode [C-010]'s per-entry adjudication could not have seen.

**6. CONSEQUENCE OF NOT DOING IT.**
`editscreen` goes on printing a per-test-type breakdown that nobody has checked, next to per-subset rates that have been. A user splitting their evaluation by that breakdown would be acting on the unchecked half of the output, and the package gives them no way to tell which half is which.

**Controls, and what could make this wrong.**
- **The definitions are written down before the counts are read**, and they are taken from the paper rather than from memory. Reading the counts first would turn every number into a prediction that came true.
- **Per type AND per subset, never pooled.** Recovery already differs by ten points across the subsets, so a pooled per-type rate confounds the two.
- **This card adds no labels.** It compares a stated prediction to a count. The 441 items already labelled stay as they are, and no fourth model-labelled draw is made while two blind human subsets sit unfilled.
- **A count is not a precision.** This card cannot say how often the screen is right on a given type; it can only say whether the per-type pattern needs the adapter to explain it. If it does, that is when a draw stratified by type is worth its labelling.
- **Cost.** No model, no gradients, no network beyond fetching the paper's definitions. Minutes.

---

## C-010 · Does the screen hold up on a benchmark that does not hand it the subject?

**Status:** closed
**Opened:** 2026-11-24
**Closed:** 2026-11-24 — yes, on the branch the threshold named. Strict precision is **100% on all three subsets**, against a threshold of 95% written down before any of the 180 items was labelled, so the floor claim survives a corpus that recovers its subject rather than being handed it. The fifth label, `w`, was never used: across 166 distinct entries the recovery named the right entity every time, adjudicated against the Wikidata QID the benchmark itself cites. Full result in `results/C-010-summary.md`; the three subset rates it licenses are in [T-016].

**What it did not settle.** The labeller was a model, and the blind 25-item subset for a second labeller is drawn and unfilled — so the agreement rate that belongs beside every figure above is still unmeasured. Two matcher failure modes were found on this draw, a title surviving as a derived variant and a surname suppressed after a middle initial, and both are recorded unfixed because a fix read off a sample cannot be scored on that sample.

**1. WHERE WE ARE.**
The matchers now have precision, measured on 261 hand-labelled MQuAKE items: the strict rule right **100%** of the time, the derived-alias rule **57.1% [45.1, 69.0]** before it was fixed and **90.2% [80.5, 97.6]** on a held-out draw after. **Every one of those items came from MQuAKE, and MQuAKE hands the screen its subject as a string.** RippleEdits does not — it names the subject by Wikidata QID, so `editscreen`'s adapter recovers the label from the entry's own test prompts, succeeding on 75.0% / 85.0% / 81.8% of `recent` / `random` / `popular`. The screen then reports strict rates of **79.6% / 51.9% / 56.4%** over those entries, and nothing licenses quoting them.

**2. WHAT WE ARE DOING.**
Draw a stratified sample of 180 RippleEdits items — the three subsets crossed with the strict, alias and clean verdicts — blinded as `validation/` already blinds, and label each with the four letters plus a fifth, `w`, meaning *the recovered subject label is not this entry's subject*. Then run `score.py` and report precision per rule, per subset.

**3. WHY.**
We do not know whether a strict match means what it means on MQuAKE. There, a strict hit says the given subject string is in the probe, and the only way to be wrong is a bad word boundary. Here it says a **recovered** string is in the probe, and the recovery can be wrong — it takes the longest candidate from patterns that were never built to be exact. So the 100% does not transfer, and the `w` label is what separates a matcher error from a recovery error. After this card there is a precision figure for a corpus whose subjects are organisations, works and non-English names, and a count of how often the adapter picked the wrong subject.

**4. WHAT IS AFFECTED.** *(written before the work)*
- T-016's three strict rates, which become quotable or do not.
- `editscreen`'s README, which tells a user to quote the strict rate and justifies that on MQuAKE alone.
- `validation/README.md`'s standing admission that "both benchmarks are MQuAKE ... precision measured here is an optimistic estimate for anything else." This replaces it with a number either way.
- Whether RippleEdits can be the paper page's third benchmark, or only its second.
- **Nothing in E-048 changes.** It is MQuAKE, its subjects are given rather than recovered, and no rate in it depends on this.

**5. CONCLUSION IF WE DO IT.** *(threshold set before running)*
- **If strict precision is at or above 95% on all three subsets:** the floor claim survives a corpus that did not hand it the subject, the recovery is good enough to build on, and the RippleEdits rates can be quoted on the strict rule with coverage beside them.
- **If strict precision falls below 95% on any subset AND most failures carry `w`:** the rule is fine and the recovery is not. The floor claim becomes conditional on the benchmark supplying a subject string, the README has to say so, and the adapter needs the leftmost-`" of "` limitation revisited — which is already documented and deliberately unfixed.
- **If strict precision falls below 95% AND the failures do not carry `w`:** the strict rule itself is weaker than MQuAKE suggested, most likely on organisation names where a short form matches inside a longer one. That is the branch that would change the headline of the whole package, and it is the reason the threshold was written down first.

**6. CONSEQUENCE OF NOT DOING IT.**
The adapter ships and produces three numbers nobody may quote, which makes it dead weight rather than an instrument. Worse, `editscreen` goes on telling users that the strict rate is the one to trust on the evidence of **one benchmark** — which is the exact criticism this project makes of everybody else's propagation results.

**Controls, and what could make this wrong.**
- **Blinded as the existing set is.** `labels.txt` carries neither the stratum nor the subset, because the screen's verdict invites agreement and the subset carries a base rate to lean on.
- **Per subset, never pooled.** Recovery already differs by ten points across the three; a pooled precision would describe no file anyone can download.
- **The labeller is a model** unless the human subset is filled in, so the agreement rate is reported beside every figure, as it is for the MQuAKE set.
- **Nothing is tuned against this sample.** 0.2.0a2 scored 100% on the set its own fixes came from; the held-out draw put it at 90.2%. If a fix comes out of this card, it is committed before a second draw is made.
- **The MQuAKE precision is not a prior to lean on.** Field 3 is the whole reason: a different thing is being measured, not the same thing again.
- **Cost.** No model, no gradients, no network. A sampler and a scorer that already exist, and roughly an hour of labelling.

---

## C-009 · Is the site where these edits go in a site where the attribute actually lives?

**Status:** open
**Opened:** 2026-11-15
**Parked:** 2026-11-22 — written in full, never run. The effort was wound up while the card was still open, so it is parked rather than closed: nothing about it has been decided and nothing needs re-deciding to resume. The three branches and the 5-point threshold below were fixed before any RAVEL number on this setup was looked at, and they still are.

**Blocked: 2026-11-24 — the cost line is wrong, and field 2 names code that has moved.** Checked before resuming, not discovered part-way in.

- **The track's code is no longer in MIB's own repository.** `aaronmueller/MIB` now points the causal variable localization track at [`atticusg/CausalAbstraction`](https://github.com/atticusg/CausalAbstraction), which has been reworked into a protocol-JSON CLI (`causalab run <protocol>.json`). Field 2's *"run MIB's RAVEL causal-variable evaluation"* names an entry point that no longer exists in the place the card points at.
- **There is no supported remote path.** The cost line says *"through NDIF"*. That repository's compute table reads **"Remote runs on large models; the guide is a placeholder"**, linking a `docs/ndif.md` that is exactly that. So the way this card assumed Llama-3.1-8B would be reached is not available.
- **The README names only DBM and DAS**, both trained by gradient descent. It does not name the **Full Vector** no-featurizer baseline that field 2 asks for. The paper reports it in Table 3g, so it presumably exists in the code; it is not documented, and that has to be read out of the source before the card can state what it is running.
- **What is NOT the blocker, and this is the useful half.** The `out.grad is None` failure that stopped [E-043] and [E-047] does not reach this card. An interchange intervention is forward-only — the repository's own quick start describes its patching work as *"two forward passes per example"* — and the gradient requirement attaches to DBM and DAS, which this card does not use. **The blocking question is where the model runs, not whether a backward pass works.**

**Three ways out, and the choice is not a detail.** Run the 8B locally, which this project has never done and which the machine may not hold. Reimplement the Full Vector interchange intervention with nnsight on NDIF, which is how every reading in this paper was taken and needs no gradients — but which turns field 3's *"externally scored ... from a benchmark nobody here built"* into our own implementation over their data and splits, and that is a real cost to the claim. Or drop to a smaller MIB model, which loses comparability with the layer-5 Llama-3.1-8B edit site that is the whole point of the card. **Until one is chosen, field 2 cannot be executed as written.**

**Unblocked: 2026-11-24 — the second way out was chosen: reimplement the Full Vector interchange intervention with nnsight on NDIF.** Chosen over running the 8B locally and over dropping to a smaller model. The reason given was that it is a thing worth learning how to do, and that is a legitimate reason to pick between three options that all answer the same question; it is recorded here so nobody later reads the choice as having been forced by the evidence.

**What it costs, stated here rather than discovered in review.** Field 3 said the card would end with *"an externally scored number ... from a benchmark nobody here built"*. After this choice the **data, the splits and the task definition** are still theirs and the **implementation is ours**, so the number is no longer externally scored. Fields 2 and 3 are amended below to say that, and a new control is added to buy back what can be bought back: before any layer-5 reading is taken, the same implementation is run on whatever MIB's paper reports for Full Vector on this model, and the two are compared. If our implementation reproduces their published Full Vector number, the layer-5 reading inherits that credibility; if it does not, the card closes on that discrepancy and reports it, because an implementation that cannot reproduce a published baseline cannot be trusted to rank layers. **That reproduction check is a stopping condition, not a sanity check.** See [T-018].

**Both of those were read on 2026-11-24, and the reading overturned two thirds of the blocker above. RCA, because the blocker was written here as fact.**

- **"The track's code is no longer in MIB's own repository" is WRONG.** It is exactly where the card always pointed: `aaronmueller/MIB/MIB-causal-variable-track/`, with the task at `tasks/RAVEL/ravel.py` and the runner at `baselines/ravel_baselines.py`. What misled me is that `CausalAbstraction` is a **submodule** of that directory, and I read the submodule's current upstream state instead of the commit MIB pins. MIB pins `f9ed6777`, dated 9 July 2025: the pre-rework layout, `experiments/` and `neural/`, built on **pyvene**. The protocol-JSON CLI I found is upstream work that happened after the pin and has no bearing on running this track.
- **"The README names only DBM and DAS, not Full Vector" is WRONG.** `ravel_baselines.py` takes `--methods`, defaulting to `["full_vector", "DAS", "DBM+SVD", "DBM+PCA", "DBM", "DBM+SAE"]`. `full_vector` is a first-class method name, not something to be reconstructed from the paper.
- **The remaining third is right, and it is the whole blocker.** The stack is pyvene against a locally loaded HuggingFace model. There is no NDIF path in it. **Where the 8B runs is the only open question**, exactly as recorded — but it is now the only one.

**What the code does, answering field 2's first control.** `full_vector` builds `PatchResidualStream(pipeline, task, list(range(start, end)), token_positions, checker, ...)` and calls `save_featurizers(None, ...)` — **no featurizer and, unlike the DAS and DBM branches, no `train_interventions` call at all.** So it swaps the whole residual-stream vector and is forward-only, which is what the card assumed and had not checked. Layers are `range(start, end)`, end exclusive, `start=0` and `end=pipeline.get_num_layers()`. **Read 2026-11-24, and it lands on the right point.** `residual_stream_experiment.py` constructs `ResidualStream(layer=layer, ..., target_output=True)`, and in `neural/LM_units.py` that flag resolves as `component_type = "block_output" if target_output else "block_input"`. So MIB's layer L is the residual stream at the **output of block L**.

**That is the same place this project's edit lands, which was the thing most likely to go wrong.** `editreach`'s `arch.py` maps layer L to `model.layers[L].mlp.down_proj`, so a ROME edit at layer 5 writes the MLP whose output is added into the residual stream inside block 5 — and therefore appears in the residual stream at the output of block 5. Both repositories index `model.layers` from zero. **MIB's layer-5 reading is taken at exactly the point the edit arrives**, not one block early or late.

**One link in that chain is argued rather than read, so it gets a control.** How pyvene itself resolves `"block_output"` to a hook lives in the pyvene package, not in either repository here, so the match above rests on pyvene's documented convention plus both repositories indexing from zero. Before any layer-5 number is quoted, capture the vector MIB hooks at some layer L and compare it against the residual stream after block L from a plain forward pass of the same model on the same input. They are equal or this card is answering a different question. That check costs two forward passes and no interventions.

**The token position matches, and that was not guaranteed.** `get_token_positions` returns exactly two: `entity_last_token`, the last token of the city entity, and `last_token`. The card says only the city-entity position is compared, and that position exists under that name. Data is the HuggingFace dataset `mib-bench/ravel`; the attributes are `Continent`, `Country`, `Language`.

**Table 3g, read off the paper rather than assumed, giving the reproduction target [T-018] needs.** Full Vector on Llama-3.1-8B: **53 (62) / 47 (53) / 47 (57)** for Continent / Country / Language, as mean across counterfactual datasets and layers with the best layer in parentheses. DAS on the same row reads 75 (83) / 58 (64) / 63 (70), which matches the figures already in field 1 and so confirms the right row was read.

**What that number does to field 5, worked through before any code. The first reading of it was wrong.**

*Written first, and withdrawn:* that a 5-point threshold against a 6-to-10-point spread made branch 3 — *the baseline cannot tell layers apart* — likely. **The published table already rules branch 3 out, and the argument is one line.** Branch 3 fires only if the baseline's range across layers is within 5 points. The table gives the mean across layers and the best layer: 53 and 62, 47 and 53, 47 and 47 → 57. The minimum across layers cannot exceed the mean, so the range is at least best-minus-mean, which is **9, 6 and 10 points** — above 5 on every attribute. Branch 3 is dead before the card runs, which is a gain, not a loss: one of three branches is eliminated by evidence that was already published.

**The real worry is resolution, and it survives.** Branches 1 and 2 split on whether layer 5 sits within 5 points of the best layer, and the whole layer-to-layer range is 6 to 10 points. So the test has about one bit of resolution, and Table 3g reports **no uncertainty at all** — a 5-point gap between two point estimates may be inside run-to-run noise, and nothing published says whether it is.

**Resolution is fixed with a control, not by re-scoping.** The thresholds were fixed in advance and they stay fixed. What is added: layer 5's accuracy and the best layer's are each reported with a bootstrap interval over the counterfactual datasets, and the branch is read off the intervals as well as the point estimates. **If the two intervals overlap, that is reported as the comparison failing to resolve** — branch 3's substance arriving by a different route than branch 3's letter, and an honest answer rather than a manufactured one. The card closes either way.

**A fourth way out, which the three recorded above missed.** Because the code is where it always was and `full_vector` is already implemented, MIB's own runner can be run **unchanged** on any machine that holds Llama-3.1-8B — a rented GPU hour, not a reimplementation. That keeps field 3's *"externally scored ... from a benchmark nobody here built"* **intact**, which the chosen nnsight path spends. The nnsight path remains the choice on record and remains defensible as a thing worth learning; this option is written down because it was not available to the decision when the decision was made.

**Reaffirmed 2026-11-24, with the fourth option on the table: nnsight on NDIF.** The choice was put again once running MIB's own runner unchanged on a rented GPU was known to be possible, and it was made the same way. So the cost in field 3 is now paid knowingly and twice over, which is the strongest form this record can take: the cheaper path that would have preserved the externally-scored claim was named, offered, and declined.

**Started 2026-11-24. Two constraints found before any model was touched, and one of them is self-inflicted.**

- **`datasets` cannot be used in this project, and trying cost an hour.** `pip install datasets` upgraded `huggingface_hub` from the pinned 1.30.0 to 2.4.0, which conflicts with the pinned `transformers` 5.17.0 and `tokenizers` 0.23.2 — so the venv every number in this repo was read through was briefly broken. It is restored: `pip check` clean, `pip freeze` an exact match to `requirements.txt`, every module importing. `datasets` would not have worked anyway — it raises `InvalidVersion: '3.14.0+'` on this Python. **Nothing was re-run and nothing needs re-reading**, because no measurement was taken while it was broken.
- **The route that does work needs one new dependency, and it is justified here rather than silently added.** `huggingface_hub` downloads the release's parquet files directly and `pyarrow` reads them, with no `datasets` and no second copy of the hub. `pyarrow==26.0.1` is pinned in `requirements.txt`; it touches nothing else and `pip check` stays clean.

**One nnsight constraint found while running that control, and it shapes the runner rather than the control.** Under `remote=True` the body of a trace **runs on the server**. A `print` inside it returns as a remote LOG line and a dict built inside it is built there and discarded — the client gets an empty dict and a `KeyError`, with no error from nnsight, because nothing went wrong. **Saved proxies have to be bound to plain local names.** So the interchange runner cannot accumulate per-layer results in a container inside one trace; it takes one trace per layer, or it restructures. The queue measured ~0.4s on this model, so extra round trips are cheap and the cleverness is not worth buying back.

**The data is in hand, and its shape settles what Table 3g's "mean across counterfactual datasets" means.** `mib-bench/ravel` ships train / val / test parquet; val is **15,950 rows**. Each row carries `prompt`, `entity` (the city), `attribute` (the one queried), gold `Continent` / `Country` / `Language`, and **three** counterfactuals under their own keys — `prompt_template_counterfactual`, `attribute_counterfactual` and `wikipedia_counterfactual` — each a full record with its own prompt, entity and attribute values. So the paper's average is over those three, which is also what the interval control above must resample.

**The model-free half of the runner is built and selftested: `agents/engineer/workspace/ravel_iia.py`.** Data straight from the released parquet, pair construction, the expected answer, and MIB's checker ported with its oddities intact — including that a trailing comma in an expected value yields an empty option that matches any output. Fixing that here would make our number incomparable with theirs, so such rows are flagged and counted; there are none in `val`. Twelve rows of 15,950 carry a null attribute and are dropped and counted rather than guessed.

**One structural fact that came out of building it, and it explains MIB's table.** The expected answer is the **causal model's**, not the source's: if the question is about the moved variable expect the source's value, and if it is not, expect the base's **unchanged**. So most of this metric is selectivity — **58% to 79% of pairs are held rather than moved**, depending on the target. Full Vector swaps the whole vector and therefore drags every attribute across at once, which is precisely why it is the weak baseline in Table 3g rather than the strong one. The card's branches read a layer profile of a method that is bad on purpose, and that was not obvious from the card when it was written.

**The intervention runs, and it was validated on six examples at layer 5 before anything was scaled.** Reading the residual stream after block L at the source city's last token and writing it at the base city's moves the attribute: *Gaya* ← *Dieppe* goes `Asia` → `Europe`. It also moves the attributes it should not, which is the point of this baseline: *Nagua* ← *Focsani* goes `Dominican Republic` → `Romania`, and *Dandong* ← *Senanga* goes `Mandarin` → `Bemba`, a Zambian language for a Zambian city. Both halves of the metric behave as the causal model predicts.

**The entity index is audited rather than assumed.** 3,600 pairs: zero missing, zero ambiguous, zero misaligned, with the selected token decoded and matched against the entity's ending. MIB takes the **first** regex match, not the last, which is only safe because RAVEL's exemplar city always differs from the queried one — so that is checked rather than trusted.

**Generation had to become multi-token, and that was a correctness bug rather than a refinement.** MIB's checker is a substring test over generated text and the answers are often several tokens. At one token the unintervened model answered `'Domin'` — right, and scored wrong. Every multi-token answer would have scored wrong whatever the model did, depressing our number against MIB's for a reason unrelated to the intervention.

**And here is the number that now governs this card: a remote trace costs 2.39s median**, measured over six, min 2.29s — not the 0.4s the server reports for its own execution, the rest being queue and transport. One example at six generated tokens over two conditions is about **30 seconds**. MIB evaluates **10,000 examples per attribute**, over 32 layers and three counterfactual types. One attribute at one layer for one counterfactual type is already ~83 hours. **A faithful reproduction at this granularity is not affordable and will not become affordable by tidying the loop.** Batching many prompts into one trace is necessary — MIB's own Llama eval batch is 256 — and even then the reproduction will be over a subsample with its own interval rather than over their 10,000. That has to be said in the write-up rather than discovered by a reader comparing denominators.

**What is left to build, in the order it has to be built.** Batched traces, without which nothing else matters; **MIB's filtering**, which keeps every example of the target attribute and half of each other and so sets the denominator; and the bootstrap over the three counterfactual types for the interval control.

**MIB's filtering is built, 2026-11-26, and that was the item the write-up called the blocker.** `results/T-020-summary.md` said of it *"That is the next thing to build and the reproduction cannot be attempted before it exists"*. It exists: `agents/engineer/workspace/ravel_filter.py`, selftested, with `ravel_iia.py` amended to carry a row index.

**Both of MIB's filters are ported with their oddities intact, because fixing them here would make our number incomparable with theirs.** In order: **correctness**, `FilterExperiment.filter` at MIB's pinned commit `f9ed6777`, and **attribute balance**, `get_filtered_indices` in `ravel_baselines.py`. Three things a reimplementation would quietly improve, and all three are kept:

- **Correctness is a conjunction over BOTH arms, not a threshold on one.** The model must answer the base prompt and the counterfactual prompt correctly, unintervened. Two of this project's own notes — `CARD.md:200` as it then stood, and `T-020-summary.md:47` — described it as one condition on one prompt. Both were wrong, and were caught only by re-fetching MIB's source rather than porting from the note.
- **`half` is misnamed in MIB's own code.** `half = len(attr_to_indices[target_variable])` is the FULL count of the target attribute; it is the *other* attributes that get cut to `half // 2`. Ported under MIB's name so the two can be diffed.
- **The wikipedia counterfactual's source arm passes unconditionally.** Its causal-model answer is `""`, `check` splits the expected value on commas and tests substring membership, and `"" in anything` is True. Not a bug we introduced and not one we may fix.

**Keep rates, 300 pairs per cell, 6 generated tokens, batch 48, seed 0.**

| counterfactual | base | source | joint | rate | balanced (Cont / Ctry / Lang) |
| --- | ---: | ---: | ---: | ---: | --- |
| `prompt_template` | 238 | 245 | 189 | 0.630 | 96 / 145 / 133 |
| `attribute` | 238 | 252 | 202 | 0.673 | 85 / 169 / 148 |
| `wikipedia` | 238 | 300 | 238 | 0.793 | 104 / 188 / 184 |

**The four predictions were committed at `804c30b` before any count was read, and one of them failed.** `results/C-009-filter-predictions.md`.

1. **Held.** Clean base accuracy came out **0.793**, above [T-020]'s 0.69. That 0.69 was never the model's own accuracy — `score_batch`'s "unintervened" arm goes through the patched path, where both arms carry an identical write by design. `generate_clean` writes nothing.
2. **Held exactly, to the pair.** `source_ok` = 300 = `built` for the wikipedia family, as the empty-option hole requires. This was the one that would have condemned the port.
3. **FAILED, and the reasoning failed with it.** Predicted 0.50–0.60, on the argument that the two arms are correlated and so the conjunction beats the independent product. Actual **0.630** and **0.673**, against independent products of 0.648 and 0.666 — within 1.8 points either side. **The arms are essentially independent, and the correlation argument was wrong**, not merely mis-sized.
4. **Held, strongly.** The three attributes do not survive at the same rate, so the balanced sets differ: 96 / 145 / 133 on one family, 85 / 169 / 148 on another. **MIB's three published numbers are not over equally sized sets**, and [T-018] has to say so rather than let a reader assume one denominator.

**The source arm first scored 0.31, and the cause was ours.** `build()` keyed rows by prompt text. Base prompts are **not unique** — 10,276 distinct prompts over 15,950 val rows, so two rows in three share one — and the lookup silently returned a different row's counterfactual. A probe asking the continent of Pinsk scored the model's correct `Europe` against gold `'Arabic,Hebrew,Russian'`. Fixed by carrying `"row": i` through `pairs()`. A regression guard with two synthetic rows sharing a prompt was added **and verified to fail against the old lookup**, which is the only way to know a guard guards anything.

**One claim made here was wrong and is withdrawn.** I recorded an apparent off-by-one — *"the final sizes imply 48/73/67 = 188, one short of the 189 reported"* — and called it a silent-drop path needing a guard. It is a reading error. The three targets do not share a survivor pool: `pairs()` drops rows whose gold for the **target** is null, which costs Continent 7 rows and the other two none, giving per-target survivor counts of {62,118,120} against {63,117,120}. Brute force confirms (48,73,67) is the unique decomposition and only at 188. The guard was kept because it is independently correct; its comment no longer cites 189-vs-188 as evidence of anything.

**What is left, unchanged from the list above except that filtering is struck:** batched traces for the intervention runner, and the bootstrap over the three counterfactual types for the interval control. **[T-018] is no longer blocked on the filter.** It remains gated on the open Full Vector / DAS judgement call, which is a question about what the card should measure and not about what can be run.

**The gradient blocker moved, and still does not reach this card.** As of 2026-11-28 NDIF refuses backward passes for untrusted requests — a sandbox with no computation graph, not `OutOfOrderError` — see [E-047]'s note of that date. This card is forward-only, so it is unaffected either way; recorded here so the next reader does not re-check it. The client is now pinned to nnsight **0.8.4**, matching the server, verified not to move any local number.

**1. WHERE WE ARE.**
This project closed negative: the coefficient detects contamination, not propagation (C-001, C-002). Every edit here and in edit-slice is delivered at Llama-3.1-8B **layer 5**, on the subject's **last token** — a choice inherited from ROME and never tested in either project. MIB's RAVEL task (Mueller et al., ICML 2025, arXiv 2504.13151, Table 3g) measures where that same model holds a city's **country, continent and language**, at the last token of the city, at every layer. Its best method, DAS, scores **75 / 58 / 63** IIA averaged over layers and **83 / 64 / 70** at its best layer.

**2. WHAT WE ARE DOING.**
Run MIB's RAVEL causal-variable evaluation on Llama-3.1-8B with its no-featurizer baseline ("Full Vector": swap the whole hidden vector) at the city's last token, at every layer, and report interchange intervention accuracy for each of the three attributes at layer 5 against that attribute's best layer.

*Amended 2026-11-24:* **the evaluation is our own implementation of their baseline, not their runner.** Their released RAVEL data and splits, their task definition and their metric; the interchange intervention written with nnsight against the NDIF-served model, because their code has moved to `atticusg/CausalAbstraction` and that repository documents no supported remote path. The amendment changes who wrote the code, not what is measured — and it adds the reproduction control above, which is what keeps that distinction checkable.

**3. WHY.**
We do not know whether the place edits are delivered is a place where the fact is causally carried. ROME's default is not evidence for it: Hase, Bansal, Kim & Ghandeharioun (NeurIPS 2023, arXiv 2301.04213) found that causal-tracing localization *"do[es] not provide any insight into which model MLP layer would be best to edit."* After this card there is a number for the edit site, on the same model, on a benchmark's own data, splits and metric. *Amended 2026-11-24:* this sentence previously said **externally scored**, and after the implementation choice above that word is no longer true — the task and the data are theirs, the code is ours. What replaces it is the reproduction check: a number that matches their published Full Vector baseline is worth nearly as much and is worth it for a stated reason, where an unchecked reimplementation is worth little.

**4. WHAT IS AFFECTED.** *(written before the work)*
- The paper's explanation of its own negative result — *contamination, not propagation* — which today never asks whether the edit went in at the right place.
- T-086 in edit-slice (what sets an edit's magnitude), which gains or loses a candidate.
- The layer-5 choice in both projects.
- Whether T-013, an entry to the MIB leaderboard, is worth opening.
- **Nothing measured so far changes.** This reads a public benchmark through the unedited model.

**5. CONCLUSION IF WE DO IT.** *(three branches, threshold set before running)*
- **If layer 5 is within 5 IIA points of the best layer on all three attributes:** the edit site carries the attribute, and the negative result cannot be blamed on editing the wrong place. The paper says so, with the numbers.
- **If layer 5 is more than 5 points below on any attribute, with the best layer later:** edits go in upstream of where the attribute becomes swappable. That is a candidate mechanism for *delivered, not effective*, and the paper gains a sentence backed by an outside benchmark.
- **If the baseline scores within 5 points across all layers:** it cannot tell layers apart, nothing about layer 5 is learned, and the question moves to a trained featurizer — T-013.

**6. CONSEQUENCE OF NOT DOING IT.**
The paper explains a negative result without once checking its edit site against an outside localization benchmark on the same model. The first question a reviewer asks is *were you editing the right place?*, and today the only answer is *ROME's default*.

**Controls, and what could make this wrong.**
- **Same object, or a neighbour.** ROME writes into the MLP at layer 5; its output lands in the residual stream after layer 5. MIB's Full Vector swaps a hidden vector at a layer. Before any number is read, confirm which hidden vector MIB's code swaps and that its layer index uses the same convention as `arch.py`; a one-off in the index is the cheapest way for this card to answer a different question.
- **Same position.** The edit site is the subject's last token; MIB's RAVEL intervenes at the last token of the city entity, and also at the final token. Only the city-entity position is compared.
- **MIB's own data and splits,** not a regenerated set, so the numbers are comparable to Table 3g.
- **The serving device is recorded** with each run (C-006). IIA is an argmax over tokens, so the 2.2e-04 cross-device tolerance should not move it, and recording the device is how that is checked rather than assumed.
- **The 5-point threshold was set here, before running,** and before any RAVEL number on this setup was looked at.
- **Reproduction before reading.** Our implementation must first reproduce MIB's published Full Vector number on this model before any layer-5 comparison is read. A discrepancy closes the card on the discrepancy. [T-018].
- **Hook equality — RUN AND PASSED, 2026-11-24.** `agents/engineer/workspace/ravel_hook_check.py`. Block L's output is the residual stream after block L, checked two ways so neither rests on a tolerance anyone chose. *Chain*, `out[L] == in[L+1]`: **bit-identical**, on gpt2 at five layers and on **Llama-3.1-8B over NDIF at layers 0, 5, 15 and 30**. *Identity*, against a plain forward pass: a **neighbour test** rather than a tolerance, because nnsight serves on mps while HuggingFace loads on cpu and the same tensor still differs by ~1e-3 — [C-006]'s device effect, and any tolerance absorbing it would be a number picked to make the check pass. Of `hidden_states[L]`, `[L+1]` and `[L+2]`, block L's output is closest to `[L+1]` by margins of **10,000× to 5,600,000×**. The one argued link in the chain from `arch.py`'s edit site to MIB's `block_output` is now measured.
- **An interval, not two point estimates.** Layer 5's accuracy and the best layer's are each reported with a bootstrap interval over the counterfactual datasets. The 5-point threshold is read against the intervals as well as the points, and overlapping intervals are reported as the comparison failing to resolve. Table 3g publishes no uncertainty, so this is the project's own and cannot be compared to theirs.
- **Branch 3 is eliminated in advance** by the published table: best-minus-mean is 9, 6 and 10 points across the three attributes, so the layer range exceeds 5 on all of them.
- **Cost.** *Amended 2026-11-24:* previously *"using MIB's released code and data"*. Forward passes with interchange interventions on Llama-3.1-8B through NDIF, using MIB's released **data** and our own nnsight implementation of their Full Vector baseline. No edits, no gradients — the interchange intervention is forward-only, which is why the `out.grad is None` failure that stopped [E-043] and [E-047] does not reach this card.

---

## C-008 · Does a subject's prominence predict how hard an edit hits, where geometry does not?

**Status:** closed
**Opened:** 2026-11-09
**Closed:** 2026-11-09 — **branch 3.** Neither predicts. Prominence **+0.005** (95% CI −0.315, +0.314), dependent count **−0.053** (−0.366, +0.270), over 41 subjects; all six partials and both covariate controls also span zero. The limit belongs with the number: at n=41 this excludes roughly **|ρ| > 0.37** and nothing smaller, so it is *no evidence of an effect*, not evidence of no effect. See `agents/shared/decisions.md` [E-016].

**1. WHERE WE ARE.**
Seven geometric candidates have been eliminated against a pre-registered floor, their best pairing bounded at 0.534, and the published page says *"it still has no candidate — but the absence is now evidence of having looked."* **Every one of those candidates was a property of the activation geometry.** None was a property of the subject. [R-003] established today that the nearest prior work never ran either arm of this question: KnowledgeSmith varies a node's depth in a hierarchy, never its number of dependents, and uses no frequency variable at all.

**2. WHAT WE ARE DOING.**
For the 42 edited subjects in [E-001], regress per-subject damage — the median `excess` over that subject's probes, which is real-minus-control movement — on two subject properties: **prominence**, as the number of Wikipedia language editions linking the subject's Wikidata item, and **dependent count**, as the number of Wikidata statements on that item. Report each coefficient with a bootstrap interval, their correlation with each other, and each one's partial effect with the other removed.

**3. WHY.**
We do not know whether the magnitude of damage is set by anything about the *fact* rather than by the geometry of its key. The project's working heuristic — edit facts with few dependents — has never been tested, and the two readings of it point opposite ways: "Maurice de Vlaminck" appears in very few prompts while "speed of light" appears in enormous numbers of them, so prominence and dependent count would rank the same facts in nearly the same order for opposite reasons. After this we know which, if either, carries the ranking.

**4. WHAT IS AFFECTED.** *(written before the work)*
- The published sentence *"the absence is now evidence of having looked"* on the edit-slice review page. It is true of geometry and this is the first thing that tests a different class of variable. If a subject property predicts, that sentence needs amending; if neither does, it gets stronger and should say which classes were searched.
- T-002 closes, and T-086 in edit-slice — *what actually sets the magnitude* — gains its first non-geometric evidence either way.
- The heuristic itself. It is currently advice with no measurement behind it.
- **Nothing measured so far changes.** This is a new regression over numbers already on disk plus one Wikidata field.

**5. CONCLUSION IF WE DO IT.** *(all three branches, in advance)*
- **If prominence predicts and dependent count does not,** once each is partialled for the other: the heuristic is right about which facts to pick and wrong about why, and the rule is restated as *prominence*, not *entanglement*.
- **If dependent count predicts and prominence does not:** structural entanglement sets magnitude here, the heuristic is right for its stated reason, and this is the first result in the project that agrees with the branch-structure line in the literature rather than departing from it.
- **If neither predicts at n = 41,** with intervals spanning zero: we say that, with the interval, and the published absence-sentence is strengthened and made specific — two classes of variable searched, geometry and subject identity, neither carrying the magnitude.

**6. CONSEQUENCE OF NOT DOING IT.**
A published page claims a search was done and found nothing. The search was entirely geometric, and the page does not say so. Leaving this unrun means the claim keeps its generality without having earned it — and the cheapest possible test of a different variable class is sitting in a cached file.

**On promotion, and why it is declined.** Field 4 names a load-bearing published claim, which is the Card's stated trigger for the ten-lens protocol. It is declined because field 5's three branches cost the same — one sitting, over data already on disk — and the protocol exists to decide *which tickets should exist at all* when that decision is expensive. Here it is not. Recorded so the decision is visible rather than skipped.

---

## C-007 · Is the upper bound on an edit's reach informative, or merely true?

**Status:** closed
**Opened:** 2026-11-09
**Closed:** 2026-11-09 — **branch 2.** Median looseness **1.05** in the near field and **21.12** (95% CI 20.16–22.14) in the far field, over 1,539 question-positions. The number that carries it is the far field's **median bound of 1.1456** against a median coefficient of 0.0544: the bound permits a question that never names the edited subject to receive more than the near field actually receives, so it forbids nothing that happens. The near field's 1.05 is not a second finding — there `k ≈ k*`, so Cauchy–Schwarz is near-equality by the same prefix-sharing that pins the anchor at 1.000. See `agents/shared/decisions.md` [E-015].

**1. WHERE WE ARE.**
The dry-run on T-001 produced a universal upper bound in one line: because ROME's update has a **fixed** direction and only the scalar `c(k) = (k*·k)/(k*·k*)` varies with the token, Cauchy–Schwarz gives `|c(k)| ≤ ‖k‖/‖k*‖` for every prompt, with no enumeration and no forward pass through the edited model. (`C = I` here — confirmed from `coefficients()` in `run_e004.py` and by reproducing two recorded values exactly from the cache.) The bound is certainly true. Nothing says it is tight enough to forbid anything.

**2. WHAT WE ARE DOING.**
For every key already cached in `results/cache/E004_keys.pt` — 513 instances, 1,539 question-positions, Llama-3.1-8B layer 5 — compute the **looseness ratio** `(‖k‖/‖k*‖) / |c(k)|` and report its median and interquartile range separately for the near field (questions naming the edited subject, read at `k_natural`, the subject's last token) and the far field (questions that do not, read at `k_final`). Offline, no NDIF, no edits, no gradients: one pass over a 206 MB file.

**3. WHY.**
We do not know whether the bound is usable. If it is tight, the project can make a statement it currently cannot make at all — *nothing outside this set receives more than X* — which is a different kind of claim from everything else here, all of which is a lower bound or a denial. If it is loose, we learn that the only universal statement available is vacuous, and we learn it before writing it down as though it were a result.

**4. WHAT IS AFFECTED.** *(written before the work)*
- The paper's sentence *"we can say which facts an edit touches, not how hard."* The dry-run already showed this is imprecise — how hard **is** boundable in activation space — and this card decides which correction it gets.
- The scope claim *contamination detector, not propagation detector*, in the abstract and on the overview page. A loose far-field bound reaches the same conclusion by a second, independent route and strengthens it; a tight one does not overturn it but sits beside it awkwardly and needs its own sentence.
- T-001, T-010. T-011 and T-012 are **not** affected either way — they are about crossing into behaviour and about prior art, and neither turns on this number.
- Nothing measured so far changes. This is a new quantity over cached keys, not a re-reading of an old one.

**5. CONCLUSION IF WE DO IT.** *(both branches, in advance)*
- **If the median looseness ratio is ≤ 10 in both regimes:** the screen carries a usable upper bound, and we claim it — a positive result this project does not currently have, and the first thing here that bounds damage from above rather than finding it from below.
- **If it exceeds 10 in the far field:** the bound is real and vacuous exactly where propagation lives. We claim that the only universal statement available is uninformative there, and the paper's sentence becomes *boundable in activation space, informatively only in the near field* — the contamination-detector finding arriving a second time by a different route.

**The threshold was chosen after an eight-item feasibility peek, and that is recorded rather than hidden.** Checking the cache was runnable at all meant computing eight values, which showed far-field ratios of roughly 12–40 at the final-token position. So branch 2 is the likelier one and the card is opened knowing it. The peek is 8 of 1,539 at one position and settles nothing; what it costs is the right to call this pre-registered, and it is not called that.

**6. CONSEQUENCE OF NOT DOING IT.**
A sentence already on a published page stays wrong in a way we have now seen. *"We can say which facts an edit touches, not how hard"* reads as though no bound on magnitude exists; one does, and it is a line of algebra. Skipping this leaves the page asserting an absence that the project can disprove in an afternoon — which is the worst of the three states, worse than either branch above.

---

## C-006 · Do the two values partition by the GPU that served the request?

**Status:** closed
**Opened:** 2026-11-01
**Closed:** 2026-11-01 — **branch 1**, and the device turns out to be 1.4% of the drift

**1. WHERE WE ARE.**
[E-005] found that readings of the same batch, on byte-identical inputs, differ between NDIF connections on **93.94% of elements** — up to 6.250e-01 at `lm_head` and 3.125e-02 at the layer-5 key site, against a median |key| of 1.135e-02. Deterministic within a connection. Across six readings only **two** distinct values appeared, grouped in contiguous runs of connections. nnsight exposes server-side `meta` on `tracer.backend`, and it carries `max_mem_by_gpu` — a **GPU index**.

**2. WHAT WE ARE DOING.**
Read the same 84-prompt batch through 16 fresh connections, recording for each: a content hash of the returned keys, the GPU index from `meta`, and the runtime. Then test whether the distinct hashes partition by GPU index.

**3. WHY.**
We do not know whether this is routing (two replicas on different devices, each internally consistent) or something that varies within one device. The two have different fixes: routing means **record the device** alongside seed and layer and the numbers stay comparable within a device; not-routing means every cross-session comparison needs a **stated tolerance** and no equality check is meaningful. After this we know which, and we have the tolerance either way.

**4. WHAT IS AFFECTED.**
- Every gate in this repo that asserts an equality across readings. [E-004]'s ±0.02 reproduction gate was right by luck; [E-005]'s `torch.equal` was wrong and had to be replaced mid-run.
- [E-001]'s published floor median of **0.0809**, which is a first-connection value where later connections give **0.081093**.
- What an artifact must record. Today it is seed, layer and model. This decides whether the device joins them.
- T-008 closes.

**5. CONCLUSION IF WE DO IT.** Three branches.

- **If the hashes partition cleanly by GPU index:** it is routing. Record the device in every artifact; readings are comparable within a device and need a tolerance across devices. The fix is bookkeeping, and the instrument is sound once the bookkeeping exists.
- **If one GPU returns more than one hash:** it is not routing, or not only routing. No equality across readings is meaningful at all, every gate needs a tolerance derived from the observed spread, and the spread must be measured per quantity rather than assumed small.
- **If all 16 readings agree:** the effect is rarer than six readings suggested and this design cannot see it. Then the honest output is a frequency bound — "not observed in 16" — and T-008 stays open with a cheaper standing check rather than a conclusion.

**6. CONSEQUENCE OF NOT DOING IT.**
Every number this project publishes carries an unquantified session dependence, and the next reproduction check either passes by luck or fails for a reason nobody can name. [E-005] already spent one wrong verdict on exactly that.

**Controls, and what could make this wrong.**
- **The batch is held fixed and so are the positions.** Same prompts, same indices, one code path (`keys_at`), so nothing but the connection varies.
- **The hash is of the full tensor**, not of a derived scalar, because derived scalars are ratios read inside one trace and cancel most of this.
- **Runtime and GPU memory are recorded too**, so a hash that tracks load rather than device is visible.
- **16 readings is a frequency floor, not an estimate.** If a third value exists at low rate this design will probably miss it, and branch 3 says so rather than claiming stability.
- **Cost.** 16 remote passes, no edits, no gradients.

**Closed:** 2026-11-01. 16 readings of one 126-prompt batch through fresh connections:

    value               readings   served by
    edd2b2b152de2098           8   GPU 0
    54a1755349e607dc           8   GPU 2

    floor median    within a GPU   0.000e+00
                    across GPUs    3.110e-06

**Branch 1.** Perfect partition in both directions — each value from one GPU, each GPU one value. It is per-connection routing; the devices alternated rather than arriving in blocks. Anchor coefficients read 1.000 with deviation 0.000e+00 on all 16 readings and both devices, because `k` and `k*` share a trace and the ratio cancels the device entirely.

**And the branch does not finish the job.** Four floor medians now exist for the same 42 probes — 0.08087725 ([E-001], 10-31), 0.08094215 ([E-005] first reading), 0.08109000 (GPU 0), 0.08109313 (GPU 2). Observed range **2.16e-04**, of which the device is **1.4%**. Two more sources were tested rather than assumed: batch composition contributes **zero**, and where the dot product runs contributes 5.06e-06 at the median but **2.98e-03 per item**. The rest is unattributed and is **T-009**.

**What it changes.** No gate asserts bit-identity across readings. A cross-session comparison of a cross-trace quantity needs a tolerance of at least **2.2e-04**. A ratio read inside one trace is preferred wherever the question allows, because it is immune to all of this — which is why every anchor gate here survived without anyone knowing the effect existed, and why [E-004]'s ±0.02 gate was right for a reason it did not state.

Artifacts: `results/E-006-session-variation.json`, `results/E-006-summary.md`, `agents/shared/decisions.md` → [E-006], `src/editreach/coefficient.py` → `keys_at(..., meta_out=)`.

---

## C-005 · Is `TransformersModel` the same instrument as `LanguageModel`, or a different one?

**Status:** closed
**Opened:** 2026-11-01
**Closed:** 2026-11-01 — **branch 1**, after the card's own criterion turned out to be unsatisfiable

**1. WHERE WE ARE.**
`editreach.remote.connect` calls `nnsight.LanguageModel`, which warns on every run: *"LanguageModel is deprecated; use TransformersModel(repo_id, task='text-generation') instead."* Every number in edit-slice and in [E-001]–[E-004] was read through it. nnsight is 0.8.1 and `TransformersModel` imports.

**2. WHAT WE ARE DOING.**
Load the same model under both loaders and compare three things: the module paths `arch.py` resolves, the raw key vectors at layer 5 on the 42 anchor-prefix and 42 anchor-floor prompts, and the two gate quantities — the anchors pinning at 1.000 and the floor median at 0.0809.

**3. WHY.**
We do not know whether switching loaders is an **upgrade** or a **re-baseline**. If activations are bit-identical the switch is free and should be taken before more numbers accumulate behind a deprecated call. If they are not, every cross-run comparison in this repo would silently straddle two instruments, and the switch becomes a decision with a cost rather than housekeeping. After this we know which, with a number.

**4. WHAT IS AFFECTED.**
- `editreach.remote.connect`, and through it all of edit-slice's 79 scripts via the shims.
- Every cached tensor on disk — the [E-014] delta cache, `E001_coefficients.json`, `E004_keys.pt` — which were written under `LanguageModel` and would be mixed with new readings.
- T-006 closes.
- If the loaders differ, [E-039]'s reproduction in [E-004] (0.9334 against 0.933) becomes the *last* clean cross-session check, and future ones need the loader recorded alongside the seed.

**5. CONCLUSION IF WE DO IT.** Three branches.

- **If module paths match and activations are bit-identical:** the switch is housekeeping. Take it, record the equality, and the deprecation stops being a liability.
- **If paths match but activations differ:** it is a re-baseline, not an upgrade. Record the magnitude, **do not switch**, and add the loader to what every artifact records alongside seed and layer. A silent re-baseline is the expensive version of this.
- **If module paths differ:** `arch.py` needs a second mapping and the switch is a real job, not a line. Then the question is scheduled rather than answered, and nothing changes until it is.

**6. CONSEQUENCE OF NOT DOING IT.**
A deprecation gives notice once, and the notice is being spent. [E-047] was the loud kind of dependency failure and still cost six wrong diagnoses; this one is the quiet kind, and the quiet kind is discovered when a loader is removed in a version bump, with a cache full of numbers nobody can place.

**Controls, and what could make this wrong.**
- **Both gates run under both loaders.** The anchors are the one quantity known analytically — they must read 1.000 whatever loads the model — and the floor at 0.0809 is the empirical companion, from [E-001]'s own output over 42 items.
- **Bit-identical means bit-identical.** Branch 1 requires `torch.equal`, not `allclose`. Activations arrive in bf16; a loader difference of one ulp is still a difference, and `allclose` is how a re-baseline gets recorded as an upgrade.
- **Same prompts, same positions, same batch shape.** Both loaders are read through `keys_at`, so padding and position arithmetic are shared and cannot differ between the arms.
- **Cost.** Four remote passes, no edits and no gradients.

**Closed:** 2026-11-01. Module paths identical. Three readings per loader, 84 prompts:

    comparison              pairs   worst |d|   max fraction differing
    WITHIN  language            3   6.250e-01        0.9394
    WITHIN  transformers        3   0.000e+00        0.0000
    BETWEEN the two             9   6.250e-01        0.9394

**Branch 1 — but not by the test this card wrote.** Field 5 asked for `torch.equal` bit-identity, and that is **unsatisfiable on this platform**: two readings through the *same* loader, on byte-identical inputs, differ on 94% of elements. The criterion was not relaxed to `allclose`; it was replaced with a repeat design, and the error is recorded rather than waived.

Varying the loader on its own shows the within-loader spread equals the between-loader spread. The loader is not the variable. The two are the same instrument at this platform's reproducibility, and the gates agree: anchors pin at exactly 1.000 in all six readings, floor median within 2e-4 of [E-001]'s 0.0809.

**The switch is safe and is not taken.** Changing the loader every recorded number was read through, on the day the instrument was found to vary between sessions, is two changes with one unmeasured. `connect(loader=...)` is switchable, default `"language"`, one line away whenever wanted.

**What this cost and bought.** The card's first run returned "branch 2, do not switch" on one reading per loader. That verdict was wrong, and it was wrong in the direction that feels responsible — which is the kind that survives review. Same shape as C-004: a difference is attributable only once the thing it is attributed to has been varied by itself.

**Spawned T-008**, which is larger than the question asked: readings differ between NDIF serving sessions. [E-001]'s published floor of 0.0809 is a first-connection value; later connections give 0.081093.

Artifacts: `results/E-005-loader-parity.json`, `results/E-005-summary.md`, `agents/shared/decisions.md` → [E-005], `src/editreach/remote.py` → `connect(loader=...)`.

---

## C-004 · Is the hop-2 coefficient at floor, when the floor is read on the hop-2 prompts themselves?

**Status:** closed
**Opened:** 2026-11-01
**Closed:** 2026-11-01 — **branch 1**, reached through branch 2 and a confound

**1. WHERE WE ARE.**
[E-039] (edit-slice, 2026-10-15) already measured most of T-005. On MQuAKE-CF-3k, 513 single-edit two-hop instances, layer 5, no edit applied: the coefficient at the subject position is **0.933** when the question names the edited subject (hop-1, n=213) and **0.055** at the final token when it does not (hop-2, n=300), IQR 0.039. Two floors measured elsewhere bracket that: **0.069** from a permuted `k*` on RippleEdits [E-038], and **0.027** from a different token on MQuAKE [E-039].

**2. WHAT WE ARE DOING.**
Re-read [E-039]'s same 513 instances, saving the key vectors rather than only the scalars, and compute for every hop-2 question a **floor on that very prompt**: its coefficient against each of the other 299 instances' `k*`, reported as the median over donors. Then compare the own-`k*` coefficient against that same-prompt floor, paired, question by question.

**3. WHY.**
T-005's falsifier asked for the far-field coefficient "against the different-subject floor **on the same prompts**". [E-039] compared it against floors from a different corpus and a different construction. They converge, which is good evidence and is not the control that was specified. A reviewer can say: MQuAKE's questions are longer and multi-hop, so perhaps their floor is 0.02 and 0.055 is two and a half times it. After this we know whether 0.055 is at its own prompts' floor or above it, and T-005 closes either way.

**4. WHAT IS AFFECTED.**
- T-005 closes, and with it the scope claim on the whole instrument: **contamination detector, not propagation detector**. That sentence is currently unwritten anywhere, which is the thing worth fixing — C-001 denied that the coefficient predicts effect, and this says where it is blind.
- [E-039]'s decision entry gains the control it names as missing, or a correction.
- The direct-exposure critique of MQuAKE, which currently rests on counting prompt strings; this is the measured version.
- If hop-2 comes back **above** its own floor, [E-039]'s "the floor is not an artifact of how either control was built" is weakened, and the two convergent floors become two floors that happen to agree on other corpora.

**5. CONCLUSION IF WE DO IT.** Three branches.

- **If hop-2 own-`k*` sits at its same-prompt donor floor:** the coefficient has no dynamic range in the far field. The instrument is a contamination detector — it tells you an edited subject is named in a prompt, and it is silent about propagation through relations. That is narrower than anything claimed so far and it should be claimed by us, not found by a reviewer.
- **If hop-2 sits meaningfully above its own floor:** there is far-field signal after all, the instrument is more than a screen, and the three-corpus floor convergence in [E-039] was misleading about this corpus. T-005 then becomes a live measurement question rather than a scope note.
- **If the re-read fails to reproduce [E-039]'s 0.933 / 0.055:** something moved between 2026-10-15 and now — the loader, the tokenizer, the key site — and nothing else in this card may be read until that is explained. **This is the cheapest branch and the one most worth having**, because every number in edit-slice was read through the same path.

**6. CONSEQUENCE OF NOT DOING IT.**
The instrument's blind spot stays stated as a convergence argument across corpora rather than a measurement on the prompts in question, and the narrowed claim stays unwritten — which means the first person to write it down is a reviewer.

**Controls, and what could make this wrong.**
- **The gate is reproduction, not an anchor.** [E-039]'s hop-1 natural arm at 0.933 and hop-2 at 0.055 are the two numbers this re-read must return. They were read with `k*` cast through `half()`; this reads in float32 in-trace, so exact equality is not expected and a tolerance is stated in advance: **±0.02 on each median**. Outside that, branch 3.
- **The floor is a distribution, not a donor.** Every hop-2 question is scored against all 299 other instances' `k*` and the median is taken, so no single arbitrary pairing can carry the result. The spread is reported.
- **Denominator.** Each donor coefficient uses its own `k*·k*`, as the definition requires; using the own-subject denominator with a donor numerator would manufacture a floor.
- **Delivery, not effect.** Unchanged and restated: nothing here measures how far an answer moves. [E-028d], 2.96x.
- **Cost.** One remote pass per instance, 513 traces, no edits and no gradients. All donor arithmetic is offline.

**Closed:** 2026-11-01. Reproduction gate passed: hop-1 0.9334 and hop-2 0.0544 against [E-039]'s 0.933 and 0.055, inside the ±0.02 stated in advance.

    hop-2 far field, n=900           floor    excess over it
      SAME-relation donors           0.0481    +0.0002   CI (+0.0001, +0.0004)
      DIFFERENT-relation donors      0.0294    +0.0244   CI (+0.0215, +0.0271)

    hop-1 near field, n=639
      SAME-relation donors           0.0506    +0.8439   CI (+0.8379, +0.8500)

**Branch 1, and the route there is the part worth keeping.** Against *all* donors the far-field excess is +0.0232 with an interval excluding zero — branch 2, "there is far-field signal after all". That was wrong, and it was wrong for a reason the card had not listed: a hop-2 subject is the chain's middle entity, so the question is *about* it indirectly and topical overlap alone produces that excess. Nearly every donor carries a different relation, so the all-donor floor is the different-relation floor wearing another name.

Split the donors by relation and the far-field excess is **+0.0002**. A stranger's edit on the same relation reaches the question as much as the real subject's edit does. The same control barely touches the near field.

**The claim, stated by us rather than by a reviewer:** the coefficient is a contamination detector — it tells you an edited subject is named in a prompt — plus a relation detector. It is not a propagation detector, and multi-hop propagation is where it is asked to work.

**What it does not say.** Delivery, not effect. A floor here does not mean an edit fails to reach the answer; the layer-5 alteration travels on through attention where this measure cannot follow.

Artifacts: `results/E-004-far-field-floor.json`, `results/E-004-summary.md`, `agents/shared/decisions.md` → [E-004], `src/editreach/coefficient.py` → `keys_at`.

---

## C-003 · Does an edit break the old answer and supply the new one by two different routes?

**Status:** closed
**Opened:** 2026-11-01
**Closed:** 2026-11-01 — **branch 1**, and the two halves separate in opposite directions

**1. WHERE WE ARE.**
[E-002] measured **destruction** over 495 probes: editing *this person rather than someone else* is worth +0.0583 paired median, editing *this fact rather than another fact about the same person* is worth +0.0009 — sixty-five times less. [E-014], on a different probe set and a different metric family, has **destination** at 67% for the real edit against 5% for the same-subject control.

**2. WHAT WE ARE DOING.**
Re-score the same 495 probes of [E-002] for destination — the post-edit top-1 token over the full vocabulary, under the `real`, same-subject `ctl` and different-subject `other` arms — and report, per arm and per family, the fraction whose top-1 token begins a city in that subject's injected target country.

**3. WHY.**
The two-route reading is assembled from three experiments built for other questions, with different probe sets and different metric families. We do not know whether destruction and destination separate **on one probe set under one metric**. After this we have three destination rates on the exact 495 probes that produced the destruction numbers, and the split is measured or it is not.

**4. WHAT IS AFFECTED.**
- T-007 becomes answered or dropped.
- The **[E-013] scope note** appended to `edit-slice/agents/shared/decisions.md`, which currently rests on comparing [E-002] against [E-014] *across* probe sets. This decides whether it can rest on one.
- The direct-exposure critique, whose behavioural leg is destruction only.
- [E-014]'s 67% / 5% is either replicated on a second probe set or contradicted.

**5. CONCLUSION IF WE DO IT.** Three branches, written before the run.

- **If `real` ≫ `ctl` and `real` ≫ `other` on destination, on the same probes where `real ≈ ctl` on destruction:** the split is measured rather than inferred. One rank-one update does two separable things — it breaks the old answer because it touched that subject's key, and it supplies the new one because of what it said.
- **If `real ≈ ctl` on destination too:** there is no split. The apparent one was an artefact of comparing two experiments across probe sets and metrics, and the [E-013] scope note is wrong and is struck rather than left standing.
- **If all three arms sit near zero:** these probes have no measurable destination at all, and the 495-probe set cannot answer the question. That would mean [E-002]'s movement numbers record destruction with nowhere identifiable for the mass to go — which needs recording before anything leans on them. **This is the branch that costs the most.**

**6. CONSEQUENCE OF NOT DOING IT.**
The two-route reading stays a story told across three experiments, the [E-013] scope note stays cross-set, and the direct-exposure critique stands on one behavioural leg instead of two.

**Controls, and what could make this wrong. Three were checked before the run rather than after.**

- **Magnitude, `real` against `ctl`.** Never matched, unlike the donor arm in [E-002]. **Checked, and the honest version is narrower than the first one written here:** the *signed* paired median difference in `‖delta_v‖/‖k*‖` is +0.0899 with `ctl` weaker in 20 of 42, so `ctl` is not systematically the weaker edit. But the *unsigned* median difference is 0.7614 over a range of 2.627, so the two arms are **not matched subject by subject** — only unbiased in direction. That is enough for an aggregate hit rate over 495 probes and it is **not** enough for a per-subject claim, which this card therefore does not make.
- **First-token resolution.** The probes ask for a *city* and the edit injects a *country*, so a bare argmax-equals-target test would under-count badly. A hit is instead "the top-1 token begins a city in the target country". **Checked:** the 81-city map gives 80 distinct first tokens, every one resolving to exactly one country. Zero ambiguity, so the mapping adds no slack of its own.
- **The `ctl` arm cannot deliver its own content here, and that bounds the claim.** The control edit injects an occupation (`By profession, {} is a` -> `urban planner`) while these probes ask for a city, so no arm-symmetric "does each arm deliver *its own* target" check exists on this probe set. What this measures is whether **content that can answer the question is what arrives** — not whether every edit delivers its own content somewhere.
- **The anchor gate runs again.** 42 traces, and it has caught two faults.
- **Cost.** Three remote passes over 495 probes, grouped by subject. The `base` arm is not re-run: [E-001] holds `base_token` and `p_base` on disk, so T-007's "four arms" costs three.

**Closed:** 2026-11-01. Paired over the same 495 probes, bootstrap 10,000, seed 1538:

    destination   real - ctl     +0.2828   95% CI (+0.2424, +0.3232)
                  ctl  - other   +0.0000   95% CI (-0.0101, +0.0101)

    destruction   real - ctl     +0.0009   95% CI (+0.0004, +0.0024)   [E-002]
                  ctl  - other   +0.0583   95% CI (+0.0472, +0.0732)   [E-002]

Hit rates: base 1%, real 29%, ctl 1%, other 1%. Discordant pairs, real against ctl: **142 to 2**.

**Branch 1.** On the same probes, destruction barely distinguishes the real edit from a different edit on the same person and strongly distinguishes that person from someone else. Destination does the exact reverse. One rank-one update breaks the old answer because it touched that subject's key, and supplies the new one because of what it said.

The same-subject control sits at the **base rate** on destination, so it delivers nothing rather than a little — while destroying the old answer to within +0.0009 of the real edit.

This replicates [E-014]'s 67% / 5% on a second probe set in a different metric family, at 29% / 1%. The levels differ because [E-014] scored a restricted city pool by teacher forcing and this is a free argmax over the whole vocabulary. **The separation carries; the level does not**, and nothing here should be quoted as a rate.

**What it does not settle, carried forward.** The control injects an occupation and these probes ask for a city, so there is no arm-symmetric check that each arm delivers *its own* content. What is measured is that content which can answer the question is what arrives. Aggregate only: the two arms are unbiased in magnitude direction, not matched per subject.

Artifacts: `results/E-003-destination.json`, `results/E-003-summary.md`, `agents/shared/decisions.md` → [E-003].

---

## C-002 · Does an edit's effect depend on what it said, or only on whose key it touched?

**Status:** closed
**Opened:** 2026-10-31
**Closed:** 2026-10-31 — **branch 1**, and the gap is quantified

**1. WHERE WE ARE.**
[E-001] measured a raw correlation of 0.522 between predicted reach and measured movement, which falls to an excess of 0.085 (CI −0.003 to 0.172) once a **same-subject control edit** is removed — that control alone accounting for about 72% of the median movement.

**2. WHAT WE ARE DOING.**
Score the same 495 probes a third time, under a **different subject's** cached edit — subject B's `delta_v` and `k*` applied while probing subject A — and report the three medians side by side against the `real` and same-subject `ctl` arms already measured, per family.

**3. WHY.**
We do not know whether an edit moves a probe because of *what it said* or because of *whose key it touched*. [E-001] is consistent with the second and cannot distinguish them, because both its arms edit the same person. A third arm that changes the person while holding everything else fixed separates them. After this we have three medians and two contrasts.

**4. WHAT IS AFFECTED.**
- The post-hoc reading recorded in [E-001] — that subject-keyed movement may be the phenomenon rather than the confound — either becomes a pre-stated result or dies. It may not be used either way until this closes.
- The direct-exposure critique, which currently rests on **counting** whether the edited subject appears in a prompt. This decides whether it can also rest on behaviour.
- [E-013]'s control design in edit-slice: if movement is subject-keyed, the same-subject control removes signal rather than noise *for this class of question*, which is a scope note that belongs on that decision.

**5. CONCLUSION IF WE DO IT.** Three branches, because the third is the one that would hurt and it has to be written down before the run.

- **If `real ≈ ctl` and both ≫ `different-subject`:** movement is keyed on the subject, not the content. Direct exposure is then demonstrable in behaviour and not only in prompt-counting, and the direct-exposure critique gains a second leg. The same-subject control gets a scope note in [E-013].
- **If `real` is meaningfully above `ctl`:** content does matter, [E-001]'s post-hoc reading is wrong and is struck from the record rather than left standing, and the conclusion that the coefficient fails to predict effect gets *stronger* — it had content to predict and did not.
- **If all three arms are alike, different-subject included:** we are measuring generic instability and nothing is keyed on anything. That would undercut [E-001]'s raw 0.522 as well as the behavioural half of the critique, and it would mean the floor arms in every prior run need re-reading. **This is the branch that costs the most and it is the reason the arm is worth running.**

**6. CONSEQUENCE OF NOT DOING IT.**
[E-001]'s most interesting sentence stays post-hoc and therefore unusable, the direct-exposure critique rests on arithmetic over prompt strings alone, and we would hold a finding we cannot name without over-reading it.

**Controls and what could make this wrong.**
- **Magnitude.** Edits differ in `norm_ratio`. B's edit must be matched to A's in magnitude or a weak different-subject arm proves nothing. Pair by closest `norm_ratio`, record the residual spread, and report it.
- **Pairing.** Deterministic: subjects sorted by `case_id`, A paired with the nearest-magnitude B that is not A. Recorded in the output.
- **The anchor gate runs again.** It is 42 traces and it has already caught two faults.

**Closed:** 2026-10-31. Paired median differences over 495 probes, bootstrap 10,000, seed 1538:

    real  -  same-subject      +0.0009   95% CI (+0.0004, +0.0024)
    same-subject - diff-subj   +0.0583   95% CI (+0.0472, +0.0732)
    real  -  diff-subject      +0.0842   95% CI (+0.0667, +0.0974)

**Branch 1.** Editing *this person rather than someone else* is worth **0.0583**. Editing *this fact rather than another fact about the same person* is worth **0.0009** — sixty-five times less. Both intervals exclude zero, so content is not irrelevant; it is detectable and small.

Donor edits were matched on magnitude (median |difference| 0.0255 against a range of 2.627), so the different-subject arm is not merely weaker.

**A statistic that would have misled, recorded because it nearly did.** The per-arm medians read 0.0977 / 0.0625 / 0.0016, which makes `real` look 56% above the same-subject control. That is a difference *of medians* over skewed distributions. The paired median *of differences* is +0.0009. The arms are measured on the same probes, so the paired form is the one that answers the question, and the unpaired one overstates the content effect by about sixty-fold.

**What this settles.** The post-hoc reading recorded in [E-001] is now pre-stated and measured: a probe moves because an edit happened to its subject, almost regardless of what the edit said. Direct exposure is demonstrable in behaviour and not only by counting prompt strings.

**What it costs — narrowed after writing the scope note.** The first version of this line said [E-013]'s same-subject control "removes the signal" for this class of question. Reading [E-013] and [E-014] properly does not support the broad form: [E-014] has that same control at **5%** against the real edit's **67%** on whether the answer lands in the injected country.

Both hold because they measure different halves. This card measured **destruction** — what the old answer loses — which is subject-keyed. [E-014] measured **destination** — where the new answer goes — which is content-specific. The same-subject control is the wrong control for the first and the right one for the second. Recorded as **[E-013] Scope note** in edit-slice, appended.

---

## C-001 · Does predicted reach predict measured movement?

**Status:** closed
**Opened:** 2026-10-31
**Closed:** 2026-10-31 — **DENIED.** Raw Spearman 0.522 (95% CI 0.450–0.587) over 495 probes, falling to an excess of 0.085 (−0.003, +0.172) once the same-subject control is removed, so the interval straddles zero. *Verdict added to this line 2026-11-10: it had lived only in the closure section below, and every other card carries its verdict here — which left the generated lab log showing this card closing with a date and nothing else.*

**1. WHERE WE ARE.**
The coefficient is exactly 1.000 for probes that begin with the edited subject (216 cells, four models 6B–405B, worst deviation 0.00e+00), falls from about 0.93 at layer 5 to about 0.52 at layer 24 when a preamble precedes the subject, and sits at a 0.082 different-subject baseline — all of it read from the **unedited** model, with no edit ever run at any layer but 5.

**2. WHAT WE ARE DOING.**
For each of the 42 subjects used in [E-014]/[E-016] and a fixed probe set, compute the layer-5 coefficient on the unedited model, then apply the ROME edit and measure the movement of the same (subject, probe) pair, and report the Spearman correlation between the two with the per-probe baseline removed.

**3. WHY.**
We do not currently know whether the coefficient carries any behavioural content. After this we have a correlation with an interval, over 42 × k pairs, and we know whether a threshold can be set on it at all.

**4. WHAT IS AFFECTED.**
- The pre-edit screen proposal, stated in writing on 2026-10-31.
- `ai/edit-slice/CLAUDE.md`, "Probe generation": *"If predicted and measured rankings correlate, cheap predictor plus mechanistic story. If they diverge, that divergence is the finding."*
- The standing sentence "a screen built on it is a proposal, not an instrument" either resolves or hardens into a permanent limit.

**5. CONCLUSION IF WE DO IT.**
- **If the correlation holds** (ρ ≥ 0.5 after removing the per-probe baseline): the coefficient is a usable pre-edit triage signal, a cut can be chosen, and the next card reports false-positive and false-negative rates at that cut. Only then is the word "screen" earned.
- **If it does not** (ρ near zero, or the interval spans zero): the coefficient is a delivery statistic with no behavioural meaning. The screen proposal is withdrawn in writing. Note what survives either way: the direct-exposure critique of RippleEdits falls back to **counting** whether the edited subject appears in the prompt, which needs no coefficient and is unaffected by this result.

**6. CONSEQUENCE OF NOT DOING IT.**
We would keep recommending a gate with no threshold and no error rates — an instruction with a verb and an object that nobody, including us, can carry out. The ask that proposal makes cannot be answered by anyone until this number exists.

**Closed:** 2026-10-31 — **deny branch**, on the number written in field 5 before the run.

    overall, raw         rho = 0.522   95% CI (0.450, 0.587)
    overall, excess      rho = 0.085   95% CI (-0.003, 0.172)

The test was always the second line: movement in excess of what a **different edit on the same person** produces. It does not reach 0.5, and its interval touches zero. By the branch written in advance, the coefficient is not established as a predictor of a particular edit's effect, and a screen built on it stays a proposal.

What the raw number means, since 0.522 is real and will be quoted. A high-coefficient probe does move more. But the same-subject control already accounts for about **72%** of the median movement (|movement| 0.1034, |control| 0.0740), so what the coefficient tracks is *this probe is sensitive to an edit on this subject*, not *this edit reaches this probe*.

Per family, the excess medians are 0.000–0.031. `exposure` is the largest at 0.031 — the item where the edited subject sits in the prompt while the question is about someone else.

**What survives, as field 5 said it would.** The direct-exposure critique of RippleEdits rests on **counting** whether the edited subject appears in a prompt. That needs no coefficient and is untouched by this result.

**An unresolved tension, recorded rather than resolved.** The same-subject control was introduced in [E-013] to separate contraction from subject-keyed leakage. Here subject-keyed leakage may *be* the phenomenon: if an item moves because an edit happened to this subject rather than because of what the edit said, that is the direct-exposure claim, and controlling it away removes the signal. That reading is **post-hoc** and licenses nothing. It needs its own card with its branches written first.

---

## Closed cards

### C-001 · Does predicted reach predict measured movement? — DENIED

Closed 2026-10-31. `results/E-001-predicted-vs-measured.json`. 495 probes, 42 subjects, Llama-3.1-8B at layer 5, edits from the [E-014] cache. Anchor gate passed at 0.000e+00 after two faults were fixed ([E-001] in decisions.md).

Independent replication worth noting: the `anchor-floor` family — same prompt shape, different person — came back at a median coefficient of **0.0809**, against [E-018]'s floor of 0.082.
