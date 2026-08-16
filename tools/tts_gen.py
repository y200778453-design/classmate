"""Generate TTS sample WAVs (Cantonese zh-HK / Mandarin zh-CN / English en-US) at 16 kHz."""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "models"

SAMPLES = [
    ("yue", "Microsoft Tracy Desktop", "點解糖尿病人容易有傷口感染㗎？"),
    ("zh", "Microsoft Huihui Desktop", "為什麼低血糖比高血糖更危險呢？"),
    ("en", "Microsoft Zira Desktop", "What is the normal range of blood pressure?"),
]

PS_TMPL = r'''
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$s.SelectVoice('{voice}')
$s.Rate = -1
$s.SetOutputToWaveFile('{out}')
$s.Speak('{text}')
$s.Dispose()
'''


def synth(voice: str, text: str, raw: Path):
    ps = PS_TMPL.format(voice=voice, out=str(raw).replace("'", "''"), text=text.replace("'", "''"))
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0 or not raw.exists():
        raise RuntimeError(f"TTS failed: {r.stderr[:200]}")


def resample_16k(raw: Path, out: Path):
    w = wave.open(str(raw), "rb")
    assert w.getsampwidth() == 2 and w.getnchannels() == 1, "unexpected wav format"
    sr = w.getframerate()
    data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    w.close()
    if sr != 16000:
        n = int(len(data) * 16000 / sr)
        data = np.interp(np.linspace(0, len(data) - 1, n), np.arange(len(data)), data).astype(np.int16)
    outw = wave.open(str(out), "wb")
    outw.setnchannels(1)
    outw.setsampwidth(2)
    outw.setframerate(16000)
    outw.writeframes(data.tobytes())
    outw.close()
    return len(data) / 16000


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for tag, voice, text in SAMPLES:
        raw = OUT / f"tts_{tag}_raw.wav"
        final = OUT / f"tts_{tag}.wav"
        try:
            synth(voice, text, raw)
            secs = resample_16k(raw, final)
            print(f"OK {tag}: {secs:.1f}s -> {final}")
        except Exception as exc:
            print(f"FAIL {tag}: {exc}")


if __name__ == "__main__":
    main()
