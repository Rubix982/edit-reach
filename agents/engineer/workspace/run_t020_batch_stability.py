#!/usr/bin/env python3
"""T-020 - does batch size move the aggregate, or only individual verdicts?

    python3 agents/engineer/workspace/run_t020_batch_stability.py

One fixed set of pairs, scored at three batch sizes, nothing else varying.
Predictions in `results/T-020-predictions.md`, committed at afb3a4a before this
file was written.

WHY IT HAS TO BE RUN. Batching is not an optimisation for [C-009]; a remote
trace costs 2.39s median against ~0.4s of server-side execution, so without it
the card cannot run at any useful size. But a source vector read alone and
inside a batch of six differs by up to 0.0078 - bfloat16 granularity, not
misalignment - and that was enough to flip one example near a decision
boundary. If the aggregate moves too, batch size is an experimental variable
rather than a configuration detail, and every number the card produces has to
name it.

The per-example disagreement is counted as well as the aggregate, because the
two can come apart: symmetric flips leave the mean alone and are the expected
result, while a one-directional shift means the cause is not arithmetic noise
and the runner is wrong somewhere.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))

import ravel_iia as R  # noqa: E402

N = 240
BATCHES = (16, 48, 120)
LAYER = 5
TOKENS = 6
TARGET = "Continent"
KIND = "prompt_template_counterfactual"
MODEL = "meta-llama/Llama-3.1-8B"


def score_with_verdicts(model, tok, ps, batch):
    """IIA plus the per-example verdicts, so disagreement can be counted."""
    verdicts, before_v = [], []
    for start in range(0, len(ps), batch):
        chunk = ps[start:start + batch]
        bp = [c["base_prompt"] for c in chunk]
        sp = [c["source_prompt"] for c in chunk]
        bi = [R.entity_last_token(tok, c["base_prompt"], c["base_entity"])
              for c in chunk]
        si = [R.entity_last_token(tok, c["source_prompt"], c["source_entity"])
              for c in chunk]
        bpos, _, _ = R.batch_positions(tok, bp, bi)
        spos, _, _ = R.batch_positions(tok, sp, si)
        own = R.read_vectors(model, bp, bpos, LAYER, remote=True)
        src = R.read_vectors(model, sp, spos, LAYER, remote=True)
        b4 = R.generate_batched(model, tok, bp, bi, LAYER, own,
                                remote=True, max_new_tokens=TOKENS)
        af = R.generate_batched(model, tok, bp, bi, LAYER, src,
                                remote=True, max_new_tokens=TOKENS)
        for c, x, y in zip(chunk, b4, af):
            before_v.append(R.check(x, c["expected"]))
            verdicts.append(R.check(y, c["expected"]))
    return verdicts, before_v


def main() -> int:
    from transformers import AutoTokenizer
    from editreach.remote import connect

    rows = R.load("val")
    ps, _ = R.pairs(rows, TARGET, KIND)
    ps = ps[:N]
    print(f"{len(ps)} pairs, layer {LAYER}, {TOKENS} tokens, "
          f"target {TARGET}, {KIND}\n")

    tok = AutoTokenizer.from_pretrained(MODEL)
    model = connect(MODEL)

    runs = {}
    for b in BATCHES:
        t0 = time.time()
        v, bv = score_with_verdicts(model, tok, ps, b)
        dt = time.time() - t0
        runs[b] = {"verdicts": v, "before": bv,
                   "iia": sum(v) / len(v), "unintervened": sum(bv) / len(bv),
                   "seconds": round(dt, 1)}
        print(f"  batch {b:>4}   IIA {runs[b]['iia']:.4f}   "
              f"unintervened {runs[b]['unintervened']:.4f}   {dt:.0f}s")

    iias = [runs[b]["iia"] for b in BATCHES]
    spread = (max(iias) - min(iias)) * 100
    half = 1.96 * (0.25 / len(ps)) ** 0.5 * 100

    print(f"\naggregate spread  {spread:.2f} points")
    print(f"sampling 95% half-width at n={len(ps)}  {half:.2f} points")
    print(f"prediction 1 {'HOLDS' if spread <= half else 'FAILS'}")

    print("\nper-example disagreement between batch sizes")
    pairs_seen = []
    for i, a in enumerate(BATCHES):
        for b in BATCHES[i + 1:]:
            va, vb = runs[a]["verdicts"], runs[b]["verdicts"]
            diff = [n for n, (x, y) in enumerate(zip(va, vb)) if x != y]
            up = sum(1 for n in diff if vb[n] and not va[n])
            print(f"  {a:>4} vs {b:<4}  {len(diff):>3} of {len(va)} "
                  f"({100 * len(diff) / len(va):.1f}%)   "
                  f"{up} became correct, {len(diff) - up} became wrong")
            pairs_seen.append({"a": a, "b": b, "n_diff": len(diff),
                               "became_correct": up,
                               "became_wrong": len(diff) - up})

    out = {"thread": "T-020", "n": len(ps), "layer": LAYER, "tokens": TOKENS,
           "target": TARGET, "kind": KIND, "model": MODEL,
           "batches": list(BATCHES),
           "iia": {str(b): runs[b]["iia"] for b in BATCHES},
           "unintervened": {str(b): runs[b]["unintervened"] for b in BATCHES},
           "seconds": {str(b): runs[b]["seconds"] for b in BATCHES},
           "spread_points": round(spread, 3),
           "sampling_half_width_points": round(half, 3),
           "disagreement": pairs_seen}
    dest = ROOT / "results" / "T-020-batch-stability.json"
    dest.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nwritten: {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
