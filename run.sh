#!/bin/bash
# Whisper GUI 啟動腳本（處理 tcl-tk 依賴問題）

# 進入專案目錄
cd "$(dirname "$0")"

# 啟動虛擬環境（支援 venv 和 .venv）
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "錯誤：找不到虛擬環境"
    exit 1
fi

# 嘗試設定 tcl-tk 路徑（如果已安裝）
if command -v brew &> /dev/null; then
    TCLTK_PATH=$(brew --prefix tcl-tk 2>/dev/null)
    if [ -n "$TCLTK_PATH" ] && [ -d "$TCLTK_PATH/lib" ]; then
        export DYLD_LIBRARY_PATH="$TCLTK_PATH/lib:$DYLD_LIBRARY_PATH"
        echo "✓ 已設定 tcl-tk 路徑: $TCLTK_PATH"
    fi
fi

# 啟動應用程式
echo "正在啟動 Whisper GUI..."
python main.py

