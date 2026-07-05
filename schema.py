"""Structured output the agent must produce, plus a FHIR mapping.

VoiceAdmin's value isn't 'the call happened' — it's clean, structured data the
EHR can ingest without a human re-keying it. This is that contract.
"""
from typing import Optional

from pydantic import BaseModel, Field


class EligibilityResult(BaseModel):
    member_id: Optional[str] = None
    payer: Optional[str] = None
    plan_name: Optional[str] = None
    plan_type: Optional[str] = None            # HMO / PPO / EPO / POS
    coverage_active: Optional[bool] = None
    group_number: Optional[str] = None
    effective_date: Optional[str] = None
    copay_pcp: Optional[float] = None
    copay_specialist: Optional[float] = None
    deductible_individual: Optional[float] = None
    deductible_met: Optional[float] = None
    oop_max_individual: Optional[float] = None
    oop_met: Optional[float] = None
    coinsurance_pct: Optional[float] = None
    prior_auth_required: Optional[bool] = None
    reference_number: Optional[str] = None      # payer's call reference # (needed for appeals)
    notes: Optional[str] = None

    def to_fhir(self) -> dict:
        """Representative FHIR R4 CoverageEligibilityResponse payload.

        Not spec-perfect — intentionally compact to show the *shape* of an
        EHR-ready write-back (Epic/Cerner ingest FHIR benefit items like this).
        """
        def benefit(category, code, money):
            return {
                "category": {"text": category},
                "productOrService": {"text": code},
                "benefit": [{"type": {"text": "copay/limit"},
                             "allowedMoney": {"value": money, "currency": "USD"}}],
            }

        items = []
        if self.copay_specialist is not None:
            items.append(benefit("Specialist Visit", "copay", self.copay_specialist))
        if self.copay_pcp is not None:
            items.append(benefit("PCP Visit", "copay", self.copay_pcp))
        if self.deductible_individual is not None:
            items.append(benefit("Deductible (individual)", "deductible",
                                  self.deductible_individual))
        if self.oop_max_individual is not None:
            items.append(benefit("Out-of-pocket max (individual)", "oop",
                                 self.oop_max_individual))

        return {
            "resourceType": "CoverageEligibilityResponse",
            "status": "active",
            "outcome": "complete" if self.coverage_active else "error",
            "insurer": {"display": self.payer},
            "insurance": [{
                "coverage": {"display": self.plan_name},
                "inforce": self.coverage_active,
                "benefitPeriod": {"start": self.effective_date},
                "item": items,
            }],
            "identifier": [{"system": "payer/call-reference",
                            "value": self.reference_number}],
        }
