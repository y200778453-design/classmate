"""Android native SpeechRecognizer via jnius (active only on Android builds).

Language mapping: yue -> yue-HK, zh -> zh-CN, en -> en-US.
Requires RECORD_AUDIO permission granted at runtime before start().
"""
from __future__ import annotations

from .base import BaseRecognizer

_ERROR_MSGS = {
    0: "錄音錯誤",
    1: "語音服務用戶端錯誤",
    2: "麥克風權限未開啟",
    3: "網路錯誤",
    4: "網路逾時",
    5: "沒有聽清楚，請再說一次",
    6: "語音服務忙碌中，稍後再試",
    7: "語音服務錯誤",
    8: "沒有偵測到語音",
    9: "請求過於頻繁，稍後再試",
}


class AndroidRecognizer(BaseRecognizer):
    name = "android"

    def __init__(self, on_transcript, on_level=None, primary_lang="yue"):
        super().__init__(on_transcript, on_level, primary_lang)
        self._sr = None
        self._intent = None
        self._listener = None
        self.on_error = None

    @staticmethod
    def available() -> bool:
        try:
            import jnius  # noqa: F401
            return True
        except Exception:
            return False

    def set_on_error(self, callback):
        self.on_error = callback

    def _report(self, msg: str):
        if self.on_error:
            try:
                self.on_error(msg)
            except Exception:
                pass

    def _ensure_record_permission(self) -> bool:
        """Request RECORD_AUDIO at runtime if not granted (Android 6+)."""
        try:
            from android.permissions import check_permission, request_permissions, Permission
            if not check_permission("android.permission.RECORD_AUDIO"):
                request_permissions([Permission.RECORD_AUDIO])
                self._report("請允許麥克風權限，然後再按一次「開始聆聽」")
                return False
            return True
        except Exception:
            try:
                from jnius import autoclass
                activity = autoclass("org.kivy.android.PythonActivity").mActivity
                # PackageManager.PERMISSION_GRANTED == 0
                if activity.checkSelfPermission("android.permission.RECORD_AUDIO") != 0:
                    activity.requestPermissions(["android.permission.RECORD_AUDIO"], 9001)
                    self._report("請允許麥克風權限，然後再按一次「開始聆聽」")
                    return False
                return True
            except Exception as exc:
                self._report(f"無法檢查麥克風權限：{exc}")
                return False

    def start(self):
        from jnius import autoclass, PythonJavaClass, java_method
        SpeechRecognizer = autoclass("android.speech.SpeechRecognizer")
        Intent = autoclass("android.content.Intent")
        Activity = autoclass("org.kivy.android.PythonActivity")

        activity = Activity.mActivity
        if not SpeechRecognizer.isRecognitionAvailable(activity):
            self._report("系統未提供語音辨識服務（需 Google 語音服務），請在設定檢查")
            return False

        if not self._ensure_record_permission():
            return False

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
                code = int(error)
                self.owner._report(_ERROR_MSGS.get(code, f"語音辨識錯誤（代碼 {code}）"))

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

        self._listener = Listener()
        self._listener.owner = self
        self._sr = SpeechRecognizer.createSpeechRecognizer(activity)
        self._sr.setRecognitionListener(self._listener)
        self._intent = Intent("android.speech.action.RECOGNIZE_SPEECH")
        self._intent.putExtra("android.speech.extra.LANGUAGE_MODEL",
                              "android.speech.extra.LANGUAGE_MODEL_FREE_FORM")
        self._intent.putExtra("android.speech.extra.LANGUAGE", lang)
        self._intent.putExtra("android.speech.extra.PARTIAL_RESULTS", True)
        self._intent.putExtra("android.speech.extra.MAX_RESULTS", 3)
        self._sr.startListening(self._intent)
        return True

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
