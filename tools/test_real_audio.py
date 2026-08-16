"""End-to-end real-audio test: WAV file → recognizer → phrase engine → answer.

Usage: python tools/test_real_audio.py <wav> [--engine vosk|google] [--subject ic]
"""
import argparse
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_wav_16k(path: Path) -> bytes:
    w = wave.open(str(path), "rb")
    assert w.getframerate() == 16000, "sample rate must be 16000"
    assert w.getsampwidth() == 2, "must be 16-bit PCM"
    data = w.readframes(w.getnframes())
    w.close()
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("--engine", choices=["vosk", "google"], default="vosk")
    ap.add_argument("--subject", default="ic")
    args = ap.parse_args()

    from classmate.config import AppConfig
    from classmate.courses import CourseCatalog
    from classmate.phrase_engine import PhraseEngine
    from classmate.answer_engine import AnswerEngine

    cfg = AppConfig(str(ROOT / "models" / "demo_config.json"))
    catalog = CourseCatalog(
        [ROOT / "data" / "courses_a.json", ROOT / "data" / "courses_b.json"], cfg)
    pe = PhraseEngine(sensitivity=55)
    pe.set_names(["李小明", "Xiao Ming", "小明"])
    answer = AnswerEngine(catalog, cfg)

    from classmate.recognizer import autodetect_models
    models = autodetect_models(ROOT / "models")
    print("available models:", models)

    audio = load_wav_16k(Path(args.wav))
    transcripts = []

    if args.engine == "vosk":
        from classmate.recognizer.vosk_recognizer import VoskRecognizer
        rec = VoskRecognizer(
            lambda text, lang, conf: transcripts.append((text, lang, conf)),
            None, "zh", model_paths=models)
        assert rec.start(), "no vosk models found"
        # feed in 0.5s chunks
        step = 8000
        for i in range(0, len(audio), step):
            rec.feed(audio[i:i + step])
        rec.stop()
    else:
        from classmate.recognizer.google_recognizer import GoogleRecognizer
        rec = GoogleRecognizer(
            lambda text, lang, conf: transcripts.append((text, lang, conf)),
            None, "yue")
        rec.start()
        rec.feed(audio)
        import time
        time.sleep(8)
        rec.stop()

    print("transcripts:", transcripts)
    assert transcripts, "no transcript produced"
    text, lang, conf = transcripts[0]
    print(f"RESULT lang={lang} text={text!r}")
    det = pe.detect(text)
    print("detection:", det)
    if det.is_question:
        subj = catalog.get(args.subject)
        hits = pe.match_hotwords(text, subj.hotwords)
        r = answer.answer(text, args.subject, "concise", hits)
        print("ANSWER:", r.answer)
        print("source:", r.source, "hotwords:", r.hotwords)
    print("REAL-AUDIO TEST PASSED")


if __name__ == "__main__":
    main()
