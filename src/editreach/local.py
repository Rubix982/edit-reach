"""Model loading and teacher-forced scoring.

Separate module with a typed interface, per CLAUDE.md: loading, editing, probing,
metrics and reporting do not share a file.

The unit here is **possession**: does a model hold a fact at all? A ground the
model never held cannot be orphaned by an edit — nothing is left standing to
contradict anything — so possession gates every downstream orphan claim [T-039].

Possession is measured by teacher-forcing candidate continuations and comparing
summed log-probabilities. Multi-token answers are summed, never read at position
one alone (CLAUDE.md, "Metrics and experimental hygiene").
"""

from __future__ import annotations

import functools
import logging
import os
from dataclasses import dataclass
from typing import Final

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizerBase

log: Final[logging.Logger] = logging.getLogger("local")

#: MPS is NOT auto-selected, and that is the whole point of this function.
#: Apple's Metal backend has a documented class of SILENT wrong answers -- no
#: exception, no NaN, just a different number. TransformerLens declines to
#: auto-select it for this reason and, as of 2026-11-28, names no torch version
#: it considers safe (`_MPS_MIN_SAFE_TORCH_VERSION = None`, "MPS silent
#: correctness issues are known in PyTorch <= 2.7"). The case behind their
#: policy: GPT-2 small on the IOI prompt gives a logit difference of +3.36 on
#: CPU and -0.99 on MPS, sign flipped, and the reporter ran about a hundred
#: patching experiments before noticing.
#:
#: nnsight has no MPS guardrails at all, so this package was auto-selecting a
#: backend no neighbouring library trusts. CPU is slower and gives the number
#: the paper claims. Opt in with EDITREACH_ALLOW_MPS=1 if you want it, and gate
#: anything you report on a CPU parity check.
def pick_device(explicit: str | None = None) -> str:
    """Where tensors go. `EDITREACH_DEVICE` overrides everything."""
    if explicit:
        return explicit
    env = os.environ.get("EDITREACH_DEVICE")
    if env:
        return env
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        if os.environ.get("EDITREACH_ALLOW_MPS") == "1":
            log.warning(
                "using MPS because EDITREACH_ALLOW_MPS=1. Metal has a known "
                "class of silently wrong results; check any reported number "
                "against cpu before believing it.")
            return "mps"
        log.info("MPS is available and not used; set EDITREACH_ALLOW_MPS=1 to "
                 "opt in, or EDITREACH_DEVICE=mps to force it.")
    return "cpu"


DEVICE: Final[str] = pick_device()


@dataclass(frozen=True)
class Scored:
    """Teacher-forced score of one continuation given one prompt."""

    text: str
    logprob_sum: float
    logprob_mean: float
    n_tokens: int


@dataclass(frozen=True)
class Ranked:
    """Rank of the true answer among type-matched distractors.

    Neither obvious possession test works. The editing literature's standard
    pre-edit condition — P(target_true) > P(target_new) — is a forced binary
    choice, far too easy: GPT-2-medium passes it 75% of the time. Unconstrained
    top-1 is confounded by prompt ambiguity — CounterFact's "X died at" invites
    "the age of 90" and "developed in" invites "the early 1980s", so a model that
    knows the answer still scores zero. Measured on GPT-2 the two disagree 75% vs
    12%, and neither number is possession.

    Constraining candidates to objects attested for the SAME relation fixes both:
    template ambiguity cannot express itself when the model may only choose among
    places, and the choice is hard enough to stay informative at scale.
    """

    true_rank: int
    n_candidates: int
    true_logprob: float
    best: str

    @property
    def top1(self) -> bool:
        return self.true_rank == 1

    @property
    def top_decile(self) -> bool:
        return self.true_rank <= max(1, self.n_candidates // 10)


@dataclass(frozen=True)
class Possession:
    """Whether a model holds `true_answer` rather than `false_answer`."""

    prompt: str
    true: Scored
    false: Scored
    top1: str

    @property
    def margin(self) -> float:
        """Summed log-prob of the true answer minus the false one. >0 = holds."""
        return self.true.logprob_sum - self.false.logprob_sum

    @property
    def holds(self) -> bool:
        return self.margin > 0

    @property
    def holds_strictly(self) -> bool:
        """Holds AND is what the model would actually say first."""
        return self.holds and self.top1.strip().startswith(self.true.text.strip()[:1])


@functools.lru_cache(maxsize=4)
def load(name: str, device: str | None = None) -> tuple[PreTrainedModel, PreTrainedTokenizerBase]:
    """`device` beats EDITREACH_DEVICE beats the default. Part of the cache key,
    so the same name on two devices is two entries rather than a silent reuse --
    which is exactly what a cpu-vs-mps parity check needs."""
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float32).to(pick_device(device))
    model.eval()
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return model, tok


@torch.no_grad()
def score(model: PreTrainedModel, tok: PreTrainedTokenizerBase, prompt: str, continuation: str) -> Scored:
    """Summed log P(continuation | prompt), teacher-forced."""
    cont = continuation if continuation.startswith(" ") else " " + continuation
    p_ids = tok(prompt, return_tensors="pt").input_ids
    c_ids = tok(cont, return_tensors="pt", add_special_tokens=False).input_ids
    ids = torch.cat([p_ids, c_ids], dim=1).to(model.device)

    logits = model(ids).logits[0].float()
    logprobs = torch.log_softmax(logits, dim=-1)
    start = p_ids.shape[1]
    total = 0.0
    for i, tid in enumerate(c_ids[0].tolist()):
        total += logprobs[start + i - 1, tid].item()
    n = c_ids.shape[1]
    return Scored(text=continuation, logprob_sum=total, logprob_mean=total / n, n_tokens=n)


@torch.no_grad()
def top1(model: PreTrainedModel, tok: PreTrainedTokenizerBase, prompt: str, max_new: int = 4) -> str:
    ids = tok(prompt, return_tensors="pt").input_ids.to(model.device)
    out = model.generate(ids, max_new_tokens=max_new, do_sample=False,
                         pad_token_id=tok.pad_token_id)
    return tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)


def possesses(model: PreTrainedModel, tok: PreTrainedTokenizerBase, prompt: str,
              true_answer: str, false_answer: str) -> Possession:
    return Possession(
        prompt=prompt,
        true=score(model, tok, prompt, true_answer),
        false=score(model, tok, prompt, false_answer),
        top1=top1(model, tok, prompt),
    )


def rank_among(model: PreTrainedModel, tok: PreTrainedTokenizerBase, prompt: str,
               true_answer: str, distractors: list[str]) -> Ranked:
    """Rank `true_answer` against type-matched distractors by MEAN log-prob.

    Mean rather than sum so ranking is not dominated by answer length — a
    one-token country would otherwise beat a three-token city on arithmetic alone.
    """
    candidates = [true_answer, *[d for d in distractors if d != true_answer]]
    scored = [(c, score(model, tok, prompt, c).logprob_mean) for c in candidates]
    scored.sort(key=lambda kv: -kv[1])
    order = [c for c, _ in scored]
    return Ranked(true_rank=order.index(true_answer) + 1, n_candidates=len(order),
                  true_logprob=dict(scored)[true_answer], best=order[0])
