#!/usr/bin/env python3
"""C-012 - does the adapter's longest-candidate rule manufacture a published rate?

    python3 agents/engineer/workspace/run_c012_candidate_pool.py [--data PATH]

No model, no gradients, no network. It reads the three released RippleEdits
subsets and scores each of them three times.

WHAT IT ANSWERS. [C-011] found that 682 of 1,067 `Subject_Aliasing` strict hits
are circular: the adapter recovered the subject out of an aliasing prompt and
then reported that same prompt as naming the subject. §5.8 of the paper says
that inflates the strict rate and not the alias rate. That sentence was written
without the count. This is the count.

THE TWO RESTRICTIONS ARE DIFFERENT EXPERIMENTS, and running only one would
answer a question nobody asked. The adapter takes the LONGEST candidate as the
canonical subject and passes THE REST ON AS ALIASES, so:

  released - as shipped. Candidates from all six types.
  R1       - the canonical pick is restricted to the five non-aliasing types;
             every candidate is still passed on as an alias. This removes the
             circularity and nothing else, so R1 is what the published rates
             should be judged against.
  R2       - the whole pool is restricted. Aliasing prompts contribute nothing,
             canonical or alias, so this also discards genuine name variants
             that `Subject_Aliasing` exists to supply. A fall in R2's alias rate
             is the restriction working as designed, not evidence about the
             published numbers.

Predictions and branches: `results/C-012-predictions.md`, committed at 6786538
before this file was written.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent          # workspace -> engineer -> agents -> repo
RESULTS = ROOT / "results"
SUBSETS = ("recent", "random", "popular")
ALIASING = "Subject_Aliasing"

ORDER = ("Compositionality_I", "Relation_Specificity", "Forgetfulness",
         "Logical_Generalization", "Subject_Aliasing", "Compositionality_II")


def _sibling(name: str, *tail: str) -> pathlib.Path | None:
    """This repo is checked out twice; search for the sibling rather than assume."""
    roots = (ROOT.parent, pathlib.Path.home() / "code",
             pathlib.Path.home() / "code" / "open-concept-lab" / "ai")
    for root in roots:
        candidate = root.joinpath(name, *tail)
        if candidate.exists():
            return candidate
    return None


def _editscreen():
    try:
        import editscreen  # noqa: F401
    except ImportError:
        src = _sibling("editscreen", "src")
        if src is None:
            sys.exit("editscreen is not installed and no checkout was found")
        sys.path.insert(0, str(src))
    from editscreen import screen
    from editscreen.adapters import ripple
    from editscreen.types import Edit
    return screen, ripple, Edit


def _without_aliasing(ripple, entry: dict) -> dict:
    """A copy of the entry with its aliasing prompts blanked.

    Doctoring the entry and re-running the adapter's OWN candidate reader keeps
    one copy of the patterns. A second implementation here would drift from the
    released one and the comparison would stop being a comparison.
    """
    return {k: ([] if k == ALIASING else entry.get(k)) for k in ripple.CRITERIA}


def _edits(ripple, Edit, entry: dict) -> dict:
    """The three Edit objects this entry yields, one per variant. None where the
    variant cannot name a subject at all."""
    full = ripple.candidates(entry)
    narrow = ripple.candidates(_without_aliasing(ripple, entry))
    relation = (entry.get("edit") or {}).get("relation")

    def build(subject: str | None, pool: list[str]):
        if subject is None:
            return None
        return Edit(subject=subject, relation=relation, object_new=None,
                    aliases=tuple(c for c in pool if c != subject))

    longest = (lambda c: max(c, key=len) if c else None)
    return {
        "released": build(longest(full), full),
        # R1: canonical from the narrow pool, aliases from the full one.
        "R1": build(longest(narrow), full),
        "R2": build(longest(narrow), narrow),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=None,
                    help="RippleEdits release directory (default: found beside this repo)")
    args = ap.parse_args()
    data = (pathlib.Path(args.data) if args.data
            else _sibling("edit-slice", "data", "ripple"))
    if data is None:
        print("no RippleEdits release found - pass --data")
        return 1
    print(f"data: {data}\n")
    screen, ripple, Edit = _editscreen()

    out: dict = {"card": "C-012", "subsets": {}}

    for subset in SUBSETS:
        path = data / f"{subset}.json"
        if not path.exists():
            print(f"missing {path} - fetch the RippleEdits release first")
            return 1
        records = json.loads(path.read_text(encoding="utf-8"))

        tot = {v: collections.Counter() for v in ("released", "R1", "R2")}
        per = {v: collections.defaultdict(collections.Counter)
               for v in ("released", "R1", "R2")}
        covered = collections.Counter()
        relabelled = 0

        for entry in records:
            edits = _edits(ripple, Edit, entry)
            if edits["released"] is not None and edits["R1"] is not None:
                if edits["released"].subject != edits["R1"].subject:
                    relabelled += 1
            prompts = [(crit, q["prompt"])
                       for crit in ripple.CRITERIA
                       for g in (entry.get(crit) or [])
                       for q in ((g or {}).get("test_queries") or [])
                       if isinstance((q or {}).get("prompt"), str)
                       and q["prompt"].strip()]
            for variant, edit in edits.items():
                if edit is None:
                    continue
                covered[variant] += 1
                for crit, prompt in prompts:
                    level = screen(edit, prompt).level.name
                    tot[variant]["prompts"] += 1
                    tot[variant]["strict"] += level == "STRICT"
                    tot[variant]["strict_or_alias"] += level in ("STRICT", "ALIAS")
                    per[variant][crit]["n"] += 1
                    per[variant][crit]["strict"] += level == "STRICT"

        entries = len(records)
        out["subsets"][subset] = {
            "entries": entries,
            "relabelled_by_R1": relabelled,
            "variants": {
                v: {
                    "entries_covered": covered[v],
                    "coverage": covered[v] / entries,
                    "prompts": tot[v]["prompts"],
                    "strict": tot[v]["strict"] / tot[v]["prompts"] if tot[v]["prompts"] else None,
                    "strict_or_alias": (tot[v]["strict_or_alias"] / tot[v]["prompts"]
                                        if tot[v]["prompts"] else None),
                    "by_type": {c: {"n": per[v][c]["n"],
                                    "strict": (per[v][c]["strict"] / per[v][c]["n"]
                                               if per[v][c]["n"] else None)}
                                for c in ORDER},
                } for v in ("released", "R1", "R2")
            },
        }

        s = out["subsets"][subset]["variants"]
        print(f"=== {subset} — {entries:,} entries, "
              f"{relabelled:,} entries relabelled by R1")
        print(f"{'':10}{'covered':>9}{'prompts':>10}{'strict':>9}{'+variants':>11}")
        for v in ("released", "R1", "R2"):
            print(f"{v:10}{s[v]['coverage']:>8.1%}{s[v]['prompts']:>10,}"
                  f"{s[v]['strict']:>9.3f}{s[v]['strict_or_alias']:>11.3f}")
        print(f"\n{'test type':<24}{'released':>10}{'R1':>10}{'R2':>10}")
        for c in ORDER:
            row = [s[v]["by_type"][c]["strict"] for v in ("released", "R1", "R2")]
            print(f"{c:<24}" + "".join(
                f"{r:>10.3f}" if r is not None else f"{'—':>10}" for r in row))
        print()

    dest = RESULTS / "C-012-candidate-pool.json"
    dest.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"written: {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
