#!/usr/bin/env bash
# ClassMate APK 一鍵打包（官方流程：Linux 主機 / WSL2 Ubuntu）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== [1/7] 系統依賴 =="
sudo apt-get update -y
sudo apt-get install -y openjdk-17-jdk unzip wget git python3 python3-pip python3-venv \
  libgl1 libegl1 libxkbcommon0 libdbus-1-3 libfontconfig1 libnss3 libasound2t64

echo "== [2/7] Python 環境（PySide6 Linux wheel 內含 pyside6-android-deploy）=="
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install "PySide6==6.11.1" jinja2 pkginfo tqdm "packaging==24.1"

echo "== [3/7] NDK r26b + SDK（官方腳本，快取於 ~/.pyside6-android-deploy）=="
git clone --depth 1 --branch 6.11 https://github.com/qtproject/pyside-pyside-setup /tmp/pyside-setup
pip install GitPython
python /tmp/pyside-setup/tools/cross_compile_android/main.py \
  --download-only --skip-update --auto-accept-license -p android_arm64_v8a --api-level 35

echo "== [4/7] 下載 Qt for Python Android wheels (aarch64) =="
mkdir -p models/wheels
curl -fL -o models/wheels/pyside6-android.whl \
  https://download.qt.io/official_releases/QtForPython/pyside6/pyside6-6.11.1-6.11.1-cp311-cp311-android_aarch64.whl
curl -fL -o models/wheels/shiboken6-android.whl \
  https://download.qt.io/official_releases/QtForPython/shiboken6/shiboken6-6.11.1-6.11.1-cp311-cp311-android_aarch64.whl

echo "== [5/7] 產生並修補 buildozer.spec（權限 + 依賴 + 套件名）=="
pyside6-android-deploy --dry-run --name ClassMate \
  --wheel-pyside models/wheels/pyside6-android.whl \
  --wheel-shiboken models/wheels/shiboken6-android.whl
python tools/patch_buildozer.py

echo "== [6/7] 正式打包（首次約 20-40 分鐘）=="
pyside6-android-deploy --name ClassMate \
  --wheel-pyside models/wheels/pyside6-android.whl \
  --wheel-shiboken models/wheels/shiboken6-android.whl

echo "== [7/7] 完成！APK 位置：=="
find . -type f -name "*.apk" | grep -v "/lib/" | sort
