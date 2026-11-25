#!/usr/bin/env python3
"""C-009: RAVEL interchange intervention accuracy, reimplemented on nnsight.

    python3 agents/engineer/workspace/ravel_iia.py --selftest
    python3 agents/engineer/workspace/ravel_iia.py --layers 5 --n 200

WHAT THIS IS AND IS NOT. MIB's own runner reaches Llama-3.1-8B through pyvene and
a locally loaded model. This project reaches it through nnsight on NDIF, so the
Full Vector baseline is reimplemented here over **their data, their splits, their
metric and their checker**. The card says plainly what that costs: the number
stops being externally scored. [T-018] holds the reproduction check that buys
back what can be bought back - this implementation must land on MIB's published
Full Vector numbers before any layer-5 reading is quoted.

THE METRIC, SPELLED OUT, BECAUSE IT IS THE PART EASIEST TO GET SUBTLY WRONG.

Each row asks the model one attribute of one city. An interchange intervention
copies the residual stream at the city's last token from a COUNTERFACTUAL prompt
into the base prompt, at one layer, and asks what the model now answers.

The expected answer is not "the source's value". It is what the causal model
says, which depends on whether the question is about the variable we moved:

    target variable V, base b, source s, question q = b["attribute"]
    q == V   ->  expect s[V]      the moved variable should carry
    q != V   ->  expect b[q]      every other variable should NOT move

So half of this metric is selectivity, and a method that simply drags everything
across scores badly on the second line. That is exactly why Full Vector - which
swaps the whole vector and so moves every attribute at once - is the weak
baseline in MIB's table rather than the strong one.

THE CHECKER IS PORTED RATHER THAN INVENTED, for the same reason. A mismatch
against MIB's published number has to mean the intervention differs, not that we
scored strings differently. Theirs is a substring test over lowercased,
punctuation-stripped output with a handful of geographic special cases; all of it
is reproduced in `check()` below with its oddities intact, including that an
empty expected option matches anything.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

ATTRS = ("Continent", "Country", "Language")
COUNTERFACTUALS = ("prompt_template_counterfactual",
                   "attribute_counterfactual",
                   "wikipedia_counterfactual")


# --------------------------------------------------------------------------
# The checker, ported from MIB-causal-variable-track/baselines/ravel_baselines.py
# --------------------------------------------------------------------------
def check(output_text: str | None, expected: str) -> bool:
    """True when the generated text counts as the expected answer.

    Ported deliberately, oddities included. Note that `expected.split(",")` on a
    value with a trailing comma yields an empty option, and `"" in anything` is
    True - so such a row is scored correct whatever the model said. That is in
    the original and is reproduced rather than fixed, because fixing it here
    would make our number incomparable with the published one. Any such rows are
    counted and reported by the runner instead.
    """
    if output_text is None:
        return False
    output_clean = re.sub(r"[^\w\s]+", "", output_text.lower()).strip()
    expected_list = [e.strip().lower() for e in expected.split(",")]
    if any(part in output_clean for part in expected_list):
        return True

    bare = output_clean.replace("the ", "")
    for want in expected_list:
        if want in ("united states", "united kingdom", "czech republic"):
            if bare.startswith(want) or bare.startswith("england") or bare == "us":
                return True
        elif want == "south korea":
            if bare.startswith("korea") or bare.startswith("south korea"):
                return True
        elif want in ("persian", "farsi"):
            if bare.startswith("persian") or bare.startswith("farsi"):
                return True
        elif want == "oceania":
            if bare.startswith("australia"):
                return True
        elif want == "north america":
            if "north america" in bare or bare == "na" or bare.startswith("america"):
                return True
        elif want in ("mandarin", "chinese"):
            if "mandarin" in bare or "chinese" in bare:
                return True
    return False


def expected_answer(base: dict, source: dict, target: str) -> str:
    """What the causal model says the answer becomes after moving `target`."""
    asked = base["attribute"]
    if asked not in ATTRS:
        raise ValueError(f"base asks {asked!r}, which is not one of {ATTRS}")
    return source[target] if asked == target else base[asked]


def degenerate(expected: str) -> bool:
    """Does this expected value hit the empty-option hole in the checker?"""
    return any(e.strip() == "" for e in expected.split(","))


def load(split: str = "val") -> list[dict]:
    """The released rows, read without the `datasets` package.

    `datasets` cannot be installed here: it raises InvalidVersion on this Python
    and drags huggingface_hub past the pin that `transformers` needs. The parquet
    is public, so it is fetched and read directly.
    """
    from huggingface_hub import hf_hub_download
    import pyarrow.parquet as pq
    path = hf_hub_download("mib-bench/ravel",
                           f"data/{split}-00000-of-00001.parquet",
                           repo_type="dataset")
    return pq.read_table(path).to_pylist()


def pairs(rows: list[dict], target: str, kind: str) -> tuple[list[dict], dict]:
    """Base/source pairs for one target variable and one counterfactual type.

    Returns the pairs and a count of what was dropped. **Rows are dropped, never
    guessed.** Some released rows carry `null` for an attribute, so the causal
    model has no answer to predict for them; counting those is the honest form
    and silently defaulting them to a string would put a wrong gold label into
    the denominator.
    """
    out, dropped = [], {"not_an_attribute": 0, "no_counterfactual": 0, "no_gold": 0}
    for i, r in enumerate(rows):
        if r["attribute"] not in ATTRS:
            dropped["not_an_attribute"] += 1
            continue
        s = r.get(kind)
        if not s or not s.get("prompt"):
            dropped["no_counterfactual"] += 1
            continue
        want = expected_answer(r, s, target)
        if not isinstance(want, str) or not want.strip():
            dropped["no_gold"] += 1
            continue
        # `row` is the index back into `rows`. A caller that needs anything else
        # off the source row MUST come back through this index and never look the
        # row up by its prompt text: base prompts are not unique (10,276 distinct
        # prompts over 15,950 val rows, so two rows in three share one), and a
        # prompt-keyed lookup silently returns a different row's counterfactual.
        # That bug scored the source arm of the filter at 0.31 instead of 0.79.
        out.append({"row": i,
                    "base_prompt": r["prompt"], "base_entity": r["entity"],
                    "asked": r["attribute"], "source_prompt": s["prompt"],
                    "source_entity": s["entity"], "target": target,
                    "expected": want, "degenerate": degenerate(want),
                    "kind": kind})
    return out, dropped


def entity_last_token(tokenizer, prompt: str, entity: str) -> int:
    """Index of the final token of `entity` inside `prompt`.

    Ported from MIB's `get_entity_last_token_position`, which searches with word
    boundaries and takes the **first** match - not the last. In a few-shot RAVEL
    prompt the exemplar city differs from the queried one, so first and last
    coincide; `audit_positions` below checks that rather than assuming it, because
    a prompt where they differ would intervene on the exemplar and the run would
    simply produce a wrong number with no error anywhere.

    Tokenisation follows the tokenizer's own defaults, special tokens included,
    exactly as the original does.
    """
    m = re.search(r"\b" + re.escape(entity) + r"\b", prompt)
    if m is None:
        return -1
    ids = tokenizer(prompt[:m.end()])["input_ids"]
    return len(ids) - 1


def audit_positions(tokenizer, ps: list[dict], n: int = 400) -> dict:
    """Does the computed index really land on the end of the entity?

    Three ways this can be wrong and none of them raises: the entity is absent,
    it occurs more than once so the first match is not the queried one, or the
    tokeniser's special tokens shift the index. Each is counted here, and the
    last is checked by decoding the token actually selected and asking whether
    the entity ends with it.
    """
    out = {"checked": 0, "missing": 0, "ambiguous": 0, "misaligned": 0,
           "examples": []}
    for p in ps[:n]:
        prompt, ent = p["base_prompt"], p["base_entity"]
        hits = list(re.finditer(r"\b" + re.escape(ent) + r"\b", prompt))
        if not hits:
            out["missing"] += 1
            continue
        if len(hits) > 1:
            out["ambiguous"] += 1
        i = entity_last_token(tokenizer, prompt, ent)
        ids = tokenizer(prompt)["input_ids"]
        if not 0 <= i < len(ids):
            out["misaligned"] += 1
            continue
        tok = tokenizer.decode([ids[i]])
        if not ent.lower().endswith(tok.strip().lower()) or not tok.strip():
            out["misaligned"] += 1
            if len(out["examples"]) < 5:
                out["examples"].append((ent, repr(tok)))
        out["checked"] += 1
    return out


def _blocks(model):
    inner = getattr(model, "model", None)
    if inner is not None and hasattr(inner, "layers"):
        return inner.layers
    return model.transformer.h


def batch_positions(tokenizer, prompts: list[str], indices: list[int]):
    """Where each prompt's entity token sits once the batch is padded.

    **nnsight left-pads**, measured rather than assumed: two prompts of 12 and 4
    tokens come back as a [2, 12, 4096] residual with the short one's real
    tokens at the END. So an entity at index `i` of an unpadded prompt of length
    `L`, in a batch whose longest member is `T`, sits at `T - L + i`.

    Getting this wrong does not raise. It patches a padding token, or a token of
    the wrong example, and the run produces a plausible wrong number - which is
    why `check_positions` exists and is called on the first batch.
    """
    lens = [len(tokenizer(p)["input_ids"]) for p in prompts]
    T = max(lens)
    return [T - L + i for L, i in zip(lens, indices)], lens, T


def check_positions(tokenizer, prompts, indices, entities) -> list[str]:
    """Does each computed batch position decode to the end of its entity?"""
    pos, lens, T = batch_positions(tokenizer, prompts, indices)
    bad = []
    for n, (prompt, ent) in enumerate(zip(prompts, entities)):
        ids = tokenizer(prompt)["input_ids"]
        j = pos[n] - (T - lens[n])
        if not 0 <= j < len(ids):
            bad.append(f"{ent!r}: position {pos[n]} outside the prompt")
            continue
        piece = tokenizer.decode([ids[j]]).strip().lower()
        if not piece or not ent.lower().endswith(piece):
            bad.append(f"{ent!r}: position {pos[n]} decodes to {piece!r}")
    return bad


def read_vectors(model, prompts: list[str], positions: list[int], layer: int,
                 *, remote: bool):
    """The residual stream after block `layer`, one vector per prompt, one trace.

    This is the whole point of batching: a trace costs 2.39s median against
    ~0.4s of server-side execution, so the round trip dominates and the only
    lever is how many examples ride in one.
    """
    import torch
    blocks = _blocks(model)
    with torch.no_grad(), model.trace(prompts, remote=remote):
        out = blocks[layer].output
        resid = (out[0] if isinstance(out, tuple) else out)
        idx = torch.tensor(positions, device=resid.device)
        rows = torch.arange(len(positions), device=resid.device)
        vecs = resid[rows, idx, :].save()
    return vecs


def generate_batched(model, tokenizer, prompts: list[str], indices: list[int],
                     layer: int, vectors, *, remote: bool,
                     max_new_tokens: int = 6) -> list[str]:
    """Greedy continuations for a whole batch, patched at each step.

    `max_new_tokens` traces for the batch rather than for each example. The
    patch is reapplied every step because the entity stays in context and an
    unpatched re-read would undo the intervention.
    """
    import torch
    blocks = _blocks(model)
    texts = list(prompts)
    done = [False] * len(prompts)
    for _ in range(max_new_tokens):
        pos, _, _ = batch_positions(tokenizer, texts, indices)
        with torch.no_grad(), model.trace(texts, remote=remote):
            out = blocks[layer].output
            resid = (out[0] if isinstance(out, tuple) else out)
            idx = torch.tensor(pos, device=resid.device)
            rows = torch.arange(len(pos), device=resid.device)
            resid[rows, idx, :] = vectors.to(resid.device).to(resid.dtype)
            # **Take the argmax REMOTELY.** `remote.py` says it in its own first
            # paragraph - "only scalars come back over the wire, never a
            # 128k-vocab logit tensor" - and saving the logits instead ignored
            # it. Measured: a batch-16 step shipped ~3.1MB and the round trip
            # took 9.7s against the 2.39s a small trace costs, so four fifths of
            # the wall clock was transport for a tensor whose only use was one
            # argmax. The argmax is B integers.
            nxt = model.lm_head.output[:, -1, :].argmax(dim=-1).save()
        nxt = nxt.tolist()
        for n, t in enumerate(nxt):
            if done[n]:
                continue
            piece = tokenizer.decode(t)
            if not piece:
                done[n] = True
                continue
            texts[n] += piece
    return [t[len(p):] for t, p in zip(texts, prompts)]


def read_vector(model, prompt: str, index: int, layer: int, *, remote: bool):
    """The residual stream after block `layer`, at one token of one prompt.

    One trace, one save, bound to a plain local name. Under `remote=True` the
    trace body executes on the server, so anything accumulated into a container
    inside it is discarded silently - see `ravel_hook_check.py`.
    """
    blocks = _blocks(model)
    with model.trace(prompt, remote=remote):
        out = blocks[layer].output
        vec = (out[0] if isinstance(out, tuple) else out)[0, index, :].save()
    return vec


def generate_patched(model, tokenizer, prompt: str, index: int, layer: int,
                     vector, *, remote: bool, max_new_tokens: int = 6) -> str:
    """Greedy continuation of `prompt` with one residual vector replaced.

    **Why more than one token, and why this is not an optimisation.** MIB's
    checker is a substring test over generated TEXT, and the answers are often
    several tokens - "Dominican Republic", "United States", "Mandarin Chinese".
    Scoring a single token marks every one of those wrong whatever the model
    did, which would depress our number against MIB's for a reason that has
    nothing to do with the intervention. The first probe run showed it: an
    unintervened model answered `'Domin'`, which is right and scores as wrong.

    The patch is reapplied at every step. The entity's position is fixed in the
    prompt and stays in context as tokens are appended, so leaving it out after
    the first step would let the model re-read the unpatched representation.

    Cost is honest rather than hidden: this is `max_new_tokens` traces per
    example, and at roughly 0.4s of queue each that sets the budget for any
    full run.
    """
    text = prompt
    for _ in range(max_new_tokens):
        lg = patched_logits(model, text, index, layer, vector, remote=remote)
        nxt = int(lg.argmax().item())
        piece = tokenizer.decode(nxt)
        if not piece:
            break
        text += piece
    return text[len(prompt):]


def patched_logits(model, prompt: str, index: int, layer: int, vector,
                   *, remote: bool):
    """Next-token logits for `prompt` with one residual vector replaced.

    The write is to the SAME site the read came from - block `layer`'s output,
    which `ravel_hook_check.py` established is the residual stream after block
    `layer` and therefore where this project's layer-`layer` edit lands.
    """
    blocks = _blocks(model)
    with model.trace(prompt, remote=remote):
        out = blocks[layer].output
        resid = out[0] if isinstance(out, tuple) else out
        resid[0, index, :] = vector
        logits = model.lm_head.output[0, -1, :].save()
    return logits


def probe_one(model, tokenizer, pair: dict, layer: int, *, remote: bool,
              tokens: int = 6) -> dict:
    """One base/source pair, end to end, with the unintervened answer beside it."""
    bi = entity_last_token(tokenizer, pair["base_prompt"], pair["base_entity"])
    si = entity_last_token(tokenizer, pair["source_prompt"], pair["source_entity"])
    if bi < 0 or si < 0:
        raise ValueError("entity not found in one of the prompts")

    # The unintervened answer is generated the same way, by patching the site
    # with the vector already there. Same code path, same token count, so a
    # difference between the two columns is the intervention and not the
    # decoding.
    own = read_vector(model, pair["base_prompt"], bi, layer, remote=remote)
    before = generate_patched(model, tokenizer, pair["base_prompt"], bi, layer,
                              own, remote=remote, max_new_tokens=tokens)

    vec = read_vector(model, pair["source_prompt"], si, layer, remote=remote)
    after = generate_patched(model, tokenizer, pair["base_prompt"], bi, layer,
                             vec, remote=remote, max_new_tokens=tokens)

    return {"asked": pair["asked"], "target": pair["target"],
            "base_entity": pair["base_entity"], "source_entity": pair["source_entity"],
            "base_index": bi, "source_index": si,
            "unintervened": before, "intervened": after,
            "expected": pair["expected"],
            "correct_before": check(before, pair["expected"]),
            "correct": check(after, pair["expected"])}


def score_batch(model, tokenizer, ps: list[dict], layer: int, *, remote: bool,
                tokens: int = 6, batch: int = 32, verbose: bool = False) -> dict:
    """Interchange intervention accuracy over `ps`, batched.

    Four traces' worth of work per batch: read the base vectors, read the source
    vectors, generate the unintervened continuations, generate the intervened
    ones - the last two being `tokens` traces each. So a batch of B costs
    `2 + 2 * tokens` traces however large B is, which is the only reason a run
    of any size is affordable.

    **BATCH SIZE CHANGES INDIVIDUAL VERDICTS, AND THAT IS NOT A BUG HERE.**
    Measured 2026-11-24: the same source vector read alone and read inside a
    batch of six differs by up to 0.0078, which is bfloat16 granularity and not
    a position error - the clean next-token prediction is identical batched or
    alone, and `check_positions` passes. Batching changes reduction order and
    kernel choice, nothing more.

    It is still enough to flip an example that sits near a decision boundary.
    `Portsmouth <- Abau` asked for a language answers `English` at batch 1 and
    `Tok Pisin` at batch 6 - the base city's answer against the patched city's,
    contested, and decided by noise. That is the same class as this project's
    [C-006] and [T-008]: readings that move with the hardware and the session.

    So **batch size is part of a run's configuration and is recorded with every
    result**, exactly as the serving device is. Per-example verdicts are not
    reproducible across batch sizes; the aggregate is the quantity, and whether
    the aggregate is stable across batch sizes is a control that has to be run
    rather than assumed.
    """
    hits = hits_before = n = 0
    checked_positions = False
    for start in range(0, len(ps), batch):
        chunk = ps[start:start + batch]
        bp = [c["base_prompt"] for c in chunk]
        sp = [c["source_prompt"] for c in chunk]
        bi = [entity_last_token(tokenizer, c["base_prompt"], c["base_entity"])
              for c in chunk]
        si = [entity_last_token(tokenizer, c["source_prompt"], c["source_entity"])
              for c in chunk]
        if min(bi + si) < 0:
            raise ValueError("an entity was not found in its prompt")

        if not checked_positions:
            bad = (check_positions(tokenizer, bp, bi, [c["base_entity"] for c in chunk])
                   + check_positions(tokenizer, sp, si,
                                     [c["source_entity"] for c in chunk]))
            if bad:
                raise ValueError("batch positions are wrong:\n  "
                                 + "\n  ".join(bad[:5]))
            checked_positions = True

        bpos, _, _ = batch_positions(tokenizer, bp, bi)
        spos, _, _ = batch_positions(tokenizer, sp, si)
        own = read_vectors(model, bp, bpos, layer, remote=remote)
        src = read_vectors(model, sp, spos, layer, remote=remote)
        before = generate_batched(model, tokenizer, bp, bi, layer, own,
                                  remote=remote, max_new_tokens=tokens)
        after = generate_batched(model, tokenizer, bp, bi, layer, src,
                                 remote=remote, max_new_tokens=tokens)

        for c, b4, af in zip(chunk, before, after):
            n += 1
            hits_before += check(b4, c["expected"])
            hits += check(af, c["expected"])
            if verbose:
                print(f"  {'ok ' if check(af, c['expected']) else 'NO '}"
                      f"{c['base_entity']!r} <- {c['source_entity']!r} "
                      f"asks {c['asked']:<9} before {b4.strip()[:28]!r} "
                      f"after {af.strip()[:28]!r} want {c['expected']!r}")
    return {"n": n, "iia": hits / n if n else None,
            "unintervened": hits_before / n if n else None,
            "batch": batch, "tokens": tokens, "layer": layer}


def selftest() -> int:
    """Everything above runs offline, so it is checked offline."""
    fails = []

    def eq(got, want, what):
        if got != want:
            fails.append(f"{what}: got {got!r} want {want!r}")

    eq(check("Africa", "Africa"), True, "plain match")
    eq(check(" africa.", "Africa"), True, "case and punctuation")
    eq(check("Europe", "Africa"), False, "wrong answer")
    eq(check(None, "Africa"), False, "no output")
    eq(check("the united states of america", "United States"), True, "us special case")
    eq(check("australia", "Oceania"), True, "oceania special case")
    eq(check("anything at all", "Africa,"), True, "empty option matches (ported bug)")
    eq(degenerate("Africa,"), True, "degenerate flagged")
    eq(degenerate("Africa"), False, "non-degenerate")

    base = {"attribute": "Continent", "Continent": "Africa",
            "Country": "Ethiopia", "Language": "Amharic"}
    src = {"attribute": "Continent", "Continent": "Asia",
           "Country": "Taiwan", "Language": "Mandarin Chinese"}
    eq(expected_answer(base, src, "Continent"), "Asia", "moved variable carries")
    eq(expected_answer(base, src, "Country"), "Africa", "unmoved: answer unchanged")
    eq(expected_answer(base, src, "Language"), "Africa", "unmoved: answer unchanged")

    for f in fails:
        print("  FAIL", f)
    print(f"\nselftest: {'PASS' if not fails else str(len(fails)) + ' FAILED'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--split", default="val")
    ap.add_argument("--run", type=int, default=0,
                    help="score N pairs, batched")
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--probe", type=int, default=0,
                    help="run N pairs end to end through the model")
    ap.add_argument("--layer", type=int, default=5)
    ap.add_argument("--tokens", type=int, default=6,
                    help="greedy tokens generated per example")
    ap.add_argument("--target", default="Continent", choices=ATTRS)
    ap.add_argument("--kind", default="prompt_template_counterfactual",
                    choices=COUNTERFACTUALS)
    ap.add_argument("--local", action="store_true",
                    help="run against a local model instead of NDIF")
    ap.add_argument("--audit", action="store_true",
                    help="check the entity token index against the tokenizer")
    ap.add_argument("--model", default="meta-llama/Llama-3.1-8B")
    ap.add_argument("--summary", action="store_true",
                    help="build the pairs and describe them; no model is loaded")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    rows = load(args.split)
    print(f"{len(rows):,} rows in {args.split}\n")

    if args.run:
        import time
        from transformers import AutoTokenizer
        sys.path.insert(0, "src")
        from editreach.remote import connect
        tok = AutoTokenizer.from_pretrained(args.model)
        model = connect(args.model)
        ps, _ = pairs(rows, args.target, args.kind)
        ps = ps[:args.run]
        t0 = time.time()
        r = score_batch(model, tok, ps, args.layer, remote=not args.local,
                        tokens=args.tokens, batch=args.batch,
                        verbose=args.verbose)
        dt = time.time() - t0
        print(f"layer {args.layer}  target {args.target}  {args.kind}")
        print(f"  n            {r['n']:,}")
        print(f"  IIA          {r['iia']:.3f}")
        print(f"  unintervened {r['unintervened']:.3f}   "
              f"(the model's own accuracy on these, same decoding)")
        print(f"  batch        {r['batch']}   tokens {r['tokens']}   "
              f"(both change individual verdicts; see score_batch)")
        print(f"  wall         {dt:.1f}s   {dt / max(r['n'], 1):.2f}s per example")
        return 0

    if args.probe:
        from transformers import AutoTokenizer
        sys.path.insert(0, "src")
        from editreach.remote import connect
        tok = AutoTokenizer.from_pretrained(args.model)
        model = connect(args.model)
        ps, _ = pairs(rows, args.target, args.kind)
        moved = [p for p in ps if p["asked"] == args.target]
        held = [p for p in ps if p["asked"] != args.target]
        print(f"layer {args.layer}, target {args.target}, {args.kind}")
        print("showing both halves of the metric: pairs the question asks about "
              "the moved\nvariable, and pairs it does not.\n")
        for label, pool in (("MOVED", moved), ("HELD", held)):
            for p in pool[:args.probe]:
                r = probe_one(model, tok, p, args.layer, remote=not args.local,
                              tokens=args.tokens)
                mark = "ok " if r["correct"] else "NO "
                print(f"  {mark}[{label}] asks {r['asked']:<9} "
                      f"{r['base_entity']!r} <- {r['source_entity']!r}")
                print(f"      before {r['unintervened']!r}   after "
                      f"{r['intervened']!r}   expected {r['expected']!r}")
        return 0

    if args.audit:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(args.model)
        print(f"tokenizer: {args.model}\n")
        print(f"{'target':<11}{'counterfactual':<32}{'checked':>9}{'missing':>9}"
              f"{'ambiguous':>11}{'misaligned':>12}")
        bad = 0
        for target in ATTRS:
            for kind in COUNTERFACTUALS:
                ps, _ = pairs(rows, target, kind)
                a = audit_positions(tok, ps)
                bad += a["missing"] + a["misaligned"]
                print(f"{target:<11}{kind:<32}{a['checked']:>9,}{a['missing']:>9,}"
                      f"{a['ambiguous']:>11,}{a['misaligned']:>12,}")
                for e in a["examples"]:
                    print(f"            {e[0]!r} -> token {e[1]}")
        print("\n" + ("PASS - the index lands on the entity's last token."
                      if not bad else
                      "FAIL - do not run interventions until this is clean."))
        return 1 if bad else 0
    print(f"{'target':<11}{'counterfactual':<32}{'pairs':>8}{'moved':>8}"
          f"{'held':>8}{'degenerate':>12}{'no gold':>10}")
    for target in ATTRS:
        for kind in COUNTERFACTUALS:
            ps, dropped = pairs(rows, target, kind)
            moved = sum(1 for p in ps if p["asked"] == target)
            deg = sum(1 for p in ps if p["degenerate"])
            print(f"{target:<11}{kind:<32}{len(ps):>8,}{moved:>8,}"
                  f"{len(ps) - moved:>8,}{deg:>12,}{dropped['no_gold']:>10,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
