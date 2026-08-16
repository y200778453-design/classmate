"""ClassMate desktop launcher (also entry point for Android via pyside6-android-deploy)."""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QTimer  # noqa: E402  (module-level helpers below use it)


def build_app(argv=None):
    args = _parse(argv)
    if args.offscreen:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")

    from PySide6.QtCore import QTimer, Qt, QUrl
    from PySide6.QtGui import QFont, QGuiApplication, QIcon, QPainter, QColor, QPixmap, QLinearGradient
    from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonInstance

    from classmate.answer_engine import AnswerEngine
    from classmate.bridge import ClassMateBridge
    from classmate.config import AppConfig
    from classmate.courses import CourseCatalog
    from classmate.history_store import HistoryStore

    use_widgets = sys.platform.startswith(("win", "linux", "darwin"))
    if use_widgets:
        from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon
        app = QApplication(sys.argv)
    else:
        app = QGuiApplication(sys.argv)

    app.setApplicationName("ClassMate")
    app.setOrganizationName("ClassMate")
    _install_fonts()
    app.setFont(QFont("Microsoft YaHei", 10))

    cfg = AppConfig(args.config)
    if args.engine:
        cfg.set("recognitionEngine", args.engine)
    if args.lang:
        cfg.set("languages", [args.lang])
    if args.modeldir:
        cfg.set("modelDir", args.modeldir)
    from classmate.recognizer import autodetect_models
    models = autodetect_models(Path(args.modeldir) if args.modeldir else ROOT / "models")
    if models:
        cfg.set("voskModels", models)

    catalog = CourseCatalog([ROOT / "data" / "courses_a.json", ROOT / "data" / "courses_b.json"], cfg)
    store = HistoryStore(Path.home() / ".classmate" / "history.db")
    bridge = ClassMateBridge(cfg, catalog, AnswerEngine(catalog, cfg), store, ROOT)

    qmlRegisterSingletonInstance(ClassMateBridge, "ClassMate.Core", 1, 0, "Bridge", bridge)
    engine = QQmlApplicationEngine()
    engine.addImportPath(str(ROOT / "qml"))
    engine.load(QUrl.fromLocalFile(str(ROOT / "qml" / "Main.qml")))
    if not engine.rootObjects():
        raise RuntimeError("QML 載入失敗")
    app._qml_engine = engine          # keep engine/window alive beyond this scope
    app._classmate_bridge = bridge
    window = engine.rootObjects()[0]
    window.setProperty("width", int(420 * args.scale))
    window.setProperty("height", int(880 * args.scale))

    tray = None
    if use_widgets and cfg.get("backgroundTray", True):
        tray = _make_tray(app, window, bridge)

    if args.demo:
        QTimer.singleShot(900, bridge.start_demo)
    if args.autoshot:
        _schedule_autoshot(window, Path(args.autoshot))
    return app, window, bridge, tray, args


def _install_fonts():
    """Load bundled/system CJK fonts so text renders offscreen and on minimal systems."""
    if not sys.platform.startswith("win"):
        return
    from PySide6.QtGui import QFontDatabase
    windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
    for name in ("msyh.ttc", "msyhbd.ttc", "segoeui.ttf", "seguisym.ttf", "seguiemj.ttf",
                 "simhei.ttf", "simsun.ttc", "arial.ttf"):
        p = windir / "Fonts" / name
        if p.exists():
            try:
                QFontDatabase.addApplicationFont(str(p))
            except Exception:
                pass


def _parse(argv):
    ap = argparse.ArgumentParser(prog="classmate", description="課堂智聽 ClassMate")
    ap.add_argument("--demo", action="store_true", help="播放腳本化課堂演示（mock 引擎）")
    ap.add_argument("--engine", choices=["auto", "vosk", "google", "mock"], default=None)
    ap.add_argument("--lang", default="yue", help="主要語言: yue/zh/en")
    ap.add_argument("--config", default=None)
    ap.add_argument("--modeldir", default=None)
    ap.add_argument("--offscreen", action="store_true")
    ap.add_argument("--autoshot", default="", help="定時截圖輸出目錄")
    ap.add_argument("--scale", type=float, default=1.0)
    return ap.parse_args(argv)


def _make_icon() -> QIcon:
    from PySide6.QtCore import Qt as _Qt
    from PySide6.QtGui import QColor, QIcon, QLinearGradient, QPainter, QPixmap
    pm = QPixmap(64, 64)
    pm.fill(_Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    g = QLinearGradient(0, 0, 64, 64)
    g.setColorAt(0, QColor("#6C8CFF"))
    g.setColorAt(1, QColor("#9B6CFF"))
    p.setBrush(g)
    p.setPen(_Qt.PenStyle.NoPen)
    p.drawEllipse(2, 2, 60, 60)
    p.setPen(QColor("#FFFFFF"))
    f = p.font()
    f.setPixelSize(26)
    f.setBold(True)
    p.setFont(f)
    p.drawText(pm.rect(), _Qt.AlignmentFlag.AlignCenter, "智")
    p.end()
    return QIcon(pm)


def _make_tray(app, window, bridge):
    from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon
    if not QSystemTrayIcon.isSystemTrayAvailable():
        return None
    tray = QSystemTrayIcon(_make_icon(), app)
    menu = QMenu()
    show_action = menu.addAction("顯示主視窗")
    show_action.triggered.connect(lambda: (window.show(), window.raise_(), window.requestActivate()))
    toggle = menu.addAction("開始/停止聆聽")
    toggle.triggered.connect(bridge.toggleListening)
    menu.addSeparator()
    quit_action = menu.addAction("退出")
    quit_action.triggered.connect(app.quit)
    tray.setContextMenu(menu)
    tray.setToolTip("課堂智聽 ClassMate")
    tray.activated.connect(lambda reason: window.show() if reason == QSystemTrayIcon.ActivationReason.Trigger else None)
    tray.show()

    def notify(event: dict):
        title = "⚠ 點名！請回答" if event.get("urgent") else "課堂提問"
        tray.showMessage(title, (event.get("question") or "")[:60] + "\n" + (event.get("answer") or "")[:60],
                         QSystemTrayIcon.MessageIcon.Information, 6000)
    bridge.questionDetected.connect(notify)
    bridge.nameCalled.connect(notify)
    return tray


def _schedule_autoshot(window, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    counter = {"n": 0}

    def grab():
        counter["n"] += 1
        try:
            pm = window.screen().grabWindow(0, window.x(), window.y(), window.width(), window.height())
            if not pm.isNull():
                pm.save(str(outdir / f"frame_{counter['n']:03d}.png"))
        except Exception:
            pass
        QTimer.singleShot(2500, grab)
    QTimer.singleShot(1500, grab)


def main():
    app, window, bridge, tray, args = build_app()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
