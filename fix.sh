#!/bin/bash
# Whisper GUI 故障排除與修復腳本
# 整合了所有常見問題的修復方案

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "Whisper GUI 故障排除與修復腳本"
echo "============================================================"
echo ""

# 檢查是否在虛擬環境中
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        echo "啟動虛擬環境..."
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        echo "啟動虛擬環境..."
        source .venv/bin/activate
    else
        echo "⚠️  未找到虛擬環境，將使用系統 Python"
    fi
fi

# 顯示選單
echo "請選擇要修復的問題："
echo ""
echo "1. Tkinter 依賴問題（使用系統 Python 重建虛擬環境）"
echo "2. CoreMLTools macOS 版本兼容性問題"
echo "3. 安裝 python-dotenv（載入 .env 檔案需要）"
echo "4. 檢查配置（驗證路徑和 API Key）"
echo "5. 重新安裝所有依賴"
echo "6. 退出"
echo ""
read -p "請輸入選項 (1-6): " choice

case $choice in
    1)
        echo ""
        echo "============================================================"
        echo "修復 Tkinter 依賴問題"
        echo "============================================================"
        echo ""
        
        # 檢查系統 Python
        if /usr/bin/python3 -c "import tkinter" 2>/dev/null; then
            echo "✓ 系統 Python 有 tkinter 支援"
            SYSTEM_PYTHON="/usr/bin/python3"
        else
            echo "✗ 系統 Python 沒有 tkinter 支援"
            exit 1
        fi
        
        # 備份舊的虛擬環境
        if [ -d "venv" ]; then
            BACKUP_NAME="venv_backup_$(date +%Y%m%d_%H%M%S)"
            echo "備份舊的虛擬環境到: $BACKUP_NAME"
            mv venv "$BACKUP_NAME"
        fi
        
        # 建立新的虛擬環境
        echo "使用系統 Python 建立新的虛擬環境..."
        $SYSTEM_PYTHON -m venv venv
        
        # 啟動虛擬環境
        source venv/bin/activate
        
        # 升級 pip
        echo "升級 pip..."
        pip install --upgrade pip
        
        # 安裝依賴
        echo "安裝依賴..."
        pip install -r requirements.txt
        
        echo ""
        echo "✓ 完成！"
        echo ""
        echo "現在可以執行："
        echo "  source venv/bin/activate"
        echo "  python main.py"
        ;;
        
    2)
        echo ""
        echo "============================================================"
        echo "修復 CoreMLTools 兼容性問題"
        echo "============================================================"
        echo ""
        
        # 方案 1: 嘗試更新
        echo "方案 1: 嘗試更新 coremltools..."
        pip install --upgrade coremltools 2>&1 | tail -5
        
        # 測試是否可以導入
        echo ""
        echo "測試 coremltools 導入..."
        if python -c "import coremltools; print('✓ coremltools 可用')" 2>&1 | grep -q "可用"; then
            echo "✓ coremltools 更新成功！"
            exit 0
        fi
        
        # 方案 2: 卸載
        echo ""
        echo "方案 2: 卸載 coremltools（如果不需要 CoreML 功能）..."
        read -p "是否要卸載 coremltools？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pip uninstall -y coremltools
            echo "✓ coremltools 已卸載"
            echo ""
            echo "注意：CoreML 執行功能將無法使用，但 CPU 執行功能仍然可用"
        fi
        ;;
        
    3)
        echo ""
        echo "============================================================"
        echo "安裝 python-dotenv"
        echo "============================================================"
        echo ""
        
        pip install python-dotenv
        
        echo ""
        echo "✓ python-dotenv 已安裝"
        echo ""
        echo "現在可以載入 .env 檔案了"
        ;;
        
    4)
        echo ""
        echo "============================================================"
        echo "檢查配置"
        echo "============================================================"
        echo ""
        
        if [ -f "check_config.py" ]; then
            python check_config.py
        else
            echo "⚠️  check_config.py 不存在"
            echo "手動檢查："
            echo ""
            echo "1. 檢查 .env 檔案是否存在："
            ls -la .env 2>/dev/null || echo "  ✗ .env 檔案不存在"
            echo ""
            echo "2. 檢查 whisper.cpp 路徑："
            python -c "from config import config; print(f'  {config.WHISPER_CPP_PATH}'); import os; print(f'  存在: {os.path.exists(config.WHISPER_CPP_PATH)}')" 2>/dev/null || echo "  ✗ 無法讀取配置"
        fi
        ;;
        
    5)
        echo ""
        echo "============================================================"
        echo "重新安裝所有依賴"
        echo "============================================================"
        echo ""
        
        echo "升級 pip..."
        pip install --upgrade pip
        
        echo ""
        echo "重新安裝依賴..."
        pip install -r requirements.txt
        
        echo ""
        echo "✓ 完成！"
        ;;
        
    6)
        echo "退出"
        exit 0
        ;;
        
    *)
        echo "無效的選項"
        exit 1
        ;;
esac

echo ""
echo "============================================================"
echo "修復完成"
echo "============================================================"

