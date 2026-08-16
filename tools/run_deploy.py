#!/usr/bin/env python3
"""Run pyside6-android-deploy with an automatic buildozer.spec patch hook.

Injects permissions (mic/overlay/notifications/background), app dependencies
(requests, pyjnius) and package name into buildozer.spec right after the
official tool generates it and before the p4a build starts.
"""
import runpy
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parent / "patch_buildozer.py"


def _load_android_deploy():
    try:
        from PySide6.scripts import android_deploy  # type: ignore
        return android_deploy
    except ImportError:
        import glob
        import site
        for p in site.getsitepackages():
            hits = glob.glob(str(Path(p) / "PySide6" / "scripts" / "android_deploy.py"))
            if hits:
                spec = importlib.util.spec_from_file_location("android_deploy", hits[0])
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod
        raise


def _load_buildozer_module():
    try:
        from PySide6.scripts.deploy_lib.android import buildozer  # type: ignore
        return buildozer
    except ImportError:
        import glob
        import importlib.util
        import site
        for p in site.getsitepackages():
            hits = glob.glob(str(Path(p) / "PySide6" / "scripts" / "deploy_lib" / "android" / "buildozer.py"))
            if hits:
                spec = importlib.util.spec_from_file_location("deploy_buildozer", hits[0])
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod
        raise


def main():
    android_deploy = _load_android_deploy()
    buildozer_mod = _load_buildozer_module()

    original_initialize = buildozer_mod.Buildozer.initialize

    def patched_initialize(config):
        original_initialize(config)
        r = subprocess.run([sys.executable, str(HOOK)], cwd=Path.cwd())
        if r.returncode != 0:
            raise RuntimeError("patch_buildozer.py failed with code %d" % r.returncode)

    buildozer_mod.Buildozer.initialize = staticmethod(patched_initialize)

    sys.argv = ["pyside6-android-deploy"] + sys.argv[1:]
    runpy.run_path(android_deploy.__file__, run_name="__main__")


if __name__ == "__main__":
    main()
