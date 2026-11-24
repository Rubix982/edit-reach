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
    for r in rows:
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
        out.append({"base_prompt": r["prompt"], "base_entity": r["entity"],
                    "asked": r["attribute"], "source_prompt": s["prompt"],
                    "source_entity": s["entity"], "target": target,
                    "expected": want, "degenerate": degenerate(want),
                    "kind": kind})
    return out, dropped


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
    ap.add_argument("--summary", action="store_true",
                    help="build the pairs and describe them; no model is loaded")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    rows = load(args.split)
    print(f"{len(rows):,} rows in {args.split}\n")
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
