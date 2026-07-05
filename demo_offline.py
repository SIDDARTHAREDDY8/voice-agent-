"""Offline demo — runs with NO API key.

The live agent/payer turns and the extractor need an LLM (see run_demo.py). But
the two most important *deterministic* pieces — the verification/reliability
layer and the FHIR write-back — are pure logic and run here against a realistic,
pre-scripted call so you can see exactly what the pipeline produces.

    python demo_offline.py
"""
from schema import EligibilityResult
from verifier import verify

# A realistic transcript for the ADVERSARIAL scenario (rep misstates the
# deductible-met as higher than the deductible). In the live version this comes
# out of agent.py <-> payer_sim.py; here it's scripted for an offline look.
SAMPLE_TRANSCRIPT = [
    ("AGENT", "Hi, this is Riverside Family Medicine calling to verify benefits for a specialist visit. Provider NPI 1548291057."),
    ("PAYER", "Thanks. This is the automated line — please say the member ID and patient date of birth."),
    ("AGENT", "Member ID ZK884120931, date of birth March 12th 1984."),
    ("PAYER", "One moment... connecting you to a representative."),
    ("PAYER", "Hi, this is Dana. Your reference number for this call is 7712-UH. How can I help?"),
    ("AGENT", "Is the member's coverage active today, and what's the plan type?"),
    ("PAYER", "Yes, active. It's a UHC Choice Plus PPO, effective January 1st 2026."),
    ("AGENT", "Great. What's the individual deductible, and how much has been met?"),
    ("PAYER", "The deductible is $1,000, and $2,000 has been met so far."),
    ("AGENT", "Just to confirm — the deductible is $1,000 but $2,000 has been met? That can't exceed the deductible. Can you re-check?"),
    ("PAYER", "Apologies, you're right — let me re-read. $400 has been met."),
    ("AGENT", "Thank you. Specialist copay, out-of-pocket max, and is prior auth required?"),
    ("PAYER", "Specialist copay is $60, individual OOP max is $5,000, and no prior auth is needed for the visit."),
    ("AGENT", "Perfect, that's everything I needed. Thanks Dana."),
]

# What a NAIVE agent records if it accepts the rep's first (wrong) answer.
NAIVE = EligibilityResult(
    member_id="ZK884120931", payer="UnitedHealthcare", plan_name="UHC Choice Plus",
    plan_type="PPO", coverage_active=True, effective_date="2026-01-01",
    copay_specialist=60, deductible_individual=1000, deductible_met=2000,
    oop_max_individual=5000, prior_auth_required=False, reference_number="7712-UH",
)

# What PayerLine records after pushing back and re-confirming.
CORRECTED = NAIVE.model_copy(update={"deductible_met": 400})


def show(title, result):
    print(f"\n{'─'*68}\n{title}\n{'─'*68}")
    print(result.model_dump_json(indent=2, exclude_none=True))
    flags = verify(result)
    print("\nVERIFICATION LAYER:")
    if flags:
        for f in flags:
            print(f"  ⚠  {f}")
    else:
        print("  ✓ All required fields captured and internally consistent.")


def main():
    print("=" * 68)
    print("PayerLine — OFFLINE DEMO (no API key needed)")
    print("Scenario: rep misstates the deductible; agent pushes back.")
    print("=" * 68)

    print("\nSAMPLE CALL TRANSCRIPT")
    print("-" * 68)
    for speaker, text in SAMPLE_TRANSCRIPT:
        print(f"  {speaker:>5}: {text}")

    show("① If the agent had NAIVELY accepted the rep's first answer:", NAIVE)
    print("\n  →  The verifier catches the impossible number instead of letting")
    print("     a bad deductible reach billing. THIS is the reliability moat.")

    show("② What PayerLine actually records (after push-back + re-confirm):", CORRECTED)

    print(f"\n{'─'*68}\nFHIR CoverageEligibilityResponse (EHR write-back payload)\n{'─'*68}")
    import json
    print(json.dumps(CORRECTED.to_fhir(), indent=2))

    print("\n" + "=" * 68)
    print("For the LIVE version (real agent + simulated payer + LLM extraction):")
    print("  export ANTHROPIC_API_KEY=sk-...")
    print("  python run_demo.py 2      # same scenario, fully generated")
    print("  python eval_run.py        # accuracy scored vs. ground truth")
    print("=" * 68)


if __name__ == "__main__":
    main()
