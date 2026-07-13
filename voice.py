"""The voice layer — makes a call audible instead of just readable.

Voice is the product; text turns were only ever a stand-in. This renders a
transcript to real speech using macOS `say` (offline, no API key, no account)
with a distinct voice per speaker, and stitches the turns into one audio file
you can play, embed, or hand to someone who won't read the code.

Stdlib only — no pydantic, no ffmpeg, no pip install. `python3 voice.py --play`
works on a bare interpreter.

Deliberately NOT telephony. The payer here is a simulator, so dialing a real
number would prove nothing the text loop doesn't already prove — see the
limitations section of the README. This makes the existing loop hearable; the
telephony seam stays `call.py`.

    python3 voice.py                # render the scripted offline call -> call.wav
    python3 voice.py --play         # ...and play it when done
    python3 voice.py -o call.mp3    # compress, if you have a working ffmpeg
    python run_demo.py 2 --speak    # speak a live generated call, turn by turn
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

# Two clearly different voices so you can tell who's talking with your eyes shut.
VOICES = {"agent": "Samantha", "payer": "Tessa"}

# 16-bit little-endian PCM: what `say` emits and what stdlib `wave` can read, so
# stitching needs no ffmpeg. (ffmpeg is easy to break — a conda env shadowing the
# system OpenGL is enough to make its libavfilter abort on load.)
_RATE = 22050
_FORMAT = f"LEI16@{_RATE}"
_GAP_SECONDS = 0.35


def _require(*tools: str) -> None:
    missing = [t for t in tools if shutil.which(t) is None]
    if missing:
        sys.exit(f"missing {', '.join(missing)} — the voice layer needs "
                 f"macOS `say` (this is a macOS-only demo).")


def _normalize(transcript) -> list[tuple[str, str]]:
    """Accept run_call's [{'speaker','text'}] or demo_offline's [(SPEAKER, text)]."""
    turns = []
    for t in transcript:
        speaker, text = (t["speaker"], t["text"]) if isinstance(t, dict) else t
        text = text.strip()
        if text:
            turns.append((speaker.lower(), text))
    return turns


def speak(speaker: str, text: str) -> None:
    """Say one turn out loud, blocking until it finishes."""
    subprocess.run(["say", "-v", VOICES.get(speaker, "Samantha"), text], check=True)


def _clip(text: str, voice: str, path: Path) -> None:
    subprocess.run(["say", "-v", voice, "-o", str(path),
                    f"--data-format={_FORMAT}", text], check=True)


def _to_mp3(wav: Path, mp3: Path) -> bool:
    """Best-effort MP3. ffmpeg is optional here — a WAV plays fine everywhere."""
    if shutil.which("ffmpeg") is None:
        return False
    done = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
                           "-c:a", "libmp3lame", "-q:a", "4", str(mp3)],
                          capture_output=True)
    return done.returncode == 0 and mp3.exists()


def render(transcript, out: str = "call.wav") -> Path:
    """Render every turn to speech and stitch them into one file, with a beat of
    silence between turns so it sounds like a conversation, not a run-on.

    Pure stdlib: `say` writes 16-bit PCM, `wave` concatenates it. If `out` ends
    in .mp3 and a working ffmpeg is around, we compress at the end — otherwise
    you get the .wav and a note, rather than a stack trace.
    """
    _require("say")
    turns = _normalize(transcript)
    if not turns:
        sys.exit("Nothing to render — the transcript is empty.")

    out_path = Path(out)
    wav_path = out_path.with_suffix(".wav")
    gap = b"\x00" * (2 * int(_RATE * _GAP_SECONDS))  # 16-bit mono silence

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        with wave.open(str(wav_path), "wb") as out_wav:
            out_wav.setnchannels(1)
            out_wav.setsampwidth(2)
            out_wav.setframerate(_RATE)
            for i, (speaker, text) in enumerate(turns):
                clip = tmp / f"{i:03d}.wav"
                _clip(text, VOICES.get(speaker, "Samantha"), clip)
                with wave.open(str(clip), "rb") as w:
                    out_wav.writeframes(w.readframes(w.getnframes()))
                out_wav.writeframes(gap)
                print(f"  {speaker:>5} ({VOICES.get(speaker, '?'):8}) {text[:58]}…")

    final = wav_path
    if out_path.suffix == ".mp3":
        if _to_mp3(wav_path, out_path):
            wav_path.unlink()
            final = out_path
        else:
            print("\n  (ffmpeg unavailable or broken — keeping the .wav)")

    print(f"\nwrote {final} ({final.stat().st_size:,} bytes, {len(turns)} turns)")
    return final


def main():
    ap = argparse.ArgumentParser(description="Render a payer call to audio.")
    ap.add_argument("-o", "--out", default="call.wav",
                    help="output path (.wav, or .mp3 if ffmpeg works)")
    ap.add_argument("--play", action="store_true", help="play it when done")
    args = ap.parse_args()

    # The scripted adversarial call — no API key needed to hear the pushback.
    from sample_call import SAMPLE_TRANSCRIPT

    print("Rendering the ADVERSARIAL call (rep misstates the deductible)…\n")
    out = render(SAMPLE_TRANSCRIPT, args.out)
    if args.play:
        subprocess.run(["afplay", str(out)], check=True)


if __name__ == "__main__":
    main()
