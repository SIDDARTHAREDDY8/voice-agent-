"""A realistic transcript for the ADVERSARIAL scenario, as plain data.

Lives on its own — no pydantic, no anthropic, no imports at all — so the offline
demo and the voice layer can both use it on a bare `python3` with nothing
installed. In the live version this comes out of agent.py <-> payer_sim.py.
"""
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
