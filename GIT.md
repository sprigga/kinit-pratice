# Git 專案上傳問題與解決方案

## 📋 目錄
- [常見問題](#常見問題)
- [解決方案](#解決方案)
- [推送方法](#推送方法)
- [最佳實踐](#最佳實踐)

## 🚨 常見問題

### 1. 資料庫文件權限問題
**問題描述：**
```bash
error: open("docker_env/mongo/data/WiredTiger.turtle"): Permission denied
error: unable to index file 'docker_env/mongo/data/WiredTiger.turtle'
fatal: updating files failed
```

**原因：**
- Docker 容器運行時產生的資料庫文件具有特殊權限
- MySQL、MongoDB 等資料庫文件不應被 Git 追蹤
- 這些文件會頻繁變動且體積龐大

### 2. GitHub 認證問題
**問題描述：**
```bash
fatal: could not read Username for 'https://github.com': No such device or address
```

**原因：**
- 缺少 GitHub 認證憑證
- 需要 Personal Access Token 或 SSH Key

### 3. Git 狀態混亂
**問題描述：**
- 大量資料庫文件被標記為已修改
- 無法正常提交和推送

### 4. 推送被拒絕 (non-fast-forward)
**問題描述：**
```bash
! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to 'https://github.com/username/repo.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. If you want to integrate the remote changes,
hint: use 'git pull' before pushing again.
```

**原因：**
- 遠程倉庫有新的提交，本地分支落後於遠程分支
- 本地有未提交的更改與遠程更新產生分歧
- Git 無法執行快進合併 (fast-forward merge)

## 🔧 解決方案

### 步驟 1：更新 .gitignore 文件

在 `.gitignore` 文件中添加以下內容：

```gitignore
# Docker 資料庫文件
docker_env/mysql/data/
docker_env/mongo/data/
docker_env/redis/data/
docker_env/data/

# 臨時文件
*.tmp
*.log

# 其他常見排除項目
node_modules/
__pycache__/
*.pyc
.env.local
.DS_Store
```

### 步驟 2：清理 Git 追蹤

```bash
# 從 Git 追蹤中移除資料庫文件
git rm --cached -r docker_env/mysql/data/ docker_env/mongo/data/ 2>/dev/null || true

# 檢查狀態
git status --porcelain
```

### 步驟 3：提交變更

```bash
# 添加所有變更
git add .

# 提交變更
git commit -m "Update .gitignore to exclude database files and add new project files"
```

### 步驟 4：處理分支分歧問題

當遇到推送被拒絕 (non-fast-forward) 錯誤時：

#### 方法一：使用 Rebase (推薦，保持線性歷史)

```bash
# 1. 檢查當前狀態
git status
git log --oneline -5

# 2. 獲取遠程更新
git fetch origin

# 3. 查看遠程分支狀態
git log origin/main --oneline -3

# 4. 提交本地更改
git add .
git commit -m "feat: add important local changes"

# 5. 暫存其他未提交更改
git stash push -m "Work in progress: temporary changes"

# 6. 使用 rebase 同步遠程更新
git pull --rebase origin main

# 7. 解決合併衝突（如有）
# 編輯衝突文件，然後：
git add <conflicted_files>
git rebase --continue

# 8. 恢復暫存的更改（如需要）
git stash pop

# 9. 推送到遠程
git push origin main
```

#### 方法二：使用 Merge (創建合併提交)

```bash
# 1. 檢查狀態並提交本地更改
git status
git add .
git commit -m "feat: local changes before merge"

# 2. 拉取並合併遠程更改
git pull origin main

# 3. 解決合併衝突（如有）
# 編輯衝突文件，然後：
git add <conflicted_files>
git commit -m "merge: resolve conflicts with remote changes"

# 4. 推送合併結果
git push origin main
```

#### 方法三：強制推送 (謹慎使用)

```bash
# ⚠️ 警告：這會覆蓋遠程更改，僅在確定本地版本正確時使用
git push origin main --force-with-lease
```

## 🔄 分支 Merge 到 Main 主幹流程

### 完整 Merge 操作步驟

```bash
# 1. 檢查當前狀態和分支
git status
git branch -a
git log --oneline -5

# 2. 提交當前分支的所有變更
git add .
git commit -m "docs: add Git troubleshooting and merge guide"

# 3. 切換到 main 分支
git checkout main

# 4. 拉取最新的 main 分支變更
git pull origin main

# 5. 合併功能分支到 main
git merge backup-20250819

# 6. 檢查合併結果
git log --oneline -5

# 7. 推送到遠端倉庫
git push origin main
```

### Merge 類型說明

#### Fast-forward Merge (快進合併)
```bash
# 當 main 分支沒有新提交時，Git 會執行快進合併
git merge feature-branch
# 輸出：Fast-forward
```

#### Three-way Merge (三方合併)
```bash
# 當 main 分支有新提交時，Git 會創建合併提交
git merge feature-branch
# 會打開編輯器讓你輸入合併提交訊息
```

#### 解決合併衝突
```bash
# 如果有衝突，Git 會暫停合併
git status  # 查看衝突文件
# 手動編輯衝突文件，解決衝突
git add .   # 標記衝突已解決
git commit  # 完成合併
```

## 🚀 推送方法

### 方法一：使用 Personal Access Token (推薦)

1. **創建 Personal Access Token：**
   - 前往 GitHub Settings > Developer settings > Personal access tokens
   - 點擊 "Generate new token"
   - 選擇適當的權限範圍（至少需要 `repo` 權限）
   - 複製生成的 token

2. **設定遠端 URL：**
```bash
git remote set-url origin https://[USERNAME]:[TOKEN]@github.com/sprigga/kinit-pratice.git
# 替換 [USERNAME] 為你的 GitHub 用戶名
# 替換 [TOKEN] 為你的 Personal Access Token
```

3. **推送分支：**
```bash
git push origin backup-20250819
```

### 方法二：使用 SSH Key

1. **生成 SSH Key（如果沒有）：**
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. **添加 SSH Key 到 GitHub：**
```bash
# 複製公鑰
cat ~/.ssh/id_ed25519.pub
# 將內容貼到 GitHub Settings > SSH and GPG keys
```

3. **設定 SSH 遠端：**
```bash
git remote set-url origin git@github.com:sprigga/kinit-pratice.git
```

4. **推送分支：**
```bash
git push origin backup-20250819
```

### 方法三：使用 GitHub CLI

```bash
# 安裝 GitHub CLI (如果尚未安裝)
# Ubuntu/Debian: apt install gh
# macOS: brew install gh
# Windows: winget install GitHub.cli

# 登入
gh auth login

# 推送
git push origin backup-20250819
```

### 方法四：手動認證

```bash
# 直接推送，系統會提示輸入認證
git push origin backup-20250819
# 輸入 GitHub 用戶名和 Personal Access Token
```

## 📝 完整操作流程

### 方案一：分支開發後 Merge 到 Main（推薦）

```bash
# 1. 檢查當前狀態
git status
git remote -v
git branch -a

# 2. 在功能分支上完成開發
git add .
git commit -m "feat: complete feature development"

# 3. 切換到 main 分支
git checkout main

# 4. 拉取最新變更
git pull origin main

# 5. 合併功能分支
git merge backup-20250819

# 6. 設定認證（選擇一種方法）
git remote set-url origin https://[USERNAME]:[TOKEN]@github.com/sprigga/kinit-pratice.git

# 7. 推送到 main
git push origin main

# 8. 清理本地分支（可選）
git branch -d backup-20250819
git push origin --delete backup-20250819
```

### 方案二：直接推送功能分支

```bash
# 1. 檢查當前狀態
git status
git remote -v
git branch

# 2. 更新 .gitignore
echo "docker_env/mysql/data/" >> .gitignore
echo "docker_env/mongo/data/" >> .gitignore
echo "docker_env/redis/data/" >> .gitignore

# 3. 清理追蹤
git rm --cached -r docker_env/mysql/data/ docker_env/mongo/data/ 2>/dev/null || true

# 4. 提交變更
git add .
git commit -m "Clean up database files and update gitignore"

# 5. 設定認證（選擇一種方法）
git remote set-url origin https://[USERNAME]:[TOKEN]@github.com/sprigga/kinit-pratice.git

# 6. 推送功能分支
git push origin backup-20250819
```

### 方案三：直接推送至主幹（使用 GitHub CLI 認證）

```bash
# 1. 檢查 GitHub CLI 認證狀態
gh auth status

# 2. 如果未登入，執行登入
gh auth login

# 3. 檢查當前狀態
git status
git branch -a

# 4. 確保在正確的分支上並提交所有變更
git add .
git commit -m "feat: complete all changes"

# 5. 切換到 main 分支（如果不在 main 上）
git checkout main

# 6. 拉取最新的 main 分支變更
git pull origin main

# 7. 合併功能分支到 main（如果需要）
git merge feature-branch-name

# 8. 設定遠端 URL 為 HTTPS
git remote set-url origin https://github.com/sprigga/kinit-pratice.git

# 9. 直接推送到 main 主幹
git push origin main

# 10. 驗證推送結果
git status
git log --oneline -5
```

#### 方案三的優勢
- ✅ 使用 GitHub CLI 自動處理認證
- ✅ 無需手動管理 Personal Access Token
- ✅ 支援雙因素認證 (2FA)
- ✅ 安全性更高，Token 自動管理
- ✅ 一次性設定，長期使用

#### GitHub CLI 認證設定
```bash
# 安裝 GitHub CLI（如果尚未安裝）
# Ubuntu/Debian
sudo apt install gh

# macOS
brew install gh

# Windows
winget install GitHub.cli

# 登入 GitHub
gh auth login
# 選擇：GitHub.com
# 選擇：HTTPS
# 選擇：Login with a web browser
# 按照提示完成認證

# 驗證登入狀態
gh auth status
```

## 🎯 最佳實踐

### 1. .gitignore 設定原則
- **排除敏感資料：** 密碼、API Key、證書文件
- **排除生成文件：** 編譯結果、日誌文件、快取
- **排除大型文件：** 資料庫文件、媒體文件
- **排除環境特定文件：** IDE 設定、OS 特定文件

### 2. 分支管理策略
```bash
# 創建功能分支
git checkout -b feature/new-feature

# 定期同步主分支
git checkout main
git pull origin main
git checkout feature/new-feature
git merge main

# 推送功能分支
git push origin feature/new-feature
```

### 3. 提交訊息規範
```bash
# 好的提交訊息範例
git commit -m "feat: add user authentication system"
git commit -m "fix: resolve database connection timeout"
git commit -m "docs: update API documentation"
git commit -m "refactor: optimize database queries"
```

### 4. 安全性考量
- 使用 Personal Access Token 而非密碼
- 定期更新 Access Token
- 不要在代碼中硬編碼敏感資訊
- 使用環境變數管理配置

## 🔍 常用 Git 指令

### 查詢指令
```bash
# 查看遠端倉庫
git remote -v

# 查看分支
git branch -a

# 查看提交歷史
git log --oneline -10

# 查看文件狀態
git status --porcelain
```

### 分支操作
```bash
# 創建並切換分支
git checkout -b new-branch

# 切換分支
git checkout branch-name

# 刪除本地分支
git branch -d branch-name

# 刪除遠端分支
git push origin --delete branch-name
```

### 同步操作
```bash
# 拉取最新變更
git pull origin main

# 推送所有分支
git push origin --all

# 推送標籤
git push origin --tags
```

## 🔄 分支分歧問題完整處理流程

### 實際案例：推送被拒絕的完整解決過程

```bash
# 錯誤情況：
# ! [rejected]        main -> main (non-fast-forward)
# error: failed to push some refs to 'https://github.com/username/repo.git'

# 完整解決步驟：

# 1. 檢查當前狀態
git status
git log --oneline -5

# 2. 提交重要的本地更改
git add MYSQL.md  # 重要文檔更新
git commit -m "docs: add complete MySQL container backup and restore guide"

# 3. 暫存其他工作進度
git stash push -m "Work in progress: various config and build changes"

# 4. 獲取遠程更新並 rebase
git pull --rebase origin main

# 5. 解決合併衝突（如 .vscode/settings.json）
# 編輯衝突文件，合併雙方有用的設定：
# {
#   "editor.fontFamily": "'Google Sans Code', Consolas, 'Courier New', monospace",
#   "editor.fontSize": 16,
#   "terminal.integrated.profiles.linux": {
#     "bash": {
#       "path": "bash",
#       "args": ["-c", "echo 'alias...' >> ~/.bashrc && source ~/.bashrc && bash"]
#     }
#   },
#   "terminal.integrated.defaultProfile.linux": "bash"
# }

git add .vscode/settings.json
git rebase --continue

# 6. 提交其他重要文件
git add .vscode/ api/alembic/versions_dev/ web/dist-pro/
git commit -m "update: Add VSCode settings, frontend build outputs, and database migration files"

# 7. 清理複雜的 stash 衝突（如果需要）
git stash drop  # 放棄有問題的 stash

# 8. 成功推送
git push origin main
```

### 分歧處理策略選擇

| 策略 | 適用場景 | 優點 | 缺點 |
|------|----------|------|------|
| **Rebase** | 保持乾淨的線性歷史 | ✅ 歷史清晰<br>✅ 無合併提交 | ❌ 需要解決衝突<br>❌ 改寫歷史 |
| **Merge** | 保留完整的分支歷史 | ✅ 保持原始歷史<br>✅ 處理簡單 | ❌ 產生合併提交<br>❌ 歷史複雜 |
| **Force Push** | 確定本地版本正確 | ✅ 直接覆蓋 | ⚠️ 可能丟失遠程更改 |

### 衝突解決最佳實踐

#### 1. 配置文件衝突
```bash
# 示例：VSCode settings.json 衝突
# <<<<<<< HEAD (遠程版本)
# {
#   "editor.fontFamily": "...",
#   "editor.fontSize": 16
# }
# =======
# {  
#   "terminal.integrated.profiles.linux": {...}
# }
# >>>>>>> local (本地版本)

# 解決：合併雙方有用的設定
{
  "editor.fontFamily": "'Google Sans Code', Consolas, 'Courier New', monospace",
  "editor.fontSize": 16,
  "terminal.integrated.profiles.linux": {
    "bash": {
      "path": "bash",
      "args": ["-c", "echo 'gemini-flash() { gemini --model gemini-2.5-flash \"$@\"; }' >> ~/.bashrc && source ~/.bashrc && bash"]
    }
  },
  "terminal.integrated.defaultProfile.linux": "bash"
}
```

#### 2. 構建文件衝突
```bash
# 處理前端構建文件衝突
# 通常選擇最新的構建結果
git checkout --theirs web/dist-pro/
git add web/dist-pro/
```

#### 3. 大量文件衝突處理
```bash
# 當有太多衝突時，重置並重新整理
git reset --hard
git stash drop
git pull --rebase origin main
```

## 🔐 GitHub 密鑰安全性問題處理

### GitGuardian 檢測到敏感信息

當收到 GitGuardian 警告時，表示你的倉庫中可能包含敏感信息。

#### 常見敏感信息類型
- **Personal Access Token**: `ghp_xxxxxxxxxxxx`
- **SSH私鑰**: `-----BEGIN OPENSSH PRIVATE KEY-----`
- **API Keys**: 各種服務的API金鑰
- **密碼**: 明文密碼或配置文件中的密碼
- **資料庫連接字符串**: 包含用戶名密碼的連接字符串

#### 立即處理步驟

##### 1. 識別洩露來源
```bash
# 搜尋可能的敏感信息
git log --oneline -10
git show --name-only HEAD

# 搜尋特定模式
grep -r "ghp_\|ssh-rsa\|-----BEGIN" . --exclude-dir=.git
grep -r "token\|key\|password\|secret" . --include="*.md" --include="*.txt"
```

##### 2. 立即撤銷受影響的憑證
- **GitHub Token**: 前往 GitHub Settings > Developer settings > Personal access tokens，立即刪除洩露的token
- **SSH Key**: 如果SSH私鑰洩露，立即生成新的密鑰對
- **API Keys**: 到相關服務提供商處撤銷並重新生成

##### 3. 從歷史記錄中清除敏感信息

**方法一：修改最近的提交**
```bash
# 如果敏感信息在最新提交中
git reset --soft HEAD~1
# 編輯文件，移除敏感信息
git add .
git commit -m "fix: remove sensitive information"
git push origin main --force-with-lease
```

**方法二：使用 BFG Repo-Cleaner（推薦）**
```bash
# 安裝 BFG Repo-Cleaner
# Ubuntu: sudo apt install bfg
# macOS: brew install bfg

# 創建敏感信息清單文件
echo "YOUR_SECRET_TOKEN" > secrets.txt
echo "ghp_xxxxxxxxxxxx" >> secrets.txt

# 清理歷史記錄
bfg --replace-text secrets.txt .git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 強制推送清理後的歷史
git push origin --force --all
```

**方法三：使用 git filter-branch**
```bash
# 從所有歷史記錄中移除特定文件
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/sensitive/file' \
  --prune-empty --tag-name-filter cat -- --all

# 清理並強制推送
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin --force --all
```

##### 4. 更新 .gitignore 防止未來洩露
```bash
# 添加敏感文件模式到 .gitignore
cat >> .gitignore << EOF

# 安全性 - 排除敏感文件
*.pem
*.key
*.p12
*.pfx
.env
.env.local
.env.production
secrets.txt
config/secrets.yml

# GitHub 相關
.github/workflows/secrets.yml
```

### 最佳實踐：防止敏感信息洩露

#### 1. 使用環境變數
```bash
# 不要在代碼中硬編碼
# ❌ 錯誤做法
TOKEN = "ghp_xxxxxxxxxxxx"

# ✅ 正確做法
import os
TOKEN = os.getenv('GITHUB_TOKEN')
```

#### 2. 配置 pre-commit hook
```bash
# 創建 .git/hooks/pre-commit
#!/bin/bash
if git diff --cached --name-only | xargs grep -l "ghp_\|ssh-rsa\|-----BEGIN"; then
    echo "❌ 檢測到敏感信息，提交被阻止"
    exit 1
fi
```

#### 3. 使用 git-secrets 工具
```bash
# 安裝 git-secrets
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets && make install

# 在專案中啟用
git secrets --install
git secrets --register-aws
git secrets --add 'ghp_[0-9A-Za-z]{36}'
```

#### 4. 定期審查
```bash
# 定期檢查敏感信息
git log --grep="password\|token\|key" --oneline
git log -S "secret" --oneline
```

### 緊急聯絡和報告

#### 如果洩露了重要憑證：
1. **立即撤銷所有相關憑證**
2. **檢查是否有異常活動**
3. **通知團隊成員**
4. **更新文檔和流程**

#### GitHub 進階安全功能
- 啟用 **Dependabot alerts**
- 啟用 **Secret scanning**
- 啟用 **Code scanning**
- 設定 **Branch protection rules**

## 🚨 緊急情況處理

### 撤銷最後一次提交
```bash
# 保留變更，撤銷提交
git reset --soft HEAD~1

# 完全撤銷提交和變更
git reset --hard HEAD~1
```

### 強制推送（謹慎使用）
```bash
# 強制推送當前分支
git push origin branch-name --force

# 更安全的強制推送
git push origin branch-name --force-with-lease
```

### 清理工作目錄
```bash
# 清理未追蹤的文件
git clean -fd

# 重置所有變更
git reset --hard HEAD
```

## 📚 參考資源

- [Git 官方文檔](https://git-scm.com/doc)
- [GitHub 文檔](https://docs.github.com/)
- [Git 最佳實踐](https://git-scm.com/book/en/v2)
- [GitHub Personal Access Token 設定](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

---

**最後更新：** 2025-08-22  
**維護者：** 專案開發團隊

## 📋 版本更新記錄

### 2025-08-22
- ✅ 新增分支分歧問題處理章節
- ✅ 新增推送被拒絕 (non-fast-forward) 問題的完整解決流程
- ✅ 新增 Rebase vs Merge 策略比較表格
- ✅ 新增衝突解決最佳實踐和實際案例
- ✅ 新增配置文件、構建文件衝突的具體處理方法

### 2025-08-20  
- ✅ 初始版本：基本Git問題排除指南
- ✅ 新增資料庫文件權限問題解決方案
- ✅ 新增GitHub認證設定方法
- ✅ 新增分支管理和推送方法