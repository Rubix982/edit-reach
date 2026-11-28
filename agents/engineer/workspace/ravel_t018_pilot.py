"""[T-018] cost pilot: one filtered, balanced cell scored at one layer, timed.

Joins the two halves that already exist and have never been run together --
`ravel_filter` (MIB's two filters) and `ravel_iia.score_batch` (the batched
interchange intervention) -- and reports what a full reproduction would cost.

It does NOT reproduce anything. Table 3g is a mean over three counterfactual
types and all 32 layers, so a reproduction is 3 targets x 3 kinds x 32 layers =
288 cells. This times one and extrapolates, so that the decision to spend the
rest is taken against a measured number rather than the 83-hour estimate in
CARD.md, which predates batching.

    python agents/engineer/workspace/ravel_t018_pilot.py --limit 300

Filtering is LAYER-INDEPENDENT -- it reads unintervened generations only -- so
its cost is paid once per (target, kind), not once per cell. The extrapolation
below splits the two.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ravel_filter import answer_cache, balance, build, correctness_filter  # noqa: E402
from ravel_iia import ATTRS, load, score_batch  # noqa: E402

from editreach.remote import connect, uses_remote  # noqa: E402

KINDS = ("prompt_template_counterfactual", "attribute_counterfactual",
         "wikipedia_counterfactual")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="meta-llama/Llama-3.1-8B")
    ap.add_argument("--target", default="Continent", choices=ATTRS)
    ap.add_argument("--kind", default="prompt_template_counterfactual", choices=KINDS)
    ap.add_argument("--layer", type=int, default=5)
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--batch", type=int, default=120)
    ap.add_argument("--tokens", type=int, default=6)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    model = connect(a.model, backend="local" if a.local else "ndif")
    remote = uses_remote(model)
    tok = model.tokenizer
    rows = load("val")

    ps, dropped = build(rows, a.target, a.kind)
    ps = ps[: a.limit]
    print(f"{a.kind}/{a.target} layer {a.layer}: {len(ps)} pairs built, dropped {dropped}")

    t0 = time.time()
    prompts = [p["base_prompt"] for p in ps] + [p["source_prompt"] for p in ps]
    answers = answer_cache(model, tok, prompts, remote=remote,
                           batch=a.batch, tokens=a.tokens)
    kept, tally = correctness_filter(ps, answers)
    t_filter = time.time() - t0
    print(f"  filter   {t_filter:7.1f}s  -> {tally}")

    bal = balance(kept, a.target, random.Random(a.seed))
    print(f"  balanced -> {len(bal)} pairs")

    t1 = time.time()
    res = score_batch(model, tok, bal, a.layer, remote=remote,
                      tokens=a.tokens, batch=a.batch)
    t_score = time.time() - t1
    print(f"  score    {t_score:7.1f}s  -> {res}")

    # Filtering is paid once per (target, kind); scoring once per cell.
    n_tk, n_cells = len(ATTRS) * len(KINDS), len(ATTRS) * len(KINDS) * 32
    total = t_filter * n_tk + t_score * n_cells
    print(f"\nEXTRAPOLATION to a full Table 3g reproduction")
    print(f"  filter  {n_tk:3} x {t_filter:6.1f}s = {t_filter * n_tk / 60:7.1f} min")
    print(f"  score   {n_cells:3} x {t_score:6.1f}s = {t_score * n_cells / 3600:7.2f} h")
    print(f"  TOTAL                   {total / 3600:7.2f} h")
    print(f"\n  n per cell here is {len(bal)}, against MIB's 10,000 per attribute.")

    if a.out:
        Path(a.out).write_text(json.dumps({
            "target": a.target, "kind": a.kind, "layer": a.layer,
            "built": len(ps), "tally": tally, "balanced": len(bal),
            "result": res, "seconds": {"filter": t_filter, "score": t_score},
            "extrapolated_hours": total / 3600,
            "batch": a.batch, "tokens": a.tokens, "model": a.model,
        }, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
