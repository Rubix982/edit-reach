#!/usr/bin/env python3
"""C-011 - the screen's verdict on each of RippleEdits' six declared test types.

    python3 agents/engineer/workspace/run_c011_test_types.py [--data PATH]

Runs the whole card. No model, no gradients, no network: it reads the three
released RippleEdits subsets and the `editscreen` adapter, and counts.

WHAT IT ANSWERS. [T-016] recorded two per-type numbers nobody had explained -
`Compositionality_II` at essentially zero and `Subject_Aliasing` low on the
strict rule. Either the benchmark is doing what its own definitions say, or the
adapter is recovering a string that does not belong in that type's prompts. The
predictions were written down from the benchmark's paper and committed before
any count here was read; see `C-011-predictions.md`.

THE THIRD TABLE IS THE ONE THAT PAYS. The adapter takes the longest candidate
across ALL six types, so when an entry's longest string is an alias lifted out
of an aliasing prompt, the screen reports that same prompt as naming the
subject - it read the name out of the prompt and then found it there. That is
circular, and `aliasing_circularity` counts how often.
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

# This repo is checked out twice - standalone at ~/code/edit-reach and as a
# submodule under open-concept-lab/ai/ - and the sibling it needs sits in a
# different place in each. Search rather than assume, and say which was used.
def _sibling(name: str, *tail: str) -> pathlib.Path | None:
    roots = (ROOT.parent, pathlib.Path.home() / "code",
             pathlib.Path.home() / "code" / "open-concept-lab" / "ai")
    for root in roots:
        candidate = root.joinpath(name, *tail)
        if candidate.exists():
            return candidate
    return None

# Ordered by what the definitions predict, not alphabetically: the three types
# whose queries are about the edited subject, then the mixed one, then the two
# that name something else. Reading the table top to bottom is the result.
ORDER = ("Compositionality_I", "Relation_Specificity", "Forgetfulness",
         "Logical_Generalization", "Subject_Aliasing", "Compositionality_II")


def _editscreen():
    """Import editscreen, from a sibling checkout if it is not installed."""
    try:
        import editscreen  # noqa: F401
    except ImportError:
        src = _sibling("editscreen", "src")
        if src is None:
            sys.exit("editscreen is not installed and no checkout was found")
        sys.path.insert(0, str(src))
    from editscreen import screen
    from editscreen.adapters import ripple
    return screen, ripple


def _alias_only_label(ripple, entry: dict) -> bool:
    """Did the recovered label come ONLY from this entry's aliasing prompts?

    Built by running the adapter's own candidate reader twice over doctored
    copies of the entry - once with every criterion but `Subject_Aliasing`
    blanked, once with only it blanked - so the split uses the adapter's
    patterns rather than a second copy of them that could drift.
    """
    label = ripple.subject_label(entry)
    if label is None:
        return False
    only_alias = {k: ([] if k != "Subject_Aliasing" else entry.get(k))
                  for k in ripple.CRITERIA}
    except_alias = {k: ([] if k == "Subject_Aliasing" else entry.get(k))
                    for k in ripple.CRITERIA}
    return (label in set(ripple.candidates(only_alias))
            and label not in set(ripple.candidates(except_alias)))


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
    screen, ripple = _editscreen()

    by_type: dict = {}
    totals: dict = {}
    circular: dict = {}

    for subset in SUBSETS:
        path = data / f"{subset}.json"
        if not path.exists():
            print(f"missing {path} - fetch the RippleEdits release first")
            return 1
        records = json.loads(path.read_text(encoding="utf-8"))
        coverage = ripple.coverage(path)
        per = collections.defaultdict(collections.Counter)
        tot = collections.Counter()
        circ = collections.Counter()

        for entry in records:
            if ripple.subject_label(entry) is None:
                continue
            from_alias = _alias_only_label(ripple, entry)
            for item in ripple.from_records([entry]):
                level = screen(item.edits[0], item.probe).level.name
                per[item.test_type][level] += 1
                per[item.test_type]["n"] += 1
                tot["prompts"] += 1
                tot["strict"] += level == "STRICT"
                tot["strict_or_alias"] += level in ("STRICT", "ALIAS")
                if item.test_type == "Subject_Aliasing" and level == "STRICT":
                    circ["circular" if from_alias else "independent"] += 1

        by_type[subset] = {k: dict(v) for k, v in per.items()}
        totals[subset] = {
            "entries": coverage["entries"],
            "subject_recovered": coverage["subject_recovered"],
            "coverage": coverage["rate"],
            # The denominator of every headline rate. It is PROMPTS of
            # recoverable entries, not entries - §5.8 of the paper page said
            # entries until this card, and the column was wrong.
            "prompts": tot["prompts"],
            "strict": tot["strict"],
            "rate_strict": round(tot["strict"] / tot["prompts"], 4),
            "rate_strict_or_alias": round(tot["strict_or_alias"] / tot["prompts"], 4),
        }
        circular[subset] = dict(circ)

    print(f"{'test type':<24}{'subset':<9}{'n':>8}{'strict':>9}{'+alias':>9}")
    for test_type in ORDER:
        for subset in SUBSETS:
            c = by_type[subset].get(test_type)
            if not c:
                continue
            n, s, a = c["n"], c.get("STRICT", 0), c.get("ALIAS", 0)
            print(f"{test_type:<24}{subset:<9}{n:>8,}{s / n:>9.3f}{(s + a) / n:>9.3f}")
        print()

    print(f"{'subset':<9}{'entries':>9}{'recovered':>11}{'prompts':>9}"
          f"{'strict':>9}{'+alias':>9}")
    for subset in SUBSETS:
        t = totals[subset]
        print(f"{subset:<9}{t['entries']:>9,}{t['subject_recovered']:>11,}"
              f"{t['prompts']:>9,}{t['rate_strict']:>9.4f}{t['rate_strict_or_alias']:>9.4f}")

    print("\nSubject_Aliasing strict hits, by where the recovered label came from")
    for subset in SUBSETS:
        c = circular[subset]
        hit = c.get("circular", 0) + c.get("independent", 0)
        share = f"{c.get('circular', 0) / hit:.0%}" if hit else "-"
        print(f"  {subset:<9}{hit:>6,} hits   {c.get('circular', 0):>5,} circular ({share})"
              f"   {c.get('independent', 0):>5,} independent")

    (RESULTS / "C-011-ripple-by-test-type.json").write_text(
        json.dumps(by_type, indent=1), encoding="utf-8")
    (RESULTS / "C-011-denominators.json").write_text(
        json.dumps({"totals": totals, "aliasing_circularity": circular}, indent=1),
        encoding="utf-8")
    print("\nwritten: C-011-ripple-by-test-type.json  C-011-denominators.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
