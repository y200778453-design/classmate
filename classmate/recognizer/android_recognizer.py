"""Android native SpeechRecognizer via jnius (active only on Android builds).

Language mapping: yue -> yue-HK, zh -> zh-CN, en -> en-US.
Requires RECORD_AUDIO permission granted before start().
"""
from __future__ import annotations

from .base import BaseRecognizer


class AndroidRecognizer(BaseRecognizer):
    name = "android"

    def __init__(self, on_transcript, on_level=None, primary_lang="yue"):
        super().__init__(on_transcript, on_level, primary_lang)
        self._sr = None
        self._intent = None

    @staticmethod
    def available() -> bool:
        try:
            import jnius  # noqa: F401
            return True
        except Exception:
            return False

    def start(self):
        from jnius import autoclass, PythonJavaClass, java_method
        SpeechRecognizer = autoclass("android.speech.SpeechRecognizer")
        Intent = autoclass("android.content.Intent")
        Bundle = autoclass("android.os.Bundle")
        Activity = autoclass("org.kivy.android.PythonActivity")  # pyside6-android-deploy activity
        self._sr = SpeechRecognizer.createSpeechRecognizer(Activity.mActivity)
        lang = {"yue": "yue-HK", "zh": "zh-CN", "en": "en-US"}.get(self.primary_lang, "yue-HK")

        class Listener(PythonJavaClass):
            __javainterfaces__ = ["android/speech/RecognitionListener"]
            __javacontext__ = "app"

            def __init__(self):
                super().__init__()

            @java_method("(Landroid/os/Bundle;)V")
            def onResults(self, results):
                matches = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                if matches and matches.size() > 0:
                    self.owner.emit(matches.get(0), self.owner.primary_lang, 0.8)

            @java_method("(Landroid/os/Bundle;)V")
            def onPartialResults(self, partial):
                pass

            @java_method("(I)V")
            def onError(self, error):
                pass

            @java_method("(I)V")
            def onReadyForSpeech(self, params):
                pass

            @java_method("(I)V")
            def onBeginningOfSpeech(self):
                pass

            @java_method("([B)V")
            def onBufferReceived(self, buffer):
                pass

            @java_method("(F)V")
            def onRmsChanged(self, rmsdB):
                pass

            @java_method("(I)V")
            def onEndOfSpeech(self):
                pass

            @java_method("(I)V")
            def onEvent(self, eventType, params):
                pass

        listener = Listener()
        listener.owner = self
        self._listener = listener
        self._sr.setRecognitionListener(listener)
        self._intent = Intent("android.speech.action.RECOGNIZE_SPEECH")
        self._intent.putExtra("android.speech.extra.LANGUAGE_MODEL",
                              "android.speech.extra.LANGUAGE_MODEL_FREE_FORM")
        self._intent.putExtra("android.speech.extra.LANGUAGE", lang)
        self._intent.putExtra("android.speech.extra.PARTIAL_RESULTS", True)
        self._intent.putExtra("android.speech.extra.MAX_RESULTS", 3)
        self._sr.startListening(self._intent)

    def stop(self):
        if self._sr:
            try:
                self._sr.stopListening()
                self._sr.cancel()
                self._sr.destroy()
            except Exception:
                pass
            self._sr = None

    def needs_audio(self) -> bool:
        return False
