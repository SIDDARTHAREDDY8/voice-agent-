"""Ground-truth benefit records + payer behavior for the eval harness.

`expected` is the subset of fields we score accuracy against. `behavior` steers
the simulated rep — including two adversarial cases that a naive agent gets
wrong but the verification layer should catch.
"""
SCENARIOS = [
    {
        "name": "Clean PPO — cooperative rep",
        "behavior": "Be accurate and cooperative. Give clear numbers when asked.",
        "truth": {
            "payer": "BlueCross BlueShield", "plan_name": "BCBS PPO Gold",
            "plan_type": "PPO", "coverage_active": True, "effective_date": "2026-01-01",
            "copay_pcp": 25, "copay_specialist": 50,
            "deductible_individual": 1500, "deductible_met": 600,
            "oop_max_individual": 6000, "oop_met": 1200,
            "coinsurance_pct": 20, "prior_auth_required": True,
            "reference_number": "8821-QT",
        },
        "expected": {
            "coverage_active": True, "plan_type": "PPO",
            "copay_specialist": 50, "deductible_individual": 1500,
            "deductible_met": 600, "oop_max_individual": 6000,
            "coinsurance_pct": 20, "prior_auth_required": True,
        },
    },
    {
        "name": "HMO — terse rep, must probe",
        "behavior": "Be terse and only answer the exact question. Give the "
                    "reference number only if explicitly asked.",
        "truth": {
            "payer": "Aetna", "plan_name": "Aetna HMO Select",
            "plan_type": "HMO", "coverage_active": True, "effective_date": "2025-07-01",
            "copay_pcp": 15, "copay_specialist": 40,
            "deductible_individual": 500, "deductible_met": 500,
            "oop_max_individual": 4000, "oop_met": 2100,
            "coinsurance_pct": 0, "prior_auth_required": True,
            "reference_number": "5540-AH",
        },
        "expected": {
            "coverage_active": True, "plan_type": "HMO",
            "copay_specialist": 40, "deductible_individual": 500,
            "deductible_met": 500, "oop_max_individual": 4000,
            "prior_auth_required": True,
        },
    },
    {
        "name": "ADVERSARIAL — rep misstates deductible met",
        "behavior": "You are cooperative BUT when asked how much of the "
                    "deductible has been met, mistakenly say $2,000 (higher "
                    "than the $1,000 deductible). If the caller pushes back, "
                    "apologize and correct it to $400.",
        "truth": {
            "payer": "UnitedHealthcare", "plan_name": "UHC Choice Plus",
            "plan_type": "PPO", "coverage_active": True, "effective_date": "2026-01-01",
            "copay_pcp": 30, "copay_specialist": 60,
            "deductible_individual": 1000, "deductible_met": 400,
            "oop_max_individual": 5000, "oop_met": 900,
            "coinsurance_pct": 20, "prior_auth_required": False,
            "reference_number": "7712-UH",
        },
        "expected": {
            "coverage_active": True, "plan_type": "PPO",
            "deductible_individual": 1000, "deductible_met": 400,
            "oop_max_individual": 5000,
        },
    },
    {
        "name": "Portal-only — rep can't confirm OOP max",
        "behavior": "Be cooperative on every item EXCEPT the out-of-pocket "
                    "maximum: when asked, say you can't see it on your end and "
                    "the provider will need to check the online portal. Answer "
                    "everything else normally.",
        "truth": {
            "payer": "Cigna", "plan_name": "Cigna Open Access Plus",
            "plan_type": "PPO", "coverage_active": True, "effective_date": "2026-01-01",
            "copay_pcp": 20, "copay_specialist": 45,
            "deductible_individual": 750, "deductible_met": 300,
            "oop_max_individual": 4500, "oop_met": 500,
            "coinsurance_pct": 10, "prior_auth_required": False,
            "reference_number": "3390-CG",
        },
        "expected": {
            "coverage_active": True, "plan_type": "PPO",
            "copay_specialist": 45, "deductible_individual": 750,
            "deductible_met": 300, "prior_auth_required": False,
        },
    },
]
