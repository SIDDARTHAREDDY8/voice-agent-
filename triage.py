"""Triage: decide what happens to a finished call.

The scaling problem in payer voice AI: you can't have a human review every call,
and you can't blindly auto-post data that might be wrong. So each call is routed:

  AUTO_POST  — confident + consistent + complete → write straight to the EHR
  REVIEW     — a required field is missing or low-confidence → a human glances
  REDO       — the payer data is internally inconsistent → re-verify on a fresh call

This is the lever that lets a small team stand behind millions of calls: humans
only touch the fraction the system isn't sure about.
"""
from dataclasses import dataclass, field

from schema import EligibilityResult
from verifier import REQUIRED, verify

CONF_THRESHOLD = 0.80


@dataclass
class Triage:
    route: str                       # AUTO_POST | REVIEW | REDO
    reasons: list = field(default_factory=list)
    min_conf: float = 0.0
    flags: list = field(default_factory=list)


def triage(result: EligibilityResult, confidences: dict, flags=None) -> Triage:
    flags = verify(result) if flags is None else flags
    inconsistencies = [f for f in flags if f.startswith(("INCONSISTENT", "INVALID"))]
    missing = [label for name, label in REQUIRED if getattr(result, name) is None]

    present_conf = [confidences.get(name, 0.0)
                    for name, _ in REQUIRED if getattr(result, name) is not None]
    min_conf = min(present_conf) if present_conf else 0.0
    low = [(label, confidences.get(name, 0.0)) for name, label in REQUIRED
           if getattr(result, name) is not None and confidences.get(name, 0.0) < CONF_THRESHOLD]

    if inconsistencies:
        return Triage("REDO", ["payer data internally inconsistent — re-verify on a fresh call"],
                      min_conf, flags)
    if missing:
        return Triage("REVIEW", ["not confirmed by payer: " + ", ".join(missing)], min_conf, flags)
    if low:
        return Triage("REVIEW", [f"low confidence on {lbl} ({c:.0%})" for lbl, c in low],
                      min_conf, flags)
    return Triage("AUTO_POST", ["all required fields confirmed with high confidence"],
                  min_conf, flags)
