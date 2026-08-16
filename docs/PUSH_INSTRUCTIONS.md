# 推送 ClassMate 到 GitHub 並觸發雲端打包（約 10 分鐘）

## 1. 建立 GitHub 帳號＋倉庫
1. 瀏覽器開 https://github.com → 註冊免費帳號（或用 Google 登入）
2. 右上 **+** → **New repository**
3. 名稱：`classmate`
4. **不要勾選** Add README / .gitignore / license（保持空白倉庫，避免衝突）
5. 按 **Create repository**

## 2. 本機推送（PowerShell，把「你的帳號」換成用戶名）
```powershell
cd E:\AI\classmate
git remote add origin https://github.com/你的帳號/classmate.git
git push -u origin main
```

第一次會自動彈出瀏覽器視窗登入 GitHub 授權（Git Credential Manager）。
若沒彈窗，改用**個人存取權杖**：
- GitHub → 右上頭像 → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
- 勾選 `repo` 權限 → 複製 token
- 推送時密碼欄貼上 token 即可（不會顯示）

## 3. 觸發雲端打包
推送成功後 **自動觸發**（不需手動）。查看進度：
- GitHub 倉庫頁 → **Actions** 分頁 → 左側 **Build ClassMate APK** → 點進最新一次運行
- 首次約 **30–60 分鐘**（下載 NDK/SDK 約 2GB＋編譯）
- 9 個步驟全部綠色勾 = 成功；紅色 ✕ = 失敗（把錯誤訊息截圖給我，我修）

## 4. 下載 APK
- 運行頁最底部 → **Artifacts** → 下載 `classmate-apk.zip`
- 解壓縮得 `ClassMate.apk`（約 100–150MB）

## 5. 安裝到 OPPO 手機
照 `docs/INSTALL_PHONE.md`：
1. 微信/QQ 檔案助手或 USB 傳 `ClassMate.apk` 到手
2. 文件管理點開 → 允許「安裝未知來源應用」→ 安裝
3. 授權：麥克風＋通知＋懸浮窗
4. OPPO 設定：自啟動＋允許完全後台行為＋電池不設限制（`android/README_OPPO_GUIDE.md` 有逐項路徑）
5. 開啟 App → 設定填名字 → 選科目 → 開始聆聽

## 常見問題
| 狀況 | 處理 |
|---|---|
| push 報 remote origin already exists | 上一步執行過 → 直接 `git push -u origin main` |
| push 被拒（non-fast-forward） | 倉庫非空白 → `git pull --rebase origin main` 後再 push |
| Actions 找不到工作流 | 確認 push 成功後等 10 秒，Actions 分頁刷新；或手動 Run workflow |
| 打包失敗 | 把 Actions 紅色步驟的日誌貼給我，我修好你再 Re-run |
