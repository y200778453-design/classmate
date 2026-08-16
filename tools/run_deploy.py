#!/usr/bin/env python3
"""Run pyside6-android-deploy with an automatic buildozer.spec patch hook.

Injects permissions (mic/overlay/notifications/background), app dependencies
(requests, pyjnius) and package name into buildozer.spec right after the
official tool generates it and before the p4a build starts.
"""
import runpy
import site
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parent / "patch_buildozer.py"


def _scripts_dir() -> Path:
    for p in site.getsitepackages():
        d = Path(p) / "PySide6" / "scripts"
        if d.is_dir():
            return d
    raise RuntimeError("PySide6/scripts not found in site-packages")


def main():
    scripts_dir = _scripts_dir()
    sys.path.insert(0, str(scripts_dir))

    from deploy_lib.android import buildozer as bzmod  # noqa: E402

    original_initialize = bzmod.Buildozer.initialize

    def patched_initialize(config):
        original_initialize(config)
        r = subprocess.run([sys.executable, str(HOOK)], cwd=Path.cwd())
        if r.returncode != 0:
            raise RuntimeError("patch_buildozer.py failed with code %d" % r.returncode)

    bzmod.Buildozer.initialize = staticmethod(patched_initialize)

    sys.argv = ["pyside6-android-deploy"] + sys.argv[1:]
    runpy.run_path(str(scripts_dir / "android_deploy.py"), run_name="__main__")


if __name__ == "__main__":
    main()
