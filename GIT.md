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
git remote set-url origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/sprigga/kinit-pratice.git
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
git remote set-url origin https://USERNAME:TOKEN@github.com/sprigga/kinit-pratice.git

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
git remote set-url origin https://USERNAME:TOKEN@github.com/sprigga/kinit-pratice.git

# 6. 推送功能分支
git push origin backup-20250819
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

**最後更新：** 2025-08-20  
**維護者：** 專案開發團隊