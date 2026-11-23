"""E-048 · How often does a MQuAKE question name a subject the case edited?

    .venv/bin/python agents/engineer/workspace/run_e048_mquake_exposure.py

Nothing is edited, no model is loaded, and no gradient is taken. This reads
two things out of the released files — the edited subjects, and the question —
and asks whether the second contains the first. It therefore runs on a laptop
in seconds and is unaffected by [E-043]/[E-047].

WHY IT WAS RUN. [E-038] found, on RippleEdits, that the items naming the edited
subject are the items where the edit sits on the first hop. That was one
benchmark. MQuAKE is a second, built by different authors for a different
purpose, and it carries the hop chain explicitly in `orig.triples_labeled` — so
the same question can be asked without inferring anything.

WHAT IS MEASURED, and the one that matters is the second:

1. The exposure rate per file: what fraction of questions name an edited
   subject, at STRICT (the subject's own surface form) or above.

2. The CROSS-TABULATION of exposure against where the edit sits. For each case
   the chain head is `triples_labeled[0][0]`. An edit is "on the head" when the
   subject it rewrites is that entity. The prediction under [E-038] is that
   head-edited cases are exposed and later-hop-edited cases are not.

HOW IT COULD COME OUT WRONG. The prediction fails if exposure is roughly equal
in both columns — that would say naming the subject is a property of how MQuAKE
phrases questions generally, not of where the edit landed, and the [E-038]
reading does not transfer. It also fails if head-edited cases are exposed at a
rate indistinguishable from the overall rate.

WHAT THIS IS NOT. It was not pre-registered. The cross-tabulation was written
after four verdicts were read by hand while building the adapter, so the
direction was known before the number was. It is reported as a measurement that
can now be repeated, not as a prediction that was risked.

The matchers are also UNVALIDATED: no precision or recall exists for them yet,
so every rate here inherits an unmeasured error. STRICT remains a lower bound —
an item naming the subject only by description is counted clean — so the true
exposure is higher than reported, never lower.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import platform
import sys
from datetime import date
from pathlib import Path

import editscreen
from editscreen.adapters import mquake
from editscreen.screen import MATCHER_VERSION, screen_any
from editscreen.types import Level

REPO = Path(__file__).resolve().parents[3]
# The MQuAKE files live in edit-slice, not here, and this is the one thing in
# this script that will break on another machine. Pass --data to override.
CODE = REPO.parent
DEFAULT_DATA = CODE / "open-concept-lab" / "ai" / "edit-slice" / "data" / "mquake"
FILES = ("MQuAKE-T", "MQuAKE-CF-3k", "MQuAKE-CF")


def _editscreen_commit() -> str | None:
    """The commit of editscreen that produced these numbers.

    0.2.0a1 is not on PyPI, so the version string alone does not identify
    the code. Without this, the run is not reproducible by anyone who did
    not have the working tree.
    """
    import subprocess
    src = Path(editscreen.__file__).resolve().parent
    try:
        out = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=10)
        dirty = subprocess.run(["git", "-C", str(src), "status", "--porcelain"],
                               capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    sha = out.stdout.strip()
    return f"{sha}-dirty" if dirty.stdout.strip() else sha


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def chain_head(case: dict) -> str | None:
    chain = (case.get("orig") or {}).get("triples_labeled")
    if isinstance(chain, list) and chain and isinstance(chain[0], list) and chain[0]:
        return chain[0][0]
    return None


def measure(path: Path) -> dict:
    cases = json.loads(path.read_text(encoding="utf-8"))

    levels: collections.Counter[str] = collections.Counter()
    by_hops: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0])
    # [exposed, total] for questions whose case edits the chain head, and not.
    cross = {"head_edited": [0, 0], "head_not_edited": [0, 0]}
    head_unreadable = 0

    for case, items in zip(cases, _grouped(path), strict=True):
        head = chain_head(case)
        subjects = {e.subject for e in items[0].edits}
        if head is None:
            head_unreadable += 1
            column = None
        else:
            column = "head_edited" if head in subjects else "head_not_edited"

        for item in items:
            verdict = screen_any(item.edits, item.probe)
            levels[verdict.level.name] += 1
            exposed = verdict.level >= Level.STRICT

            if item.test_type:
                by_hops[item.test_type][1] += 1
                by_hops[item.test_type][0] += int(exposed)
            if column:
                cross[column][1] += 1
                cross[column][0] += int(exposed)

    total = sum(levels.values())
    return {
        "file": path.name,
        "sha256": sha256(path),
        "n_cases": len(cases),
        "n_questions": total,
        "levels": dict(levels),
        "exposure_rate_strict_or_above": _rate(
            levels.get("STRICT", 0) + levels.get("ALIAS", 0), total),
        "by_hops": {k: {"exposed": v[0], "total": v[1], "rate": _rate(v[0], v[1])}
                    for k, v in sorted(by_hops.items())},
        "cross_tabulation": {
            k: {"exposed": v[0], "total": v[1], "rate": _rate(v[0], v[1])}
            for k, v in cross.items()
        },
        "cases_with_unreadable_chain_head": head_unreadable,
    }


def _grouped(path: Path) -> list[list]:
    """Items, regrouped per case, so each case's questions stay together."""
    out: dict[str, list] = collections.defaultdict(list)
    for item in mquake.load(path):
        out[item.item_id.rsplit(":q", 1)[0]].append(item)
    return list(out.values())


def _rate(hits: int, total: int) -> float | None:
    return round(hits / total, 4) if total else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--out", type=Path,
                    default=REPO / "results" / "E-048-mquake-exposure.json")
    args = ap.parse_args()

    files = [args.data / f"{n}.json" for n in FILES]
    missing = [f for f in files if not f.exists()]
    if missing:
        print("missing: " + ", ".join(str(m) for m in missing), file=sys.stderr)
        return 2

    payload = {
        "ticket": "E-048",
        "date": date.today().isoformat(),
        "question": "does a MQuAKE question name a subject its case edited, and "
                    "does that track whether the edit sits on the chain head?",
        "pre_registered": False,
        "matchers_validated": False,
        "editscreen_version": editscreen.__version__,
        "editscreen_commit": _editscreen_commit(),
        "matcher_version": MATCHER_VERSION,
        "python": platform.python_version(),
        "model": None,
        "gradients": False,
        "note": "Exposure is a property of how the item was written. No model is "
                "loaded and nothing is edited, so this is unaffected by the "
                "[E-043]/[E-047] gradient failure. STRICT is a lower bound: the "
                "true exposure is higher than reported, never lower.",
        "files": [measure(f) for f in files],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    for f in payload["files"]:
        c = f["cross_tabulation"]
        print(f"{f['file']:18} n={f['n_questions']:6} "
              f"exposed={f['exposure_rate_strict_or_above']:.3f}  "
              f"head-edited={c['head_edited']['rate']}  "
              f"later-hop={c['head_not_edited']['rate']}")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
