# 安卓（OPPO / ColorOS）部署與後台運行指南

## 1. 打包 APK

前置：Python 3.10+、JDK 17、Android SDK（build-tools / platform-tools）、androiddeployqt 所需環境。

```bash
cd classmate
pip install pyside6-android-deploy
pyside6-android-deploy --name ClassMate \
  --org "edu.kwnc.classmate" --version 1.0.0 \
  --requirements "requests>=2.28" \
  --extra-ignore-dirs "tests,docs,tools,models" \
  run.py
```

產物：`pyside6_android_deploy/ClassMate/build/outputs/apk/debug/*.apk`。
Release 版請先 `--release` 並配置簽名（keytool + apksigner）。

> 注意：pyside6-android-deploy 需在 **Linux** 上執行（WSL2 Ubuntu 亦可）。
> 若使用 jnius 原生語音，確認 `requirements` 包含 `pyjnius`。

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
