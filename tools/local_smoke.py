"""Does the whole measurement path run with no NDIF account and no network?

    python3 tools/local_smoke.py

Loads a small Llama-architecture model in process, reads a coefficient through
a local nnsight trace, and scores it against a different-subject floor. It
prints the same line `README.md` advertises, produced without an API key.

This is a SMOKE TEST and its numbers are not a result. The model is 135M
parameters, `u` and `denom` are placeholders overridden by `reference=`, and
the floor prompts are structurally identical to the subject ones. What it
establishes is that `connect(backend="local")`, `resolve_arch`,
`coefficient_for` and `Baseline` compose on a machine that has only weights --
which was not true before the backend seam existed, and is the claim a reader
without NDIF access most needs checked.

Run `tools/device_parity.py` first. This reports whatever the device gives it.
"""

from __future__ import annotations

import argparse
import os

import torch

from editreach.arch import resolve_arch
from editreach.control import Baseline
from editreach.coefficient import coefficient_for
from editreach.remote import connect, uses_remote

#: Llama architecture at 135M, so `resolve_arch` resolves and the download is
#: ~270MB rather than ~16GB. GPT-2 would NOT work here: `ARCH` covers llama and
#: gptj, and GPT-2 is neither.
DEFAULT_MODEL = "HuggingFaceTB/SmolLM2-135M"

SUBJECT = "The Eiffel Tower is located in"
SAME = ("The Eiffel Tower is located in", "The Eiffel Tower can be found in")
DIFF = ("The Statue of Liberty is located in", "Mount Fuji is located in")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--layer", type=int, default=5)
    a = ap.parse_args()

    # Proving the point: a key in the environment must not be what makes this
    # work, so it is removed rather than merely unused.
    os.environ.pop("NNSIGHT_API_KEY", None)

    model = connect(a.model, backend="local")
    assert not uses_remote(model), "backend='local' must not trace remotely"
    arch, n_layers, d_mlp = resolve_arch(model, a.model)
    print(f"{a.model}: arch={arch} layers={n_layers} d_mlp={d_mlp} remote={uses_remote(model)}")

    # Indices are absolute on the UNPADDED prompt; -1 raises, by design.
    def last(prompts):
        return [len(model.tokenizer(p).input_ids) - 1 for p in prompts]

    def read(prompts):
        return coefficient_for(
            model, list(prompts), last(prompts),
            u=torch.zeros(d_mlp), denom=1.0, layer=a.layer,
            remote=uses_remote(model), reference=(SUBJECT, last([SUBJECT])[0]))

    same, diff = read(SAME), read(DIFF)
    print(f"  same subject: {[round(c.value, 4) for c in same]}")
    print(f"  diff subject: {[round(c.value, 4) for c in diff]}")
    print("\n" + str(same[0].against(Baseline.of("different subject",
                                                 [c.value for c in diff]))))
    print("\nsmoke test only -- these numbers are not a measurement.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
