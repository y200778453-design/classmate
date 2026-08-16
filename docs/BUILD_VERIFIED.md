# 安卓打包鏈驗證報告（APK 建置前置檢查）

狀態：**打包鏈所有輸入已在本機驗證通過**；實際編譯需 Linux（WSL2 重啟後可用，或 GitHub Actions）。

## 驗證項目

| 項目 | 結果 | 說明 |
|---|---|---|
| pyside6-android-deploy 來源 | ✅ 隨 Linux 版 PySide6 wheel 分發 | PyPI 無此套件（404 實測）；Windows wheel 亦無（Scripts 實測） |
| 官方流程文件 | ✅ 已核對 | doc-snapshots.qt.io deployment-pyside6-android-deploy：僅支援 Unix host、入口須名為 main.py、wheel 走 qtpip/下載頁、NDK r26b |
| CLI 旗標 | ✅ 源碼核對 | android_deploy.py 無 --permission/--org/--requirements/--version；僅 --name/--wheel-pyside/--wheel-shiboken/--ndk-path/--sdk-path/--extra-ignore-dirs 等 → 已改為 buildozer.spec 補丁方案 |
| buildozer.spec 機制 | ✅ 源碼核對 | 工具生成 spec 時若已存在則直接採用（buildozer.py initialize）→ dry-run 生成後補丁再正式建置 |
| NDK/SDK | ✅ r26b + API 35 | 官方 cross_compile_android/main.py（--download-only --skip-update --auto-accept-license -p android_arm64_v8a） |
| PySide6 Android wheel | ✅ 已下載 79.9MB 並驗證 | pyside6-6.11.1-6.11.1-cp311-cp311-android_aarch64.whl：3317 條目、362 個 .so、Qt6AndroidBindings.jar、2403 個 qml 檔、QtQuickControls2、各模組 -dependencies.xml |
| Shiboken6 Android wheel | ✅ 已下載並驗證 | shiboken6-6.11.1-6.11.1-cp311-cp311-android_aarch64.whl：Shiboken.abi3.so + libshiboken6.abi3.so |
| 權限補丁 | ✅ 實測通過 | tools/patch_buildozer.py：RECORD_AUDIO、INTERNET、POST_NOTIFICATIONS、SYSTEM_ALERT_WINDOW、FOREGROUND_SERVICE、REQUEST_IGNORE_BATTERY_OPTIMIZATIONS + requirements requests,pyjnius + package edu.kwnc.classmate |
| main.py 入口 | ✅ 已新增 | pyside6-android-deploy 要求入口命名 main.py |
| Android 相容性加固 | ✅ 48/48 測試通過 | requests 改為可選導入；引擎啟動異常有狀態回饋 |
| 雲端工作流 | ✅ YAML 驗證 | .github/workflows/build-apk.yml 9 步驟：依賴→工具→NDK/SDK→wheels→dry-run→補丁→建置→Artifact |
| 本機打包腳本 | ✅ 已重寫 | tools/build_apk.sh 對應完整 7 步驟 |

## 遺留事項（需要你）

1. **重啟 Windows 一次**（WSL 生效）→ 我可在本機全自動打包（無需 GitHub）；或
2. **GitHub：建 repo + 推送**（教學見 docs/INSTALL_PHONE.md）→ 雲端自動建置，Actions 下載 classmate-apk.zip。
