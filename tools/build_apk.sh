#!/usr/bin/env bash
# ClassMate APK 一鍵打包（在任何 Linux 主機 / WSL2 Ubuntu 上執行）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== [1/5] 系統依賴 (JDK17 + 圖形庫) =="
sudo apt-get update -y
sudo apt-get install -y openjdk-17-jdk unzip wget python3 python3-pip python3-venv \
  libgl1 libegl1 libxkbcommon0 libdbus-1-3 libfontconfig1 libnss3 libasound2 libxcb-* cmake

SDK="${ANDROID_HOME:-$HOME/Android/Sdk}"
export ANDROID_HOME="$SDK"
echo "== [2/5] Android SDK ($SDK) =="
if [ ! -x "$SDK/cmdline-tools/latest/bin/sdkmanager" ]; then
  mkdir -p "$SDK/cmdline-tools"
  wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O /tmp/cmdtools.zip
  unzip -q -o /tmp/cmdtools.zip -d "$SDK/cmdline-tools"
  mv "$SDK/cmdline-tools/cmdline-tools" "$SDK/cmdline-tools/latest"
fi
yes | "$SDK/cmdline-tools/latest/bin/sdkmanager" --licenses >/dev/null 2>&1 || true
"$SDK/cmdline-tools/latest/bin/sdkmanager" --install \
  "platform-tools" "platforms;android-34" "build-tools;34.0.0" "ndk;27.2.12479018" "cmake;3.22.1"

echo "== [3/5] Python 環境 =="
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install "PySide6==6.11.1" pyside6-android-deploy requests

echo "== [4/5] 打包 APK（首次約 20-40 分鐘）=="
pyside6-android-deploy \
  --name ClassMate \
  --org edu.kwnc.classmate \
  --version 1.0.0 \
  --requirements "requests>=2.28,pyjnius" \
  --extra-ignore-dirs "tests,docs,tools,models" \
  --permission android.permission.RECORD_AUDIO \
  --permission android.permission.INTERNET \
  --permission android.permission.POST_NOTIFICATIONS \
  --permission android.permission.FOREGROUND_SERVICE \
  --permission android.permission.SYSTEM_ALERT_WINDOW \
  --permission android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS \
  run.py

echo "== [5/5] 完成！APK 位置：=="
find . -type f -name "*.apk" | grep -v "/lib/" | sort
