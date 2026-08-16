# 課堂智聽 ClassMate 🎧

為安卓手機設計的課堂聆聽助手（**OPPO / ColorOS 優先**，桌面版可完整測試）。
監聽粵語、英語、普通話授課內容；聽到**老師提問**即彈窗附 AI 答案；**點名叫你**時立即彈出警示＋簡潔答案。

## 功能

| 功能 | 說明 |
|---|---|
| 🎙 三語監聽 | 粵語 / 英語 / 普通話（Android 原生 SpeechRecognizer yue-HK / en-US / zh-CN） |
| 📚 科目與熱詞 | 預置**澳門鏡湖護理學院 護理學學士 大三全部課程**（10 必修 + 核心/選修，148 個課堂高頻熱詞），可自訂增刪 |
| 💡 提問彈窗 | 偵測到問題即彈出卡片：熱詞標籤＋AI 答案（打字機動畫），一鍵複製 |
| ⚠ 點名提醒 | 老師叫你名字 → 紅色警示彈窗＋**最近問題的簡潔答案**（先答為敬） |
| ✂️ 作答模式 | 「簡潔」／「深入研討」隨時切換；深入模式按 定義→機制→臨床→護理 分點 |
| 🧠 AI 接駁 | 預設**完全離線**（內建護理知識庫＋答題框架）；可接駁任何 OpenAI 相容 API |
| 🕘 歷史紀錄 | 自動存檔、搜尋、匯出 JSON、清空 |
| 🎚 靈敏度 | 0–100 三檔（溫柔/標準/敏銳）即時調節識別門檻 |
| 🔋 後台運行 | 桌面＝系統匣；安卓＝前台服務＋通知（OPPO 需授權，見下方指南） |

## 快速開始（桌面）

```bash
pip install -r requirements.txt
python run.py                 # 真實監聽（自動選擇 vosk → google → mock）
python run.py --demo          # 播放腳本化課堂演示（彈窗/點名全流程）
python tools/run_demo.py      # 離屏演示＋自動截圖到 docs/shots_demo
```

離線語音模型（可選，放在 `models/` 自動偵測）：
`vosk-model-small-cn-0.22`、`vosk-model-small-en-us-0.15`（alphacephei.com/vosk/models）。

## 測試

```bash
python -m pytest tests/unit tests/integration -q   # 44 個核心測試
python -m pytest tests/e2e -q                      # 離屏 UI 冒煙＋截圖
python tools/test_real_audio.py models/tts_yue.wav --engine vosk|google   # 真實音訊端對端
```

## 專案結構

```
classmate/
  run.py                  # 啟動器（桌面／安卓入口）
  classmate/              # Python 核心：辨識、偵測、作答、歷史、橋接
    recognizer/           # vosk(離線) / google(線上粵語) / android(原生) / mock(演示)
  data/                   # 大三課程＋熱詞知識庫（courses_a/b.json）
  qml/                    # QML 介面（主題 token、動效元件、四大頁面、彈窗）
  tests/                  # unit / integration / e2e
  android/                # 安卓打包與 OPPO 設定指南
  docs/                   # 測試報告、截圖
```

## 技術架構

- **Qt 6.11 / PySide6 + QML**：動感深色霓虹主題、Spring 動效（OutCubic/OutBack 緩動表）、
  typewriter 答案、脈衝環/聲波視覺化。
- **辨識抽象層**：Android→原生 SpeechRecognizer（jnius）；桌面→vosk 離線優先，Google zh-HK 兜底，
  mock 供演示/測試。
- **偵測核心**：多語言問題標記（點解/為什麼/why…）、名字稱呼模式、熱詞模糊匹配
  （SequenceMatcher 滑窗，閾值隨靈敏度滑動）、點名沿用最近問題緩衝。
- **作答引擎**：熱詞知識庫（簡潔/深入雙筆記）→ OpenAI 相容 API → 離線答題框架，永不空白。
- **歷史**：SQLite（WAL），完整增刪查與匯出。

## 安卓打包（概覽）

```bash
pip install pyside6-android-deploy
pyside6-android-deploy --name ClassMate --requirements "vosk==0.3.45,requests" run.py
```
詳細步驟、權限與 **OPPO/ColorOS 後台運行設定**見 [android/README_OPPO_GUIDE.md](android/README_OPPO_GUIDE.md)。
