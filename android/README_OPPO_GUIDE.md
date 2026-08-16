# 安卓（OPPO / ColorOS）部署與後台運行指南

## 1. 打包 APK

`pyside6-android-deploy` 隨 **Linux 版 PySide6 wheel** 分發，須在 Linux（WSL2 / 雲端）執行。

```bash
# 一鍵打包（推薦）：自動完成 JDK/NDK r26b/SDK/Android wheels/權限補丁
bash tools/build_apk.sh
```

或推送 GitHub 觸發雲端打包（.github/workflows/build-apk.yml）→ Actions 下載 classmate-apk.zip。

**手動步驟**（build_apk.sh 的內容）：
```bash
pip install "PySide6==6.11.1" jinja2 pkginfo tqdm "packaging==24.1"
git clone --depth 1 --branch 6.11 https://github.com/qtproject/pyside-pyside-setup /tmp/pyside-setup
python /tmp/pyside-setup/tools/cross_compile_android/main.py \
  --download-only --skip-update --auto-accept-license -p android_arm64_v8a --api-level 35
curl -fLO https://download.qt.io/official_releases/QtForPython/pyside6/pyside6-6.11.1-6.11.1-cp311-cp311-android_aarch64.whl
curl -fLO https://download.qt.io/official_releases/QtForPython/shiboken6/shiboken6-6.11.1-6.11.1-cp311-cp311-android_aarch64.whl
pyside6-android-deploy --dry-run --name ClassMate \
  --wheel-pyside pyside6-6.11.1-*.whl --wheel-shiboken shiboken6-6.11.1-*.whl
python tools/patch_buildozer.py   # 注入 RECORD_AUDIO 等權限 + requests/pyjnius 依賴
pyside6-android-deploy --name ClassMate \
  --wheel-pyside pyside6-6.11.1-*.whl --wheel-shiboken shiboken6-6.11.1-*.whl
```

產物：APK 位於專案目錄（buildozer bin_dir）；debug 模式為 .apk，release 為 .aab（需簽名）。

## 2. 需要的權限

打包後在 AndroidManifest 確認（`RECORD_AUDIO`、`INTERNET` 必須；OPPO 額外需懸浮窗/後台）：

```xml
<uses-permission android:name="android.permission.RECORD_AUDIO"/>
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
<uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW"/>
<uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE"/>
<uses-permission android:name="android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS"/>
```

首次啟動 App 會請求麥克風權限；「顯示在其他應用上層」（懸浮窗）需引導用戶手動開啟（見 §4）。

## 3. OPPO / ColorOS 必做設定（關鍵！）

OPPO 對後台與彈窗管控嚴格，**逐項開啟**：

| 設定 | 路徑（ColorOS 13/14 約略位置） |
|---|---|
| 懸浮窗 | 設定 → 應用程式 → 應用程式管理 → ClassMate → **顯示在其他應用程式上層**：允許 |
| 自啟動 | 設定 → 應用程式 → 自啟動管理 → ClassMate：開啟 |
| 後台運行 | 設定 → 應用程式 → ClassMate → 電池 → **允許完全後台行為** |
| 電池優化 | 設定 → 電池 → 更多設定 → 優化電池使用 → ClassMate：**不允許優化** |
| 通知 | 設定 → 通知與狀態列 → ClassMate：允許（前台服務通知） |
| 鎖定任務 | 最近任務列表 → ClassMate 卡片 → 右上 ⋮ → **鎖定**（防誤滑清除） |
| 隱私→麥克風 | 設定 → 隱私權 → 權限管理 → 麥克風 → ClassMate：僅使用時允許（或一律允許） |

## 4. 語音辨識語言

`classmate/recognizer/android_recognizer.py` 已按設定映射：
- 粵語 → `yue-HK`（Google 語音服務需可用；若無可改用 zh-HK）
- 普通話 → `zh-CN`
- 英語 → `en-US`

OPPO 原生輸入法/Google App 的離線語言包可在「設定 → Google → 語言」下載離線辨識包。

## 5. 課堂使用建議

1. 入座後把手機放在桌上（收音距離 < 1.5 米效果最佳）。
2. 先選好科目（例如：感染控制），熱詞命中率更高。
3. 老師語速快或環境嘈雜 → 靈敏度調「敏銳」；怕誤觸發 → 「溫柔」。
4. 點名提醒請先在「設定」填好你的中文名/英文名/粵語叫法。
5. 答案以課本為準——本 App 是輔助，臨床決策請核對教材與指引。
