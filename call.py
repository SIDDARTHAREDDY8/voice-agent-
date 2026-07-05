"""Orchestrates one agent<->payer call and returns the transcript."""
from agent import Agent
from payer_sim import PayerSim

MAX_TURNS = 16
END_TOKEN = "[[END_CALL]]"


def run_call(payer: PayerSim, verbose: bool = False) -> list[dict]:
    agent = Agent()
    transcript: list[dict] = []

    for _ in range(MAX_TURNS):
        text = agent.utterance(transcript)
        ended = END_TOKEN in text
        text = text.replace(END_TOKEN, "").strip()
        transcript.append({"speaker": "agent", "text": text})
        if verbose:
            print(f"\n  AGENT: {text}")
        if ended:
            break

        reply = payer.reply(transcript)
        transcript.append({"speaker": "payer", "text": reply})
        if verbose:
            print(f"  PAYER: {reply}")

    return transcript
