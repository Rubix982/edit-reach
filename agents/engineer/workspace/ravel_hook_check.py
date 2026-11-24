#!/usr/bin/env python3
"""C-009's hook-equality control: is the vector we intervene on the one we name?

    python3 agents/engineer/workspace/ravel_hook_check.py                  # local, gpt2
    python3 agents/engineer/workspace/ravel_hook_check.py --remote         # NDIF, Llama-3.1-8B

WHY THIS RUNS BEFORE ANY INTERVENTION.

C-009 compares an edit site against an outside benchmark's layer profile. MIB's
RAVEL baseline builds `ResidualStream(layer=L, ..., target_output=True)`, which
`neural/LM_units.py` resolves to pyvene's `"block_output"` - the residual stream
AFTER block L. `editreach`'s `arch.py` writes a ROME edit into
`model.layers[L].mlp.down_proj`, whose output joins the residual stream inside
block L and so appears at the output of block L. Same point, if both index from
zero and if pyvene's `"block_output"` means what its name says.

THAT LAST LINK IS ARGUED, NOT READ - pyvene's resolution lives in pyvene, not in
either repository this project checks out. So it is checked instead of trusted.
A one-off here would not raise an error anywhere; it would quietly answer a
different question than the card asks, one block early or late.

TWO CHECKS, BECAUSE THE REMOTE CASE CANNOT RUN THE FIRST.

  identity  blocks[L].output == hidden_states[L+1] from a plain forward pass.
            This is the definition of "the residual stream after block L" in
            HuggingFace's own terms. Needs local weights.
  chain     blocks[L].output == blocks[L+1].input. The same claim without a
            second forward pass, so it runs on a model served remotely.

The second is the weaker statement on its own - it would also hold under a
consistent off-by-one - which is why the local run exists to anchor it.
"""
from __future__ import annotations

import argparse
import sys

import torch


def _blocks(model):
    """The transformer block list, by the two layouts this project meets."""
    inner = getattr(model, "model", None)
    if inner is not None and hasattr(inner, "layers"):
        return inner.layers
    tr = getattr(model, "transformer", None)
    if tr is not None and hasattr(tr, "h"):
        return tr.h
    raise AttributeError("no block list found on this model")


def _cpu(t):
    """One device for every comparison.

    [C-006] found readings that differ by the GPU that served them, so a
    subtraction across two devices would be measuring that as well as the thing
    under test. This control is about structure, not numerics: it asks whether
    two hooks name the same tensor, and that question deserves a comparison with
    only one variable in it.
    """
    return t.detach().float().cpu()


def _resid(x):
    """A block's output is a tensor or a tuple whose first element is one."""
    return x[0] if isinstance(x, (tuple, list)) else x


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt2")
    ap.add_argument("--remote", action="store_true",
                    help="run on NDIF (implies a model this machine cannot hold)")
    ap.add_argument("--text", default="The city of Adigrat is on the continent of")
    ap.add_argument("--layers", default="", help="comma-separated; default: a spread")
    ap.add_argument("--tol", type=float, default=0.0,
                    help="max abs difference accepted; 0 means bit-identical")
    args = ap.parse_args()

    name = "meta-llama/Llama-3.1-8B" if args.remote and args.model == "gpt2" else args.model
    sys.path.insert(0, "src")
    from editreach.remote import connect

    model = connect(name)
    blocks = _blocks(model)
    n = len(blocks)
    layers = ([int(x) for x in args.layers.split(",") if x.strip()]
              or sorted({0, 1, 5, n // 2, n - 2}))
    layers = [L for L in layers if 0 <= L < n - 1]
    print(f"model: {name}   blocks: {n}   layers checked: {layers}")
    print(f"text:  {args.text!r}\n")

    # --- chain: output of block L is the input to block L+1 -----------------
    # TWO THINGS NNSIGHT 0.8 IMPOSES HERE, AND THE SECOND IS NOT OBVIOUS.
    #
    # Order. Activations are handed out in EXECUTION order, so every request
    # must be made in the order the forward pass reaches it. Asking for block
    # 1's input after block 10 has run raises OutOfOrderError rather than
    # returning a stale value, which is the right behaviour.
    #
    # Scope, and this one cost a confused half hour. Under `remote=True` the
    # BODY OF THE TRACE RUNS ON THE SERVER. A `print` inside it comes back as a
    # remote LOG line, and a dict built inside it is built there and discarded -
    # the client sees an empty dict and a KeyError, with no error from nnsight
    # because nothing went wrong. **Saved proxies must be bound to plain local
    # names**, which are what the client gets back. So the remote path takes one
    # trace per layer instead of accumulating into a container. The queue is
    # ~0.4s, so the extra round trips are cheaper than the cleverness.
    outs: dict[int, object] = {}
    ins: dict[int, object] = {}
    if args.remote:
        for L in sorted(layers):
            with torch.no_grad(), model.trace(args.text, remote=True):
                o = _resid(blocks[L].output).save()
                i = _resid(blocks[L + 1].input).save()
            outs[L], ins[L] = o, i
    else:
        with torch.no_grad(), model.trace(args.text):
            for L in sorted(layers):
                outs[L] = _resid(blocks[L].output).save()
                ins[L] = _resid(blocks[L + 1].input).save()

    ok = True
    print(f"{'layer':>6}  {'chain: out[L] vs in[L+1]':<28}{'max|diff|':>12}")
    for L in layers:
        d = (_cpu(outs[L]) - _cpu(ins[L])).abs().max().item()
        good = d <= args.tol
        ok &= good
        print(f"{L:>6}  {'equal' if good else 'DIFFERENT':<28}{d:>12.3e}")

    if args.remote:
        print("\nchain only: the identity check needs local weights.")
        return 0 if ok else 1

    # --- identity: block L's output IS hidden_states[L+1] -------------------
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(name)
    hf = AutoModelForCausalLM.from_pretrained(name)
    hf.eval()
    with torch.no_grad():
        hs = hf(**tok(args.text, return_tensors="pt"),
                output_hidden_states=True).hidden_states

    # The identity check is a NEIGHBOUR TEST, not a tolerance test, and that is
    # deliberate. nnsight serves this model on mps and HuggingFace loads it on
    # cpu, so a same-tensor comparison still shows ~1e-3 - which is [C-006]'s
    # device effect, not a misalignment. Any tolerance that absorbs it is a
    # number chosen to make the check pass.
    #
    # So ask the question that has no free parameter: of hidden_states[L],
    # [L+1] and [L+2], which one is block L's output closest to? A one-off
    # would put the minimum somewhere else, and the gap between the winner and
    # its neighbours is hundreds of times the device noise.
    print(f"\n{'layer':>6}  {'closest hidden_state':<22}{'|d| at L':>11}{'|d| at L+1':>12}{'|d| at L+2':>12}")
    for L in layers:
        cand = {k: (_cpu(outs[L]) - _cpu(hs[k])).abs().max().item()
                for k in (L, L + 1, L + 2) if 0 <= k < len(hs)}
        best = min(cand, key=cand.get)
        runner = min((v for k, v in cand.items() if k != best), default=float("inf"))
        margin = runner / cand[best] if cand[best] else float("inf")
        good = best == L + 1 and margin > 10
        ok &= good
        cells = "".join(f"{cand.get(k, float('nan')):>12.3e}" for k in (L, L + 1, L + 2))
        print(f"{L:>6}  {('hidden[%d]' % best) + (' ok' if good else ' WRONG'):<22}{cells}"
              f"   x{margin:.0f}")

    print("\n" + ("PASS - block L's output is the residual stream after block L,\n"
                  "       which is where arch.py's layer-L edit lands and what MIB's\n"
                  "       block_output names. The card may quote layer numbers."
                  if ok else
                  "FAIL - the hook is not where the card says it is. Do not quote a\n"
                  "       layer number until this passes."))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
