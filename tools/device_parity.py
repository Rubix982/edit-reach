"""Does this machine's accelerator give the same answer as the CPU?

    python3 tools/device_parity.py --model gpt2

Run this BEFORE believing any locally-measured number, and re-run it after a
torch upgrade. It exists because Apple's Metal backend has a documented class
of silently wrong results -- no exception, no NaN, just a different number --
and because `editreach.local` used to select it automatically.

The reference case, from TransformerLens #1178: GPT-2 small on the IOI prompt
scores a logit difference of +3.36 on CPU and -0.99 on MPS. Sign flipped, no
warning. The reporter ran about a hundred patching experiments before noticing.

This compares the quantity this package actually reports -- a teacher-forced
summed log-probability -- rather than a generic tensor op, because that is what
a wrong answer would corrupt.
"""

from __future__ import annotations

import argparse
import sys

import torch

from editreach.local import load, score

#: Prompt/continuation pairs with one right answer and one wrong one, so a
#: failure shows up as a changed MARGIN and not only as changed magnitudes.
CASES: tuple[tuple[str, str, str], ...] = (
    ("The Eiffel Tower is located in the city of", " Paris", " Tokyo"),
    ("The capital of Japan is", " Tokyo", " Paris"),
    ("Water freezes at a temperature of", " 0", " 100"),
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="gpt2")
    ap.add_argument("--against", default=None,
                    help="device to test (default: mps if present, else cuda)")
    ap.add_argument("--tol", type=float, default=1e-2,
                    help="max allowed absolute difference in summed log-prob")
    a = ap.parse_args()

    other = a.against or ("mps" if torch.backends.mps.is_available()
                          else "cuda" if torch.cuda.is_available() else None)
    if other is None:
        print("no accelerator present; cpu is the only device, nothing to compare")
        return 0

    print(f"{a.model}: cpu vs {other}\n")
    m_cpu, t_cpu = load(a.model, device="cpu")
    m_oth, t_oth = load(a.model, device=other)

    worst = 0.0
    sign_flips = 0
    for prompt, right, wrong in CASES:
        row = []
        for m, t in ((m_cpu, t_cpu), (m_oth, t_oth)):
            r = score(m, t, prompt, right).logprob_sum
            w = score(m, t, prompt, wrong).logprob_sum
            row.append((r, w, r - w))
        (rc, wc, mc), (ro, wo, mo) = row
        d = max(abs(rc - ro), abs(wc - wo))
        worst = max(worst, d)
        flipped = (mc > 0) != (mo > 0)
        sign_flips += flipped
        print(f"  {prompt[:38]:40} margin cpu {mc:+7.3f}  {other} {mo:+7.3f}"
              f"  |d|={d:.2e}{'   <-- SIGN FLIP' if flipped else ''}")

    print(f"\n  worst absolute difference: {worst:.3e}   tolerance: {a.tol:.0e}")
    if sign_flips:
        print(f"\nFAIL: {sign_flips} margin(s) changed sign. {other} is not usable "
              f"for this package on this machine.")
        return 1
    if worst > a.tol:
        print(f"\nFAIL: {other} disagrees with cpu beyond tolerance.")
        return 1
    print(f"\nPASS: {other} agrees with cpu on every case.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
