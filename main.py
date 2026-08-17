"""Android / desktop entry point (must be named main.py for pyside6-android-deploy).

Wraps the real entry so startup crashes are written to classmate_crash.log and
shown as a Toast on Android instead of disappearing silently.
"""
import sys
import traceback
from pathlib import Path


def _crash_log_dir() -> Path:
    try:
        from jnius import autoclass  # type: ignore
        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        files = activity.getExternalFilesDir(None)
        if files:
            return Path(files.getAbsolutePath())
    except Exception:
        pass
    try:
        from PySide6.QtCore import QStandardPaths
        p = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        if p:
            return Path(p)
    except Exception:
        pass
    return Path.home() / ".classmate"


def _toast(title: str, body: str):
    try:
        from jnius import autoclass  # type: ignore
        Toast = autoclass("android.widget.Toast")
        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        msg = (title + "\n" + body)[:220]
        Toast.makeText(activity, msg, 1).show()
    except Exception:
        pass


def main():
    try:
        from run import main as run_main
        run_main()
    except SystemExit:
        raise
    except Exception:
        tb = traceback.format_exc()
        log_dir = _crash_log_dir()
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            (log_dir / "classmate_crash.log").write_text(tb, encoding="utf-8")
        except Exception:
            pass
        try:
            lines = tb.splitlines()
            _toast("ClassMate 啟動失敗", lines[-2] if lines else tb)
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()
