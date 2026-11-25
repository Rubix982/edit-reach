#!/usr/bin/env python3
"""C-009: MIB's two RAVEL filters, ported.

MIB does not score the released rows. It scores what survives two filters, applied
in this order, and the denominator they leave is what Table 3g's numbers are over.
Until both exist here, no number from `ravel_iia.py` is comparable to 53 / 47 / 47
and [T-018] cannot be attempted.

    1. CORRECTNESS - CausalAbstraction/experiments/filter_experiment.py, at the
       commit MIB pins (f9ed6777). Keep a pair only if the model, unintervened,
       answers BOTH the base prompt and the counterfactual prompt the way the
       causal model says it should.

    2. ATTRIBUTE BALANCE - `get_filtered_indices` in
       MIB-causal-variable-track/baselines/ravel_baselines.py. Bucket what
       survived by the attribute the BASE prompt asks. Keep every row of the
       target attribute, and half that many of each other attribute.

THREE THINGS THE PORT KEEPS THAT A REIMPLEMENTATION WOULD QUIETLY FIX.

**The correctness filter is a conjunction over both arms, not an accuracy
threshold on the base.** Our own note for this card said it "filters to what the
model answers correctly unintervened", which reads as one condition on one prompt.
It is two conditions, and a pair dies if either fails. That matters to the size of
the denominator: base accuracy alone is 0.69, so if the two arms were independent
the joint keep rate would be nearer 0.48. Which it actually is, is measured by
`report()` below rather than assumed.

**`half` in MIB's code is not half of anything.** It is bound to
`len(attr_to_indices[target_variable])`, the FULL count of the target attribute,
and it is the non-target attributes that are then cut to `half // 2`. The name
says the opposite of what the line does. Ported as written, with their name kept
so the two files can be read side by side.

**The wikipedia counterfactual passes the correctness filter unconditionally.**
Its causal-model answer is the empty string, and `check()` splits the expected
value on commas and asks whether any part is a substring of the output - and the
empty string is a substring of everything. So for that counterfactual type, the
second arm of the filter is vacuous and only the base is really tested. This is
the same empty-option hole `ravel_iia.check()` already documents, reached from a
different direction. It is their behaviour, so it is reproduced, and
`report()` prints the two arms separately so it cannot hide.
"""
from __future__ import annotations

import argparse
import random
import sys
import time

from ravel_iia import ATTRS, COUNTERFACTUALS, check, load, pairs


def source_gold(source: dict) -> str:
    """What the counterfactual prompt should answer on its own, unintervened.

    The source row carries the attribute it asks. For a wikipedia passage that
    attribute is "wikipedia", for which the causal model's `get_answer` returns
    the empty string - see the module docstring on why that makes this arm
    vacuous rather than merely lenient.
    """
    a = source.get("attribute")
    if a not in ATTRS:
        return ""
    v = source.get(a)
    return v if isinstance(v, str) else ""


def generate_clean(model, tokenizer, prompts: list[str], *, remote: bool,
                   max_new_tokens: int = 6) -> list[str]:
    """Greedy continuations with no intervention of any kind.

    `ravel_iia.generate_batched` cannot serve here. Its unintervened arm still
    writes a vector into the residual stream - deliberately, so that a difference
    between its two columns is the intervention and not the decoding ([T-020]).
    The filter needs the model's own answer, so this traces without touching the
    stream at all. The argmax is taken remotely for the reason `remote.py` gives.
    """
    import torch
    texts = list(prompts)
    done = [False] * len(prompts)
    for _ in range(max_new_tokens):
        with torch.no_grad(), model.trace(texts, remote=remote):
            nxt = model.lm_head.output[:, -1, :].argmax(dim=-1).save()
        for n, t in enumerate(nxt.tolist()):
            if done[n]:
                continue
            piece = tokenizer.decode(t)
            if not piece:
                done[n] = True
                continue
            texts[n] += piece
    return [t[len(p):] for t, p in zip(texts, prompts)]


def answer_cache(model, tokenizer, prompts: list[str], *, remote: bool,
                 batch: int = 32, tokens: int = 6,
                 verbose: bool = False) -> dict[str, str]:
    """Unintervened continuation for each DISTINCT prompt, keyed by the prompt.

    Correctness of the base arm depends on the base row alone and correctness of
    the source arm on the source row alone - neither depends on the target
    variable, and the same base row is reused across all three targets. So the
    generations are cached per prompt string rather than per pair, which is what
    makes filtering all three targets affordable rather than three times the cost.
    """
    uniq = sorted({p for p in prompts})
    out: dict[str, str] = {}
    for i in range(0, len(uniq), batch):
        chunk = uniq[i:i + batch]
        for p, g in zip(chunk, generate_clean(model, tokenizer, chunk,
                                              remote=remote,
                                              max_new_tokens=tokens)):
            out[p] = g
        if verbose:
            print(f"  generated {min(i + batch, len(uniq)):,}/{len(uniq):,}",
                  flush=True)
    return out


def correctness_filter(ps: list[dict], answers: dict[str, str]) -> tuple[list[dict], dict]:
    """FilterExperiment.filter, over pairs we have already generated for.

    Returns the survivors and a per-arm tally, so the base arm and the
    counterfactual arm can be read separately.
    """
    kept, tally = [], {"n": len(ps), "base_ok": 0, "source_ok": 0, "both_ok": 0}
    for p in ps:
        b = check(answers.get(p["base_prompt"]), p["base_gold"])
        s = check(answers.get(p["source_prompt"]), p["source_gold"])
        tally["base_ok"] += b
        tally["source_ok"] += s
        if b and s:
            tally["both_ok"] += 1
            kept.append(p)
    return kept, tally


def balance(ps: list[dict], target: str, rng: random.Random) -> list[dict]:
    """`get_filtered_indices`, ported with its own variable name kept.

    Buckets on the attribute the BASE prompt asks - which is always one of the
    three, even in the wikipedia family, where only the counterfactual is a
    wikipedia passage.
    """
    attr_to_indices: dict[str, list[int]] = {a: [] for a in ATTRS}
    for i, p in enumerate(ps):
        if p["asked"] in attr_to_indices:
            attr_to_indices[p["asked"]].append(i)

    # MIB's loop drops anything outside the three attributes without saying so.
    # Here that must never happen - `pairs()` already refuses a row whose asked
    # attribute is not one of the three - so a shortfall means an upstream bug
    # rather than a filtering decision, and it is loud instead of silent.
    #
    # It has not fired, and the thing that looked like it should have was a
    # reading error worth recording. The first run reported 189 survivors for
    # all three targets of one counterfactual type, while the balanced sizes
    # 96 / 145 / 133 invert to 48 + 73 + 67 = 188. That is not an off-by-one:
    # THE THREE TARGETS DO NOT SHARE A SURVIVOR POOL. `pairs()` drops a row
    # whose gold for the target variable is null, and which rows those are
    # depends on the target - Continent loses 7 and the other two lose none -
    # so each target's window of N pairs is a slightly different set, with its
    # own composition ({62, 118, 120} against {63, 117, 120}). Inverting the
    # balanced totals as though one pool produced all three is what makes a
    # phantom missing row appear.
    binned = sum(len(v) for v in attr_to_indices.values())
    if binned != len(ps):
        missing = [p["asked"] for p in ps if p["asked"] not in attr_to_indices]
        raise ValueError(
            f"balance() binned {binned} of {len(ps)} pairs; "
            f"{len(missing)} fell outside {ATTRS}: {sorted(set(missing))}")

    half = len(attr_to_indices[target])          # MIB's name; it is the full count
    for a in ATTRS:
        rng.shuffle(attr_to_indices[a])

    final_indices: list[int] = []
    for a in ATTRS:
        if a == target:
            final_indices.extend(attr_to_indices[a][:half])
        else:
            final_indices.extend(attr_to_indices[a][:int(half // 2)])

    rng.shuffle(final_indices)
    return [ps[i] for i in final_indices]


def build(rows: list[dict], target: str, kind: str) -> tuple[list[dict], dict]:
    """Pairs for one target and counterfactual type, carrying both gold answers.

    `ravel_iia.pairs` carries `expected`, which is the post-intervention gold.
    The filter needs the two UNINTERVENED golds instead, which are different
    quantities, so they are attached here rather than conflated with it.
    """
    ps, dropped = pairs(rows, target, kind)
    out = []
    for p in ps:
        base = rows[p["row"]]
        g = base.get(p["asked"])
        if not isinstance(g, str) or not g.strip():
            dropped["no_gold"] += 1
            continue
        src = (base.get(p["kind"]) or {})
        out.append({**p, "base_gold": g, "source_gold": source_gold(src)})
    return out, dropped


def report(model, tokenizer, rows: list[dict], *, kinds, targets, remote: bool,
           batch: int, tokens: int, limit: int, seed: int,
           verbose: bool) -> dict:
    """Keep rates for every target x counterfactual cell, both filters."""
    rng = random.Random(seed)
    built = {}
    prompts: set[str] = set()
    for kind in kinds:
        for target in targets:
            ps, dropped = build(rows, target, kind)
            if limit:
                ps = ps[:limit]
            built[(kind, target)] = (ps, dropped)
            for p in ps:
                prompts.add(p["base_prompt"])
                prompts.add(p["source_prompt"])

    print(f"{len(prompts):,} distinct prompts to generate "
          f"(batch {batch}, {tokens} tokens)", flush=True)
    t0 = time.time()
    answers = answer_cache(model, tokenizer, sorted(prompts), remote=remote,
                           batch=batch, tokens=tokens, verbose=verbose)
    print(f"generation took {time.time() - t0:.1f}s\n", flush=True)

    out = {"batch": batch, "tokens": tokens, "seed": seed, "cells": []}
    for (kind, target), (ps, dropped) in built.items():
        kept, tally = correctness_filter(ps, answers)
        final = balance(kept, target, rng)
        import collections
        out["cells"].append({
            "kind": kind, "target": target, "built": len(ps),
            "base_ok": tally["base_ok"], "source_ok": tally["source_ok"],
            "after_correctness": len(kept), "after_balance": len(final),
            # Recorded, not inferred. The balanced total alone does not pin the
            # composition down, and reading it back out of the total is how the
            # off-by-one above stayed invisible for a run.
            "survivors_by_attribute": dict(
                collections.Counter(p["asked"] for p in kept)),
            "balanced_by_attribute": dict(
                collections.Counter(p["asked"] for p in final)),
            "dropped": dropped,
        })
    return out


def selftest() -> int:
    """Checks the two ports do what MIB's code does, with no model loaded."""
    fails = []

    def ok(cond, msg):
        if not cond:
            fails.append(msg)

    # --- the empty-option hole, which is what makes the wikipedia arm vacuous
    ok(check("anything at all", ""), "empty expected should match anything")
    ok(source_gold({"attribute": "wikipedia"}) == "",
       "a wikipedia source should have the empty gold")
    ok(source_gold({"attribute": "Country", "Country": "France"}) == "France",
       "an attribute source should have its own value as gold")

    # --- balance: target keeps all, the other two keep half the target's count
    def synth(counts):
        out = []
        for a, n in counts.items():
            out += [{"asked": a, "i": f"{a}{k}"} for k in range(n)]
        return out

    import collections
    ps = synth({"Continent": 100, "Country": 80, "Language": 60})
    got = collections.Counter(p["asked"]
                              for p in balance(ps, "Continent", random.Random(0)))
    ok(got == {"Continent": 100, "Country": 50, "Language": 50},
       f"balance on Continent gave {dict(got)}")
    got = collections.Counter(p["asked"]
                              for p in balance(ps, "Language", random.Random(0)))
    ok(got == {"Language": 60, "Continent": 30, "Country": 30},
       f"balance on Language gave {dict(got)}")

    # a target scarcer than half of another attribute still caps the others at
    # half ITS count, which is the asymmetry the misleading name hides
    ps = synth({"Continent": 10, "Country": 400, "Language": 400})
    got = collections.Counter(p["asked"]
                              for p in balance(ps, "Continent", random.Random(0)))
    ok(got == {"Continent": 10, "Country": 5, "Language": 5},
       f"balance on a scarce target gave {dict(got)}")

    # --- correctness: a conjunction, so one bad arm kills the pair
    ps = [
        {"base_prompt": "b1", "source_prompt": "s1",
         "base_gold": "France", "source_gold": "Japan"},     # both right
        {"base_prompt": "b2", "source_prompt": "s2",
         "base_gold": "France", "source_gold": "Japan"},     # source wrong
        {"base_prompt": "b3", "source_prompt": "s3",
         "base_gold": "France", "source_gold": "Japan"},     # base wrong
    ]
    answers = {"b1": " France", "s1": " Japan",
               "b2": " France", "s2": " Peru",
               "b3": " Chad", "s3": " Japan"}
    kept, tally = correctness_filter(ps, answers)
    ok(len(kept) == 1, f"only the all-correct pair should survive, got {len(kept)}")
    ok(tally == {"n": 3, "base_ok": 2, "source_ok": 2, "both_ok": 1},
       f"per-arm tally wrong: {tally}")

    # a prompt with no generation is a miss, never a silent pass
    kept, _ = correctness_filter(ps[:1], {})
    ok(kept == [], "a missing generation must not count as correct")

    # --- build() must attach each pair's OWN row's gold, even when two rows
    # share a base prompt. This is the bug that scored the source arm at 0.31:
    # the source row was recovered by looking the base prompt up in a dict, and
    # 10,389 of the 15,950 val rows share a prompt with another row, so most
    # pairs were scored against a different city's answer.
    shared = '[{"city": "Beijing", "continent": "Asia"}, {"city": "Pinsk", "continent": "'
    rows = [
        {"prompt": shared, "entity": "Pinsk", "attribute": "Continent",
         "Continent": "Europe", "Country": "Belarus", "Language": "Belarusian",
         "attribute_counterfactual": {
             "prompt": "People in Lima speak", "entity": "Lima",
             "attribute": "Language", "Continent": "South America",
             "Country": "Peru", "Language": "Spanish"}},
        {"prompt": shared, "entity": "Pinsk", "attribute": "Continent",
         "Continent": "Europe", "Country": "Belarus", "Language": "Belarusian",
         "attribute_counterfactual": {
             "prompt": "Cairo is in", "entity": "Cairo",
             "attribute": "Country", "Continent": "Africa",
             "Country": "Egypt", "Language": "Arabic"}},
    ]
    built, _ = build(rows, "Continent", "attribute_counterfactual")
    ok(len(built) == 2, f"both rows should build, got {len(built)}")
    if len(built) == 2:
        ok([b["source_gold"] for b in built] == ["Spanish", "Egypt"],
           "each row must get ITS OWN source gold, not the other row's: "
           f"got {[b['source_gold'] for b in built]}")
        ok(all(b["base_gold"] == "Europe" for b in built),
           "base gold should be the asked attribute of the row itself")

    for f in fails:
        print("FAIL", f)
    print(f"\nselftest: {'PASS' if not fails else str(len(fails)) + ' FAILED'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="val")
    ap.add_argument("--limit", type=int, default=300,
                    help="pairs built per cell before filtering; 0 for all")
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--tokens", type=int, default=6)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--target", default="all")
    ap.add_argument("--kind", default="attribute_counterfactual")
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--model", default="meta-llama/Llama-3.1-8B")
    ap.add_argument("--out", default="")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry", action="store_true",
                    help="build and count pairs; no model is loaded")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    targets = list(ATTRS) if args.target == "all" else [args.target]
    kinds = list(COUNTERFACTUALS) if args.kind == "all" else [args.kind]
    rows = load(args.split)
    print(f"{len(rows):,} rows in {args.split}\n")

    if args.dry:
        for kind in kinds:
            for target in targets:
                ps, dropped = build(rows, target, kind)
                n = len(ps[:args.limit] if args.limit else ps)
                print(f"{kind:<32}{target:<11}{n:>7} pairs   dropped {dropped}")
        return 0

    from transformers import AutoTokenizer
    sys.path.insert(0, "src")
    from editreach.remote import connect
    tok = AutoTokenizer.from_pretrained(args.model)
    model = connect(args.model)

    r = report(model, tok, rows, kinds=kinds, targets=targets,
               remote=not args.local, batch=args.batch, tokens=args.tokens,
               limit=args.limit, seed=args.seed, verbose=args.verbose)

    print(f"{'counterfactual':<32}{'target':<11}{'built':>7}{'base':>7}"
          f"{'src':>7}{'both':>7}{'final':>7}")
    for c in r["cells"]:
        print(f"{c['kind']:<32}{c['target']:<11}{c['built']:>7}"
              f"{c['base_ok']:>7}{c['source_ok']:>7}"
              f"{c['after_correctness']:>7}{c['after_balance']:>7}")

    if args.out:
        import json
        with open(args.out, "w") as f:
            json.dump(r, f, indent=2)
        print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
