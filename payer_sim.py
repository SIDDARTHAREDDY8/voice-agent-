"""Simulated insurance payer: an IVR gate + a live rep, driven by an LLM that
knows a hidden 'ground truth' benefits record.

Why simulate? You can't hammer real payer lines in a demo (and shouldn't).
A simulator also lets the eval harness know the correct answer, so accuracy is
measurable. On purpose, some scenarios make the rep slightly wrong or vague —
that's what the agent's verification layer has to catch.
"""
import json

from llm import MODEL_SIM, chat

SIM_SYSTEM = """You are role-playing the INSURANCE PAYER side of a phone call for a
healthcare eligibility demo. You are NOT an assistant. Stay in character.

Behave like a real payer line:
1. First 1-2 turns: you are the IVR. Ask the caller to state member ID, patient
   date of birth, and provider NPI before you connect them.
2. Then you become a live representative named 'Dana'. Give a call reference
   number early (e.g. "your reference number is 8821-XX").
3. Answer ONLY what is asked, one turn at a time, conversationally and briefly,
   like a busy rep. Do not dump all benefits at once.
4. Use the GROUND TRUTH below as the real record. Never reveal fields that
   weren't asked about.

BEHAVIOR FLAGS for this call (obey them — they test the caller's agent):
{behavior}

GROUND TRUTH (the real benefits record):
{truth}
"""


class PayerSim:
    def __init__(self, ground_truth: dict, behavior: str = "Be accurate and cooperative."):
        self.system = SIM_SYSTEM.format(
            truth=json.dumps(ground_truth, indent=2), behavior=behavior)

    def reply(self, transcript: list[dict]) -> str:
        # From the payer's POV, the agent is the 'user'. Skip any empty turns —
        # the API rejects empty message content.
        msgs = [{"role": "user" if t["speaker"] == "agent" else "assistant",
                 "content": t["text"]} for t in transcript if t["text"].strip()]
        return chat(self.system, msgs, model=MODEL_SIM, max_tokens=250, temperature=0.7)
