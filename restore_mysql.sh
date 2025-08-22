#!/bin/bash

# MySQL 資料恢復腳本
# 用途：從備份目錄恢復 MySQL 資料
# 作者：Claude Code
# 版本：1.0

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日誌函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 顯示使用說明
show_usage() {
    echo "用法: $0 [備份日期]"
    echo ""
    echo "參數："
    echo "  備份日期    可選，格式如：20250822 或 20250821_163430"
    echo "               如果不提供，將顯示可用的備份並讓您選擇"
    echo ""
    echo "範例："
    echo "  $0                      # 交互式選擇備份"
    echo "  $0 20250822            # 恢復到 2025-08-22 的備份"
    echo "  $0 20250821_163430     # 恢復到 2025-08-21 16:34:30 的備份"
    echo ""
}

# 檢查 Docker Compose 是否可用
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose 未安裝或不在 PATH 中"
        exit 1
    fi
    
    if [ ! -f "docker-compose.yml" ]; then
        log_error "當前目錄中找不到 docker-compose.yml 文件"
        exit 1
    fi
}

# 列出可用的備份
list_backups() {
    local backup_dir="docker_env/mysql"
    local backups=()
    
    log_info "掃描可用的備份..."
    
    # 掃描所有以 data_backup_ 開頭的目錄
    while IFS= read -r -d '' dir; do
        if [ -d "$dir" ]; then
            local backup_name=$(basename "$dir" | sed 's/data_backup_//')
            backups+=("$backup_name")
        fi
    done < <(find "${backup_dir}" -maxdepth 1 -name "data_backup_*" -type d -print0 2>/dev/null)
    
    if [ ${#backups[@]} -eq 0 ]; then
        log_error "找不到任何備份目錄"
        log_info "備份目錄應該位於 ${backup_dir}/data_backup_*"
        log_info "當前目錄內容："
        ls -la "${backup_dir}/" | grep -E "(data_backup_|^total)" || log_info "  目錄為空或無權限存取"
        exit 1
    fi
    
    # 按日期排序（新的在前）
    IFS=$'\n' backups=($(sort -r <<< "${backups[*]}"))
    unset IFS
    
    echo "${backups[@]}"
}

# 交互式選擇備份
select_backup() {
    local backups=($(list_backups))
    
    log_info "可用的備份："
    for i in "${!backups[@]}"; do
        local backup_path="docker_env/mysql/data_backup_${backups[$i]}"
        local backup_date="${backups[$i]}"
        local backup_type="一般備份"
        
        # 判斷備份類型
        if [[ $backup_date == before_restore_* ]]; then
            backup_type="恢復前備份"
        elif [[ $backup_date == *_test ]]; then
            backup_type="測試備份"
        fi
        
        # 嘗試解析日期格式
        if [[ $backup_date =~ ^([0-9]{4})([0-9]{2})([0-9]{2})(_([0-9]{2})([0-9]{2})([0-9]{2}))?$ ]]; then
            local year=${BASH_REMATCH[1]}
            local month=${BASH_REMATCH[2]}
            local day=${BASH_REMATCH[3]}
            local hour=${BASH_REMATCH[5]:-"00"}
            local minute=${BASH_REMATCH[6]:-"00"}
            local second=${BASH_REMATCH[7]:-"00"}
            local formatted_date="${year}-${month}-${day} ${hour}:${minute}:${second}"
        else
            local formatted_date="$backup_date"
        fi
        
        echo "  $((i+1)). $backup_date (${backup_type})"
        echo "     時間: $formatted_date"
        if [ -d "$backup_path" ]; then
            local size=$(du -sh "$backup_path" 2>/dev/null | cut -f1 || echo "未知")
            echo "     大小: $size"
        fi
        echo ""
    done
    
    echo ""
    read -p "請選擇要恢復的備份 (1-${#backups[@]}): " choice
    
    if [[ ! "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt ${#backups[@]} ]; then
        log_error "無效的選擇"
        exit 1
    fi
    
    echo "${backups[$((choice-1))]}"
}

# 驗證備份目錄
validate_backup() {
    local backup_date="$1"
    local backup_path="docker_env/mysql/data_backup_${backup_date}"
    
    if [ ! -d "$backup_path" ]; then
        log_error "備份目錄不存在: $backup_path"
        log_info "可用的備份："
        local available_backups=($(list_backups))
        for backup in "${available_backups[@]}"; do
            echo "  - $backup"
        done
        exit 1
    fi
    
    # 檢查備份目錄是否包含必要的 MySQL 文件
    if [ ! -f "$backup_path/ibdata1" ] && [ ! -d "$backup_path/mysql" ]; then
        log_warning "備份目錄似乎不包含有效的 MySQL 資料文件"
        log_warning "路徑: $backup_path"
        read -p "是否繼續? (y/N): " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            log_info "操作已取消"
            exit 1
        fi
    fi
    
    echo "$backup_path"
}

# 停止 MySQL 容器
stop_mysql() {
    log_info "停止 MySQL 容器..."
    
    if docker-compose ps mysql | grep -q "Up"; then
        docker-compose stop mysql
        log_success "MySQL 容器已停止"
    else
        log_info "MySQL 容器已經停止"
    fi
    
    # 等待容器完全停止
    sleep 2
}

# 備份當前資料
backup_current_data() {
    local current_backup_path="docker_env/mysql/data_backup_before_restore_$(date +%Y%m%d_%H%M%S)"
    
    log_info "備份當前資料到: $current_backup_path"
    
    if [ -d "docker_env/mysql/data" ] && [ "$(ls -A docker_env/mysql/data 2>/dev/null)" ]; then
        # 使用 sudo 進行備份以避免權限問題
        if command -v sudo &> /dev/null; then
            sudo cp -r docker_env/mysql/data "$current_backup_path"
            log_success "當前資料已備份到: $current_backup_path"
        else
            log_warning "無法使用 sudo，嘗試直接複製..."
            if cp -r docker_env/mysql/data "$current_backup_path" 2>/dev/null; then
                log_success "當前資料已備份到: $current_backup_path"
            else
                log_warning "備份當前資料失敗（權限問題），但將繼續恢復流程"
                log_warning "建議在恢復前手動備份重要資料"
            fi
        fi
    else
        log_info "當前資料目錄為空，跳過備份"
    fi
}

# 恢復資料
restore_data() {
    local backup_path="$1"
    local data_path="docker_env/mysql/data"
    
    log_info "清除當前資料目錄..."
    if [ -d "$data_path" ]; then
        # 使用 sudo 清除資料以避免權限問題
        if command -v sudo &> /dev/null; then
            sudo rm -rf "$data_path"/*
        else
            rm -rf "$data_path"/*
        fi
        log_success "當前資料目錄已清除"
    fi
    
    log_info "從備份恢復資料..."
    log_info "來源: $backup_path"
    log_info "目標: $data_path"
    
    # 確保目標目錄存在
    mkdir -p "$data_path"
    
    # 複製資料
    cp -r "$backup_path"/* "$data_path"/
    log_success "資料恢復完成"
    
    # 設置權限 (MySQL 容器使用 uid:gid 999:999)
    log_info "設置資料目錄權限..."
    if command -v sudo &> /dev/null; then
        sudo chown -R 999:999 "$data_path"
        sudo chmod -R 755 "$data_path"
    else
        log_warning "無法使用 sudo，跳過權限設置"
        log_warning "如果 MySQL 啟動失敗，請手動執行: sudo chown -R 999:999 $data_path"
    fi
    log_success "權限設置完成"
}

# 啟動 MySQL 容器
start_mysql() {
    log_info "重新啟動 MySQL 容器..."
    docker-compose up -d mysql
    
    # 等待容器啟動
    log_info "等待 MySQL 容器啟動..."
    local timeout=60
    local count=0
    
    while [ $count -lt $timeout ]; do
        if docker-compose ps mysql | grep -q "Up"; then
            log_success "MySQL 容器已啟動"
            return 0
        fi
        sleep 1
        count=$((count + 1))
        echo -n "."
    done
    
    echo ""
    log_warning "MySQL 容器啟動超時，請檢查容器狀態"
    log_info "您可以執行以下命令檢查："
    log_info "  docker-compose ps mysql"
    log_info "  docker-compose logs mysql"
}

# 驗證恢復結果
verify_restore() {
    log_info "驗證恢復結果..."
    
    # 檢查容器狀態
    if docker-compose ps mysql | grep -q "Up"; then
        log_success "MySQL 容器運行正常"
        
        # 嘗試連接 MySQL
        log_info "測試 MySQL 連接..."
        if docker-compose exec -T mysql mysqladmin ping -h localhost --silent 2>/dev/null; then
            log_success "MySQL 服務響應正常"
        else
            log_warning "MySQL 服務可能尚未完全啟動，請稍後再試"
        fi
    else
        log_error "MySQL 容器未正常運行"
        log_info "請檢查容器日誌: docker-compose logs mysql"
        return 1
    fi
}

# 主程序
main() {
    # 檢查參數
    if [ "$1" = "-h" ] || [ "$1" = "--help" ] || [ "$1" = "-help" ]; then
        show_usage
        exit 0
    fi
    
    log_info "MySQL 資料恢復腳本啟動"
    log_info "當前目錄: $(pwd)"
    
    # 檢查環境
    check_docker_compose
    
    # 確定備份日期
    local backup_date="$1"
    if [ -z "$backup_date" ]; then
        backup_date=$(select_backup)
    fi
    
    # 驗證備份
    local backup_path=$(validate_backup "$backup_date")
    
    # 顯示恢復信息
    log_info "準備恢復資料："
    log_info "  備份路徑: $backup_path"
    log_info "  目標路徑: docker_env/mysql/data"
    
    # 最終確認
    echo ""
    log_warning "此操作將："
    log_warning "  1. 停止當前的 MySQL 容器"
    log_warning "  2. 備份當前資料 (data_backup_before_restore_*)"
    log_warning "  3. 清除當前 MySQL 資料目錄"
    log_warning "  4. 從備份恢復資料"
    log_warning "  5. 重新啟動 MySQL 容器"
    echo ""
    read -p "確定要繼續嗎? (y/N): " confirm
    
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        log_info "操作已取消"
        exit 0
    fi
    
    # 執行恢復流程
    echo ""
    log_info "開始恢復流程..."
    
    stop_mysql
    backup_current_data
    restore_data "$backup_path"
    start_mysql
    
    # 等待一段時間讓 MySQL 完全啟動
    sleep 5
    verify_restore
    
    echo ""
    log_success "MySQL 資料恢復完成！"
    log_info "建議操作："
    log_info "  1. 檢查容器狀態: docker-compose ps"
    log_info "  2. 檢查 MySQL 日誌: docker-compose logs mysql"
    log_info "  3. 連接測試: docker-compose exec mysql mysql -u root -p"
    
    # 檢查是否需要重新初始化應用
    echo ""
    log_info "如果需要重新初始化應用資料，請執行："
    log_info "  docker-compose exec kinit-api python3 main.py init"
}

# 錯誤處理
trap 'log_error "腳本執行過程中發生錯誤，請檢查上述輸出"; exit 1' ERR

# 執行主程序
main "$@"