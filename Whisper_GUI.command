#!/bin/bash
# Whisper GUI 啟動腳本（雙擊執行版本）

# 獲取腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 檢查虛擬環境是否存在（支援 venv 和 .venv）
if [ -d "venv" ]; then
    VENV_DIR="venv"
elif [ -d ".venv" ]; then
    VENV_DIR=".venv"
else
    osascript -e 'display dialog "錯誤：找不到虛擬環境。\n\n請先執行：\n/usr/bin/python3 -m venv venv\nsource venv/bin/activate\npip install -r requirements.txt" buttons {"確定"} default button 1 with icon stop'
    exit 1
fi

# 啟動虛擬環境
source "$VENV_DIR/bin/activate"

# 檢查 Python 是否可用
if ! command -v python &> /dev/null; then
    osascript -e 'display dialog "錯誤：無法找到 Python。\n\n請確認虛擬環境已正確設定。" buttons {"確定"} default button 1 with icon stop'
    exit 1
fi

# 嘗試設定 tcl-tk 路徑（如果已安裝）
if command -v brew &> /dev/null; then
    TCLTK_PATH=$(brew --prefix tcl-tk 2>/dev/null)
    if [ -n "$TCLTK_PATH" ] && [ -d "$TCLTK_PATH/lib" ]; then
        export DYLD_LIBRARY_PATH="$TCLTK_PATH/lib:$DYLD_LIBRARY_PATH"
    fi
fi

# 啟動應用程式
python main.py

# 如果程式異常退出，顯示錯誤訊息
if [ $? -ne 0 ]; then
    osascript -e 'display dialog "應用程式異常退出。\n\n請檢查終端機的錯誤訊息。" buttons {"確定"} default button 1 with icon caution'
fi

